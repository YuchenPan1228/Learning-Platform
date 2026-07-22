from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.models.enums import (
    JobExecutionStage,
    JobExecutionStatus,
    TopicJobCreatedBy,
    TopicJobStatus,
)
from app.models.job_execution_log import JobExecutionLog
from app.models.topic import Topic
from app.models.topic_job import TopicJob
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage
from app.services.job_execution import (
    JobExecutionFinishInput,
    JobExecutionStartInput,
    complete_job_execution,
    fail_job_execution,
    start_job_execution,
    track_job_execution,
)


def test_start_job_execution_persists_running_log() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row
    started = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)

    result = start_job_execution(
        session,
        JobExecutionStartInput(
            topic_job_id=7,
            stage=JobExecutionStage.COLLECTING,
            source_url="https://example.com/notes",
            model=None,
            started_at=started,
        ),
    )

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    saved = session.add.call_args.args[0]
    assert isinstance(saved, JobExecutionLog)
    assert saved.topic_job_id == 7
    assert saved.stage is JobExecutionStage.COLLECTING
    assert saved.status is JobExecutionStatus.RUNNING
    assert saved.started_at == started
    assert saved.source_url == "https://example.com/notes"
    assert saved.finished_at is None
    assert saved.runtime_ms is None
    assert result is saved


def test_complete_job_execution_sets_runtime_and_usage_fields() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row
    session.get.return_value = MagicMock(
        model="qwen2.5:3b",
        input_tokens=11,
        output_tokens=22,
        estimated_cost_usd=Decimal("0"),
    )

    log = JobExecutionLog(
        topic_job_id=7,
        stage=JobExecutionStage.AI_EXTRACTION,
        status=JobExecutionStatus.RUNNING,
        started_at=datetime(2026, 7, 22, 12, 0, 0, tzinfo=UTC),
    )
    log.id = 3

    result = complete_job_execution(
        session,
        log,
        JobExecutionFinishInput(
            finished_at=datetime(2026, 7, 22, 12, 0, 1, 500000, tzinfo=UTC),
            ai_usage_log_id=99,
            source_url="https://example.com/pdf",
        ),
    )

    assert result.status is JobExecutionStatus.SUCCEEDED
    assert result.runtime_ms == 1500
    assert result.failure_reason is None
    assert result.source_url == "https://example.com/pdf"
    assert result.model == "qwen2.5:3b"
    assert result.input_tokens == 11
    assert result.output_tokens == 22
    assert result.estimated_cost_usd == Decimal("0")
    assert result.ai_usage_log_id == 99
    session.commit.assert_called_once()


def test_fail_job_execution_records_failure_reason() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row

    log = JobExecutionLog(
        topic_job_id=7,
        stage=JobExecutionStage.EXTRACTING,
        status=JobExecutionStatus.RUNNING,
        started_at=datetime(2026, 7, 22, 12, 0, 0, tzinfo=UTC),
        source_url="https://example.com/page",
    )
    log.id = 4

    result = fail_job_execution(
        session,
        log,
        failure_reason="timeout while fetching page",
        finish=JobExecutionFinishInput(
            finished_at=datetime(2026, 7, 22, 12, 0, 2, tzinfo=UTC),
        ),
    )

    assert result.status is JobExecutionStatus.FAILED
    assert result.failure_reason == "timeout while fetching page"
    assert result.runtime_ms == 2000
    assert result.source_url == "https://example.com/page"
    session.commit.assert_called_once()


def test_complete_rejects_non_running_log() -> None:
    session = MagicMock()
    log = JobExecutionLog(
        topic_job_id=7,
        stage=JobExecutionStage.PUBLISHING,
        status=JobExecutionStatus.SUCCEEDED,
        started_at=datetime(2026, 7, 22, 12, 0, 0, tzinfo=UTC),
    )
    log.id = 5

    with pytest.raises(ValueError, match="expected running"):
        complete_job_execution(session, log)


def test_track_job_execution_completes_on_success() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row

    tracked: JobExecutionLog
    with track_job_execution(
        session,
        JobExecutionStartInput(
            topic_job_id=7,
            stage=JobExecutionStage.POLICY_CHECK,
            started_at=datetime(2026, 7, 22, 12, 0, 0, tzinfo=UTC),
        ),
    ) as log:
        tracked = log
        assert log.status == JobExecutionStatus.RUNNING

    assert tracked.status == JobExecutionStatus.SUCCEEDED
    assert tracked.finished_at is not None
    assert tracked.runtime_ms is not None
    assert session.commit.call_count == 2


def test_track_job_execution_fails_on_exception() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row

    tracked: JobExecutionLog
    with (
        pytest.raises(RuntimeError, match="boom"),
        track_job_execution(
            session,
            JobExecutionStartInput(
                topic_job_id=7,
                stage=JobExecutionStage.DEDUPLICATION,
                started_at=datetime(2026, 7, 22, 12, 0, 0, tzinfo=UTC),
            ),
        ) as log,
    ):
        tracked = log
        raise RuntimeError("boom")

    assert tracked.status == JobExecutionStatus.FAILED
    assert tracked.failure_reason == "boom"
    assert session.commit.call_count == 2


@pytest.mark.integration
def test_job_execution_observability_writes_to_database(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory

    session = get_session_factory()()
    try:
        topic = Topic(slug="job-obs-topic", name="Job Observability Topic", order_index=0)
        session.add(topic)
        session.flush()

        topic_job = TopicJob(
            topic_id=topic.id,
            query="bayes theorem",
            target_source_count=2,
            status=TopicJobStatus.QUEUED,
            priority=0,
            created_by=TopicJobCreatedBy.ADMIN,
        )
        session.add(topic_job)
        session.commit()

        usage = record_ai_usage(
            session,
            AIUsageRecordInput(
                provider="ollama",
                model="qwen2.5:3b",
                input_tokens=5,
                output_tokens=9,
                latency_ms=80,
                cache_hit=False,
            ),
        )

        with track_job_execution(
            session,
            JobExecutionStartInput(
                topic_job_id=topic_job.id,
                stage=JobExecutionStage.AI_EXTRACTION,
                source_url="https://example.com/bayes",
            ),
        ) as log:
            complete_job_execution(
                session,
                log,
                JobExecutionFinishInput(
                    ai_usage_log_id=usage.id,
                    model="qwen2.5:3b",
                ),
            )

        session.refresh(log)
        assert log.status is JobExecutionStatus.SUCCEEDED
        assert log.started_at is not None
        assert log.finished_at is not None
        assert log.runtime_ms is not None
        assert log.runtime_ms >= 0
        assert log.source_url == "https://example.com/bayes"
        assert log.model == "qwen2.5:3b"
        assert log.input_tokens == 5
        assert log.output_tokens == 9
        assert log.estimated_cost_usd == Decimal("0")
        assert log.ai_usage_log_id == usage.id
        assert log.failure_reason is None
    finally:
        session.close()
