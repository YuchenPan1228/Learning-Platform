from datetime import datetime

from pydantic import BaseModel, Field


class WeakConceptRead(BaseModel):
    concept_id: int
    slug: str
    name: str
    topic_id: int
    topic_slug: str
    mastery_score: float
    attempts_count: int


class AttemptHistoryItemRead(BaseModel):
    id: int
    question_id: int
    question_title: str
    topic_id: int
    topic_slug: str
    is_correct: bool | None
    score: float | None
    time_spent_seconds: int
    created_at: datetime


class SearchMissRead(BaseModel):
    id: int
    query: str
    topic_slug: str | None = None
    types: list[str] = Field(default_factory=list)
    created_at: datetime


class LearningAnalyticsRead(BaseModel):
    user_id: str
    weak_concepts: list[WeakConceptRead]
    attempt_history: list[AttemptHistoryItemRead]
    review_due_count: int
    search_misses: list[SearchMissRead]
