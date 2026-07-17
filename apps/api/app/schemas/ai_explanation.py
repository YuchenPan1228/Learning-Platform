from pydantic import BaseModel, Field


class AIExplanationRequest(BaseModel):
    answer: str = Field(min_length=1)


class AIExplanationContent(BaseModel):
    explanation: str = Field(min_length=1)
    hints: list[str] = Field(min_length=1)
    common_mistakes: list[str]


class AIExplanationResponse(AIExplanationContent):
    question_id: int
    cache_hit: bool
