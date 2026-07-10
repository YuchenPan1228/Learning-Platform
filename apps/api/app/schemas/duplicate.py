from pydantic import BaseModel

from app.models.enums import DuplicateMatchType


class DuplicateMatchRead(BaseModel):
    question_id: int
    title: str
    match_type: DuplicateMatchType
    similarity_score: float | None


class QuestionDuplicatesRead(BaseModel):
    question_id: int
    matches: list[DuplicateMatchRead]
