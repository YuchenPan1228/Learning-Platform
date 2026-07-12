from pydantic import BaseModel

from app.models.enums import QuestionProgressStatus


class QuestionProgressRead(BaseModel):
    question_id: int
    status: QuestionProgressStatus
    attempt_count: int


class AttemptProgressResponse(BaseModel):
    questions: list[QuestionProgressRead]
