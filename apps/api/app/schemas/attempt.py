from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AttemptCreate(BaseModel):
    question_id: int
    answer: str = Field(min_length=1)
    time_spent_seconds: int = Field(ge=0)


class AttemptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    topic_id: int
    answer: str
    supported: bool
    is_correct: bool | None
    score: float | None
    feedback: str | None
    time_spent_seconds: int
    created_at: datetime
