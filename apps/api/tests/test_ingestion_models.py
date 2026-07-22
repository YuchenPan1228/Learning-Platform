from datetime import UTC, datetime
from decimal import Decimal

import pytest
from app.models.enums import (
    ContentStatus,
    ExtractedObjectType,
    JobExecutionStage,
    JobExecutionStatus,
    ResourceSourceType,
    TopicJobCreatedBy,
    TopicJobStatus,
)
from app.models.extracted_object import ExtractedObject
from app.models.job_execution_log import JobExecutionLog
from app.models.resource import Resource
from app.models.topic import Topic
from app.models.topic_job import TopicJob
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage


@pytest.mark.integration
def test_ingestion_models_persist_with_relations(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory

    session = get_session_factory()()
    try:
        topic = Topic(slug="ingestion-test-topic", name="Ingestion Test Topic", order_index=0)
        session.add(topic)
        session.flush()

        resource = Resource(
            source_type=ResourceSourceType.URL,
            url="https://example.com/bayes",
            title="Bayes notes",
            license="CC-BY-4.0",
            quality_score=0.8,
            status=ContentStatus.DRAFT,
        )
        session.add(resource)
        session.flush()

        topic_job = TopicJob(
            topic_id=topic.id,
            query="conditional probability bayes",
            target_source_count=3,
            status=TopicJobStatus.QUEUED,
            priority=1,
            created_by=TopicJobCreatedBy.ADMIN,
        )
        session.add(topic_job)
        session.flush()

        extracted = ExtractedObject(
            resource_id=resource.id,
            topic_job_id=topic_job.id,
            object_type=ExtractedObjectType.QUESTION,
            payload_json={"title": "Bayes draft", "body": "What is P(A|B)?"},
            confidence_score=0.9,
            quality_score=0.7,
            status=ContentStatus.DRAFT,
            extraction_method="manual",
            model_version=None,
        )
        session.add(extracted)

        usage = record_ai_usage(
            session,
            AIUsageRecordInput(
                provider="ollama",
                model="qwen2.5:3b",
                input_tokens=10,
                output_tokens=20,
                latency_ms=100,
                cache_hit=False,
            ),
        )

        started = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
        finished = datetime(2026, 7, 22, 12, 0, 1, tzinfo=UTC)
        log = JobExecutionLog(
            topic_job_id=topic_job.id,
            stage=JobExecutionStage.AI_EXTRACTION,
            status=JobExecutionStatus.SUCCEEDED,
            started_at=started,
            finished_at=finished,
            runtime_ms=1000,
            source_url=resource.url,
            model="qwen2.5:3b",
            input_tokens=10,
            output_tokens=20,
            estimated_cost_usd=Decimal("0"),
            ai_usage_log_id=usage.id,
        )
        session.add(log)
        session.commit()

        session.refresh(topic_job)
        session.refresh(resource)
        session.refresh(extracted)
        session.refresh(log)

        assert topic_job.id is not None
        assert topic_job.status is TopicJobStatus.QUEUED
        assert resource.source_type is ResourceSourceType.URL
        assert extracted.object_type is ExtractedObjectType.QUESTION
        assert extracted.payload_json["title"] == "Bayes draft"
        assert extracted.duplicate_cluster_id is None
        assert log.ai_usage_log_id == usage.id
        assert log.stage is JobExecutionStage.AI_EXTRACTION
        assert len(topic_job.extracted_objects) == 1
        assert len(topic_job.execution_logs) == 1
        assert len(resource.extracted_objects) == 1
    finally:
        session.close()
