from datetime import datetime

from pydantic import BaseModel


class TopicMasterySnapshot(BaseModel):
    topic_id: int
    slug: str
    name: str
    mastery_score: float
    attempts_count: int
    last_practiced_at: datetime | None
    next_review_at: datetime | None


class ConceptMasterySnapshot(BaseModel):
    concept_id: int
    slug: str
    name: str
    topic_id: int
    topic_slug: str
    mastery_score: float
    attempts_count: int
    last_practiced_at: datetime | None


class MasteryRead(BaseModel):
    user_id: str
    topic_mastery: list[TopicMasterySnapshot]
    concept_mastery: list[ConceptMasterySnapshot]
