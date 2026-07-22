from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.ai_usage_log import AIUsageLog
from app.models.enums import JobExecutionStage, JobExecutionStatus
from app.models.job_execution_log import JobExecutionLog


@dataclass(frozen=True, slots=True)
class JobExecutionStartInput:
    topic_job_id: int
    stage: JobExecutionStage
    source_url: str | None = None
    model: str | None = None
    started_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class JobExecutionFinishInput:
    source_url: str | None = None
    model: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    estimated_cost_usd: Decimal | None = None
    ai_usage_log_id: int | None = None
    finished_at: datetime | None = None


def start_job_execution(session: Session, start: JobExecutionStartInput) -> JobExecutionLog:
    started_at = start.started_at or datetime.now(UTC)
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)

    log = JobExecutionLog(
        topic_job_id=start.topic_job_id,
        stage=start.stage,
        status=JobExecutionStatus.RUNNING,
        started_at=started_at,
        source_url=start.source_url,
        model=start.model,
    )
    session.add(log)
    session.commit()
    session.refresh(log)
    return log


def complete_job_execution(
    session: Session,
    log: JobExecutionLog,
    finish: JobExecutionFinishInput | None = None,
) -> JobExecutionLog:
    return _finish_job_execution(
        session,
        log,
        status=JobExecutionStatus.SUCCEEDED,
        failure_reason=None,
        finish=finish or JobExecutionFinishInput(),
    )


def fail_job_execution(
    session: Session,
    log: JobExecutionLog,
    *,
    failure_reason: str,
    finish: JobExecutionFinishInput | None = None,
) -> JobExecutionLog:
    return _finish_job_execution(
        session,
        log,
        status=JobExecutionStatus.FAILED,
        failure_reason=failure_reason,
        finish=finish or JobExecutionFinishInput(),
    )


@contextmanager
def track_job_execution(
    session: Session,
    start: JobExecutionStartInput,
) -> Iterator[JobExecutionLog]:
    """Start a RUNNING log and auto-complete or fail when the block exits."""
    log = start_job_execution(session, start)
    try:
        yield log
    except Exception as exc:
        if log.status is JobExecutionStatus.RUNNING:
            fail_job_execution(session, log, failure_reason=str(exc))
        raise
    else:
        if log.status is JobExecutionStatus.RUNNING:
            complete_job_execution(session, log)


def _finish_job_execution(
    session: Session,
    log: JobExecutionLog,
    *,
    status: JobExecutionStatus,
    failure_reason: str | None,
    finish: JobExecutionFinishInput,
) -> JobExecutionLog:
    if log.status is not JobExecutionStatus.RUNNING:
        raise ValueError(
            f"Job execution log {log.id} is {log.status.value}, expected running",
        )

    finished_at = finish.finished_at or datetime.now(UTC)
    if finished_at.tzinfo is None:
        finished_at = finished_at.replace(tzinfo=UTC)

    started_at = log.started_at
    if started_at.tzinfo is None:
        started_at = started_at.replace(tzinfo=UTC)

    runtime_ms = max(0, int((finished_at - started_at).total_seconds() * 1000))

    source_url = finish.source_url if finish.source_url is not None else log.source_url
    model = finish.model if finish.model is not None else log.model
    input_tokens = finish.input_tokens
    output_tokens = finish.output_tokens
    estimated_cost_usd = finish.estimated_cost_usd
    ai_usage_log_id = finish.ai_usage_log_id

    if ai_usage_log_id is not None:
        usage = session.get(AIUsageLog, ai_usage_log_id)
        if usage is None:
            raise ValueError(f"AI usage log {ai_usage_log_id} not found")
        if model is None:
            model = usage.model
        if input_tokens is None:
            input_tokens = usage.input_tokens
        if output_tokens is None:
            output_tokens = usage.output_tokens
        if estimated_cost_usd is None:
            estimated_cost_usd = usage.estimated_cost_usd

    log.status = status
    log.finished_at = finished_at
    log.runtime_ms = runtime_ms
    log.failure_reason = failure_reason
    log.source_url = source_url
    log.model = model
    log.input_tokens = input_tokens
    log.output_tokens = output_tokens
    log.estimated_cost_usd = estimated_cost_usd
    log.ai_usage_log_id = ai_usage_log_id

    session.add(log)
    session.commit()
    session.refresh(log)
    return log
