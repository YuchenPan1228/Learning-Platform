from pydantic import BaseModel, Field

from app.models.enums import ContentStatus, Difficulty
from app.schemas.question import QuestionSummaryRead


class QuestionUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=300)
    body: str | None = Field(default=None, min_length=1)
    canonical_solution: str | None = None
    short_answer: str | None = None
    difficulty: Difficulty | None = None
    estimated_time_seconds: int | None = Field(default=None, ge=0)
    topic_slug: str | None = Field(default=None, min_length=1, max_length=120)
    subtopic_slug: str | None = None
    company_hint: str | None = None
    expected_solution_pattern: str | None = None
    common_mistakes: list[str] | None = None
    prerequisites: list[str] | None = None
    source_attribution: str | None = None
    status: ContentStatus | None = None


class QuestionListResponse(BaseModel):
    items: list[QuestionSummaryRead]


class QuestionDeleteResponse(BaseModel):
    deleted_id: int
