from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class StudyPlanItemKind(StrEnum):
    FLASHCARD_REVIEW = "flashcard_review"
    PREREQUISITE_REPAIR = "prerequisite_repair"
    PRACTICE = "practice"


class StudyPlanItemRead(BaseModel):
    kind: StudyPlanItemKind
    title: str
    description: str
    duration_minutes: int = Field(ge=1)
    href: str | None = None
    topic_slug: str | None = None
    concept_slug: str | None = None


class DailyStudyPlanRead(BaseModel):
    user_id: str
    generated_at: datetime
    target_minutes: int
    total_minutes: int
    summary: str
    detail: str
    items: list[StudyPlanItemRead]
