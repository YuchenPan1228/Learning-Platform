from pydantic import BaseModel, Field


class SelfCheckRequest(BaseModel):
    answer: str = Field(min_length=1)


class SelfCheckResponse(BaseModel):
    question_id: int
    supported: bool
    is_correct: bool | None
    feedback: str
