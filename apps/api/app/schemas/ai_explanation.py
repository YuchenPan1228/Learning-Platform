from pydantic import BaseModel, Field


class AIExplanationRequest(BaseModel):
    answer: str = Field(min_length=1)


class AIHintsContent(BaseModel):
    hints: list[str] = Field(min_length=1, max_length=2)


class AIHintsResponse(AIHintsContent):
    question_id: int
    cache_hit: bool


class AIExplanationContent(BaseModel):
    explanation: str = Field(min_length=1, max_length=900)


class AIExplanationResponse(AIExplanationContent):
    question_id: int
    cache_hit: bool
