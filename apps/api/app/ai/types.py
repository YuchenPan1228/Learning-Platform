from enum import StrEnum

from pydantic import BaseModel, Field


class AIMessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class AIMessage(BaseModel):
    role: AIMessageRole
    content: str = Field(min_length=1)


class AITokenUsage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None


class AIChatResult(BaseModel):
    content: str
    provider: str
    model: str
    token_usage: AITokenUsage
    latency_ms: int = Field(ge=0)
