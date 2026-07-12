from pydantic import BaseModel

from app.models.enums import ManualQuestionProgressStatus, QuestionProgressStatus


class QuestionProgressRead(BaseModel):
    question_id: int
    status: QuestionProgressStatus
    attempt_count: int
    manually_marked: bool


class AttemptProgressResponse(BaseModel):
    questions: list[QuestionProgressRead]


class SetQuestionProgressRequest(BaseModel):
    status: ManualQuestionProgressStatus
