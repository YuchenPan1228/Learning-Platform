from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from app.models.concept import Concept
from app.models.enums import TopicJobCreatedBy, TopicJobStatus
from app.models.topic import Topic
from app.models.topic_job import TopicJob
from app.services.topic_job import (
    TopicJobCreateInput,
    TopicJobError,
    allowed_transitions,
    create_topic_job,
    is_terminal,
    list_topic_jobs,
    mark_collecting,
    mark_completed,
    mark_extracting,
    mark_failed,
    mark_reviewing,
    transition_topic_job,
)
from fastapi.testclient import TestClient


def _topic(*, topic_id: int = 10) -> Topic:
    return Topic(
        id=topic_id,
        slug="conditional-probability",
        name="Conditional Probability",
        order_index=0,
    )


def _job(
    *,
    job_id: int = 1,
    status: TopicJobStatus = TopicJobStatus.QUEUED,
    topic: Topic | None = None,
) -> TopicJob:
    now = datetime.now(UTC)
    resolved_topic = topic or _topic()
    job = TopicJob(
        topic_id=resolved_topic.id,
        concept_id=None,
        query="bayes theorem interview questions",
        target_source_count=5,
        status=status,
        priority=0,
        created_by=TopicJobCreatedBy.ADMIN,
    )
    job.id = job_id
    job.created_at = now
    job.updated_at = now
    job.topic = resolved_topic
    job.execution_logs = []
    return job


def test_allowed_transitions_cover_lifecycle() -> None:
    assert allowed_transitions(TopicJobStatus.QUEUED) == {
        TopicJobStatus.COLLECTING,
        TopicJobStatus.FAILED,
    }
    assert allowed_transitions(TopicJobStatus.COLLECTING) == {
        TopicJobStatus.EXTRACTING,
        TopicJobStatus.FAILED,
    }
    assert allowed_transitions(TopicJobStatus.EXTRACTING) == {
        TopicJobStatus.REVIEWING,
        TopicJobStatus.FAILED,
    }
    assert allowed_transitions(TopicJobStatus.REVIEWING) == {
        TopicJobStatus.COMPLETED,
        TopicJobStatus.FAILED,
    }
    assert allowed_transitions(TopicJobStatus.COMPLETED) == frozenset()
    assert allowed_transitions(TopicJobStatus.FAILED) == frozenset()
    assert is_terminal(TopicJobStatus.COMPLETED)
    assert is_terminal(TopicJobStatus.FAILED)
    assert not is_terminal(TopicJobStatus.QUEUED)


def test_create_topic_job_starts_queued() -> None:
    session = MagicMock()
    topic = _topic()
    session.get.return_value = topic
    persisted: dict[str, TopicJob] = {}

    def add(row: object) -> None:
        if isinstance(row, TopicJob):
            now = datetime.now(UTC)
            row.id = 42
            row.created_at = now
            row.updated_at = now
            row.topic = topic
            row.execution_logs = []
            persisted["job"] = row

    def scalar(_stmt: object) -> TopicJob:
        return persisted["job"]

    session.add.side_effect = add
    session.scalar.side_effect = scalar

    result = create_topic_job(
        session,
        TopicJobCreateInput(
            topic_id=10,
            query="  bayes  ",
            priority=1,
        ),
    )

    session.commit.assert_called()
    saved = persisted["job"]
    assert saved.status is TopicJobStatus.QUEUED
    assert saved.query == "bayes"
    assert saved.priority == 1
    assert result.id == 42
    assert result.status is TopicJobStatus.QUEUED
    assert result.query == "bayes"
    assert result.topic_slug == "conditional-probability"


def test_create_rejects_blank_query() -> None:
    session = MagicMock()
    with pytest.raises(TopicJobError, match="query must not be blank"):
        create_topic_job(session, TopicJobCreateInput(topic_id=1, query="   "))


def test_create_rejects_missing_topic() -> None:
    session = MagicMock()
    session.get.return_value = None
    with pytest.raises(TopicJobError, match="topic 99 not found"):
        create_topic_job(session, TopicJobCreateInput(topic_id=99, query="x"))


def test_create_rejects_concept_on_wrong_topic() -> None:
    session = MagicMock()
    topic = _topic(topic_id=10)
    concept = Concept(
        slug="greeks",
        name="Greeks",
        topic_id=99,
        definition="Option sensitivities",
    )
    concept.id = 3
    session.get.side_effect = [topic, concept]

    with pytest.raises(TopicJobError, match="does not belong"):
        create_topic_job(
            session,
            TopicJobCreateInput(topic_id=10, concept_id=3, query="delta"),
        )


