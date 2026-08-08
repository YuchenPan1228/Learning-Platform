from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    AllowlistStatus,
    ContentStatus,
    ExtractedObjectType,
    LicenseStatus,
    ResourceSourceType,
    RobotsStatus,
    SourcePolicyDecision,
)
from app.schemas.extracted_duplicate import ExtractedDedupeResultRead


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
    domain_reputation_score: float | None = None
    content_length_score: float | None = None
    formula_density_score: float | None = None
    code_example_score: float | None = None
    educational_structure_score: float | None = None
    human_review_score: float | None = None
    status: ContentStatus


class SourcePolicyStatusRead(BaseModel):
    decision: SourcePolicyDecision
    allowlist_status: AllowlistStatus
    robots_status: RobotsStatus
    license_status: LicenseStatus
    attribution_required: bool
    attribution_present: bool
    reasons: list[str]
    host: str | None = None


class SourceQualityStatusRead(BaseModel):
    draft_quality_score: float | None = None
    resource_quality_score: float | None = None
    overall_score: float | None = None
    domain_reputation_score: float | None = None
    content_length_score: float | None = None
    formula_density_score: float | None = None
    code_example_score: float | None = None
    educational_structure_score: float | None = None
    human_review_score: float | None = None


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
    # Populated on detail GET for review UI (QP-046); list may leave these null.
    policy: SourcePolicyStatusRead | None = None
    quality: SourceQualityStatusRead | None = None
    duplicates: ExtractedDedupeResultRead | None = None


class ExtractedObjectEdit(BaseModel):
    payload_json: dict[str, Any] | None = None
    object_type: ExtractedObjectType | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    quality_score: float | None = Field(default=None, ge=0, le=1)


class ReviewQueueResponse(BaseModel):
    items: list[ExtractedObjectReviewRead]
