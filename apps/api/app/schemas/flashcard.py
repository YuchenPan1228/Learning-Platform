from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty, FlashcardReviewRating


class FlashcardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    front: str
    back: str
    topic_id: int
    topic_slug: str
    difficulty: Difficulty | None
    next_review_at: datetime | None = None
    interval_days: float | None = None
    ease_factor: float | None = None
    repetitions: int | None = None
    last_reviewed_at: datetime | None = None
    last_rating: FlashcardReviewRating | None = None
    is_due: bool = True


class FlashcardReviewRequest(BaseModel):
    rating: FlashcardReviewRating


class FlashcardReviewResponse(BaseModel):
    flashcard: FlashcardRead
    rating: FlashcardReviewRating
    next_review_at: datetime
    interval_days: float
    ease_factor: float
    repetitions: int


class FlashcardListPage(BaseModel):
    items: list[FlashcardRead]
    total: int
    limit: int
    offset: int
