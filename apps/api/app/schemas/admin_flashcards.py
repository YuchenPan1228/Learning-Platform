from pydantic import BaseModel, Field

from app.models.enums import Difficulty
from app.schemas.flashcard import FlashcardRead


class FlashcardUpdate(BaseModel):
    front: str | None = Field(default=None, min_length=1)
    back: str | None = Field(default=None, min_length=1)
    topic_slug: str | None = Field(default=None, min_length=1, max_length=120)
    difficulty: Difficulty | None = None


class FlashcardListResponse(BaseModel):
    items: list[FlashcardRead]


class FlashcardDeleteResponse(BaseModel):
    deleted_id: int
