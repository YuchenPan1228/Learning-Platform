from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    JobExecutionStage,
    JobExecutionStatus,
    TopicJobCreatedBy,
    TopicJobStatus,
)


class TopicJobCreate(BaseModel):
    query: str = Field(min_length=1)
    topic_id: int | None = None
    topic_slug: str | None = Field(default=None, max_length=120)
    concept_id: int | None = None
    target_source_count: int = Field(default=5, ge=1, le=100)
    priority: int = Field(default=0, ge=-1000, le=1000)
    created_by: TopicJobCreatedBy = TopicJobCreatedBy.ADMIN


class TopicJobStatusUpdate(BaseModel):
    status: TopicJobStatus


class JobExecutionLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_job_id: int
    stage: JobExecutionStage
    status: JobExecutionStatus
    started_at: datetime
    finished_at: datetime | None
    runtime_ms: int | None
    failure_reason: str | None
    source_url: str | None
    model: str | None
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost_usd: Decimal | None
    ai_usage_log_id: int | None


class TopicJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int
    topic_slug: str | None = None
    concept_id: int | None
    query: str
    target_source_count: int
    status: TopicJobStatus
    priority: int
    created_by: TopicJobCreatedBy
    created_at: datetime
    updated_at: datetime


class TopicJobDetailRead(TopicJobRead):
    execution_logs: list[JobExecutionLogRead] = Field(default_factory=list)


class TopicJobListResponse(BaseModel):
    items: list[TopicJobRead]
