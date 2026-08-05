from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.concept import Concept
from app.models.enums import TopicJobCreatedBy, TopicJobStatus
from app.models.topic import Topic
from app.models.topic_job import TopicJob
from app.schemas.topic_job import (
    JobExecutionLogRead,
    TopicJobDetailRead,
    TopicJobListResponse,
    TopicJobRead,
)

# Happy-path progression plus fail from any active status.
# Terminal states (completed, failed) accept no further transitions.
_ALLOWED_TRANSITIONS: dict[TopicJobStatus, frozenset[TopicJobStatus]] = {
    TopicJobStatus.QUEUED: frozenset({TopicJobStatus.COLLECTING, TopicJobStatus.FAILED}),
    TopicJobStatus.COLLECTING: frozenset({TopicJobStatus.EXTRACTING, TopicJobStatus.FAILED}),
    TopicJobStatus.EXTRACTING: frozenset({TopicJobStatus.REVIEWING, TopicJobStatus.FAILED}),
    TopicJobStatus.REVIEWING: frozenset({TopicJobStatus.COMPLETED, TopicJobStatus.FAILED}),
    TopicJobStatus.COMPLETED: frozenset(),
    TopicJobStatus.FAILED: frozenset(),
}

_ACTIVE_STATUSES = frozenset(
    {
        TopicJobStatus.QUEUED,
        TopicJobStatus.COLLECTING,
        TopicJobStatus.EXTRACTING,
        TopicJobStatus.REVIEWING,
    }
)


class TopicJobError(ValueError):
    """Raised when a topic job create or transition is invalid."""


@dataclass(frozen=True, slots=True)
class TopicJobCreateInput:
    query: str
    topic_id: int | None = None
    topic_slug: str | None = None
    concept_id: int | None = None
    target_source_count: int = 5
    priority: int = 0
    created_by: TopicJobCreatedBy = TopicJobCreatedBy.ADMIN


def create_topic_job(session: Session, data: TopicJobCreateInput) -> TopicJobDetailRead:
    query = data.query.strip()
    if not query:
        raise TopicJobError("query must not be blank")
    if data.target_source_count < 1:
        raise TopicJobError("target_source_count must be at least 1")

    topic = _resolve_topic(session, topic_id=data.topic_id, topic_slug=data.topic_slug)
    if data.concept_id is not None:
        concept = session.get(Concept, data.concept_id)
        if concept is None:
            raise TopicJobError(f"concept {data.concept_id} not found")
        if concept.topic_id != topic.id:
            raise TopicJobError(
                f"concept {data.concept_id} does not belong to topic {topic.id}",
            )

    job = TopicJob(
        topic_id=topic.id,
        concept_id=data.concept_id,
        query=query,
        target_source_count=data.target_source_count,
        status=TopicJobStatus.QUEUED,
        priority=data.priority,
        created_by=data.created_by,
    )
    session.add(job)
    session.commit()
    return get_topic_job(session, job.id)


def get_topic_job(session: Session, job_id: int) -> TopicJobDetailRead:
    job = _get_job(session, job_id, with_logs=True)
    return _detail_read(job)


def list_topic_jobs(
    session: Session,
    *,
    status: TopicJobStatus | None = None,
    topic_id: int | None = None,
    limit: int = 50,
) -> TopicJobListResponse:
    if limit < 1 or limit > 200:
        raise TopicJobError("limit must be between 1 and 200")

    query = (
        select(TopicJob)
        .options(joinedload(TopicJob.topic))
        .order_by(TopicJob.priority.desc(), TopicJob.id.desc())
        .limit(limit)
    )
    if status is not None:
        query = query.where(TopicJob.status == status)
    if topic_id is not None:
        query = query.where(TopicJob.topic_id == topic_id)

    jobs = session.scalars(query).unique().all()
    return TopicJobListResponse(items=[_summary_read(job) for job in jobs])


def transition_topic_job(
    session: Session,
    job_id: int,
    new_status: TopicJobStatus,
) -> TopicJobDetailRead:
    job = _get_job(session, job_id, with_logs=True)
    allowed = _ALLOWED_TRANSITIONS[job.status]
    if new_status not in allowed:
        raise TopicJobError(
            f"cannot transition topic job {job_id} from {job.status.value} to {new_status.value}",
        )

    job.status = new_status
    session.add(job)
    session.commit()
    return get_topic_job(session, job.id)


def mark_collecting(session: Session, job_id: int) -> TopicJobDetailRead:
    return transition_topic_job(session, job_id, TopicJobStatus.COLLECTING)


def mark_extracting(session: Session, job_id: int) -> TopicJobDetailRead:
    return transition_topic_job(session, job_id, TopicJobStatus.EXTRACTING)


def mark_reviewing(session: Session, job_id: int) -> TopicJobDetailRead:
    return transition_topic_job(session, job_id, TopicJobStatus.REVIEWING)


def mark_completed(session: Session, job_id: int) -> TopicJobDetailRead:
    return transition_topic_job(session, job_id, TopicJobStatus.COMPLETED)


def mark_failed(session: Session, job_id: int) -> TopicJobDetailRead:
    return transition_topic_job(session, job_id, TopicJobStatus.FAILED)


def allowed_transitions(status: TopicJobStatus) -> frozenset[TopicJobStatus]:
    return _ALLOWED_TRANSITIONS[status]


def is_terminal(status: TopicJobStatus) -> bool:
    return status not in _ACTIVE_STATUSES


def _resolve_topic(
    session: Session,
    *,
    topic_id: int | None,
    topic_slug: str | None,
) -> Topic:
    if topic_id is not None and topic_slug is not None:
        raise TopicJobError("provide topic_id or topic_slug, not both")
    if topic_id is None and topic_slug is None:
        raise TopicJobError("topic_id or topic_slug is required")

    if topic_id is not None:
        topic = session.get(Topic, topic_id)
        if topic is None:
            raise TopicJobError(f"topic {topic_id} not found")
        return topic

    slug = (topic_slug or "").strip()
    if not slug:
        raise TopicJobError("topic_slug must not be blank")
    topic = session.scalar(select(Topic).where(Topic.slug == slug))
    if topic is None:
        raise TopicJobError(f"topic '{slug}' not found")
    return topic


def _get_job(session: Session, job_id: int, *, with_logs: bool) -> TopicJob:
    query = select(TopicJob).where(TopicJob.id == job_id).options(joinedload(TopicJob.topic))
    if with_logs:
        query = query.options(selectinload(TopicJob.execution_logs))
    job = session.scalar(query)
    if job is None:
        raise LookupError(f"topic job {job_id} not found")
    return job


def _summary_read(job: TopicJob) -> TopicJobRead:
    topic_slug = job.topic.slug if job.topic is not None else None
    return TopicJobRead(
        id=job.id,
        topic_id=job.topic_id,
        topic_slug=topic_slug,
        concept_id=job.concept_id,
        query=job.query,
        target_source_count=job.target_source_count,
        status=job.status,
        priority=job.priority,
        created_by=job.created_by,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def _detail_read(job: TopicJob) -> TopicJobDetailRead:
    summary = _summary_read(job)
    logs = sorted(job.execution_logs, key=lambda row: (row.started_at, row.id))
    return TopicJobDetailRead(
        **summary.model_dump(),
        execution_logs=[JobExecutionLogRead.model_validate(log) for log in logs],
    )