def test_happy_path_lifecycle_transitions() -> None:
    session = MagicMock()
    job = _job(status=TopicJobStatus.QUEUED)
    session.scalar.return_value = job

    assert mark_collecting(session, 1).status is TopicJobStatus.COLLECTING
    assert job.status is TopicJobStatus.COLLECTING
    assert mark_extracting(session, 1).status is TopicJobStatus.EXTRACTING
    assert mark_reviewing(session, 1).status is TopicJobStatus.REVIEWING
    assert mark_completed(session, 1).status is TopicJobStatus.COMPLETED
    assert session.commit.call_count == 4


def test_can_fail_from_each_active_status() -> None:
    for start in (
        TopicJobStatus.QUEUED,
        TopicJobStatus.COLLECTING,
        TopicJobStatus.EXTRACTING,
        TopicJobStatus.REVIEWING,
    ):
        session = MagicMock()
        job = _job(status=start)
        session.scalar.return_value = job
        result = mark_failed(session, 1)
        assert result.status is TopicJobStatus.FAILED
        assert job.status is TopicJobStatus.FAILED


def test_rejects_invalid_and_terminal_transitions() -> None:
    session = MagicMock()
    job = _job(status=TopicJobStatus.QUEUED)
    session.scalar.return_value = job

    with pytest.raises(TopicJobError, match="cannot transition"):
        transition_topic_job(session, 1, TopicJobStatus.EXTRACTING)

    with pytest.raises(TopicJobError, match="cannot transition"):
        transition_topic_job(session, 1, TopicJobStatus.COMPLETED)

    job.status = TopicJobStatus.COMPLETED
    with pytest.raises(TopicJobError, match="cannot transition"):
        transition_topic_job(session, 1, TopicJobStatus.FAILED)

    job.status = TopicJobStatus.FAILED
    with pytest.raises(TopicJobError, match="cannot transition"):
        transition_topic_job(session, 1, TopicJobStatus.QUEUED)


def test_list_topic_jobs_filters_status() -> None:
    session = MagicMock()
    job = _job(status=TopicJobStatus.COLLECTING)
    result_proxy = MagicMock()
    result_proxy.unique.return_value.all.return_value = [job]
    session.scalars.return_value = result_proxy

    result = list_topic_jobs(session, status=TopicJobStatus.COLLECTING)
    assert len(result.items) == 1
    assert result.items[0].status is TopicJobStatus.COLLECTING
    assert result.items[0].topic_slug == "conditional-probability"


@pytest.mark.integration
def test_create_and_transition_api(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.topic import Topic as TopicModel

    session = get_session_factory()()
    try:
        topic = TopicModel(
            slug="topic-job-lifecycle",
            name="Topic Job Lifecycle",
            order_index=0,
        )
        session.add(topic)
        session.commit()
        topic_id = topic.id
    finally:
        session.close()

    create_resp = client.post(
        "/admin/ingestion/jobs",
        json={
            "topic_id": topic_id,
            "query": "conditional probability sources",
            "target_source_count": 3,
            "priority": 2,
        },
    )
    assert create_resp.status_code == 200, create_resp.text
    body = create_resp.json()
    assert body["status"] == "queued"
    assert body["query"] == "conditional probability sources"
    assert body["target_source_count"] == 3
    assert body["execution_logs"] == []
    job_id = body["id"]

    list_resp = client.get("/admin/ingestion/jobs", params={"status": "queued"})
    assert list_resp.status_code == 200
    assert any(item["id"] == job_id for item in list_resp.json()["items"])

    for status in ("collecting", "extracting", "reviewing", "completed"):
        resp = client.post(
            f"/admin/ingestion/jobs/{job_id}/status",
            json={"status": status},
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["status"] == status

    bad = client.post(
        f"/admin/ingestion/jobs/{job_id}/status",
        json={"status": "failed"},
    )
    assert bad.status_code == 400
    assert "cannot transition" in bad.json()["detail"]

    missing = client.get("/admin/ingestion/jobs/999999")
    assert missing.status_code == 404


@pytest.mark.integration
def test_fail_from_collecting_via_api(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    from app.db import get_session_factory
    from app.models.topic import Topic as TopicModel

    session = get_session_factory()()
    try:
        topic = TopicModel(slug="fail-job-topic", name="Fail Job Topic", order_index=0)
        session.add(topic)
        session.commit()
        topic_id = topic.id
    finally:
        session.close()

    create_resp = client.post(
        "/admin/ingestion/jobs",
        json={"topic_slug": "fail-job-topic", "query": "greeks notes"},
    )
    assert create_resp.status_code == 200
    job_id = create_resp.json()["id"]
    assert create_resp.json()["topic_id"] == topic_id

    collecting = client.post(
        f"/admin/ingestion/jobs/{job_id}/status",
        json={"status": "collecting"},
    )
    assert collecting.status_code == 200

    failed = client.post(
        f"/admin/ingestion/jobs/{job_id}/status",
        json={"status": "failed"},
    )
    assert failed.status_code == 200
    assert failed.json()["status"] == "failed"
