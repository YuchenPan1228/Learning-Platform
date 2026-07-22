from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    ContentStatus,
    ExtractedObjectType,
    ResourceSourceType,
)


class ResourceProvenanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: ResourceSourceType
    url: str | None
    title: str | None
    author: str | None
    publisher: str | None
    license: str | None
    attribution: str | None
    summary: str | None
    quality_score: float | None
    status: ContentStatus


class ExtractedObjectReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    resource_id: int | None
    topic_job_id: int | None
    object_type: ExtractedObjectType
    payload_json: dict[str, Any]
    confidence_score: float | None
    quality_score: float | None
    duplicate_cluster_id: int | None
    status: ContentStatus
    extraction_method: str | None
    model_version: str | None
    created_at: datetime
    updated_at: datetime
    resource: ResourceProvenanceRead | None = None


class ExtractedObjectEdit(BaseModel):
    payload_json: dict[str, Any] | None = None
    object_type: ExtractedObjectType | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    quality_score: float | None = Field(default=None, ge=0, le=1)


class ReviewQueueResponse(BaseModel):
    items: list[ExtractedObjectReviewRead]
