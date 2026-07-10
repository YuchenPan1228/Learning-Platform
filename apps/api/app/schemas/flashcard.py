from pydantic import BaseModel, ConfigDict

from app.models.enums import Difficulty


class FlashcardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    front: str
    back: str
    topic_id: int
    topic_slug: str
    difficulty: Difficulty | None
