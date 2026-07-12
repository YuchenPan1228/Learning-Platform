from pydantic import BaseModel, ConfigDict

from app.models.enums import ContentStatus, Difficulty
from app.schemas.tag import TagRead


class QuestionSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    difficulty: Difficulty
    topic_id: int
    topic_slug: str
    subtopic_id: int | None
    subtopic_slug: str | None
    estimated_time_seconds: int | None
    company_hint: str | None
    status: ContentStatus
    tags: list[TagRead]


class QuestionDetailRead(QuestionSummaryRead):
    body: str
    canonical_solution: str | None
    short_answer: str | None
    expected_solution_pattern: str | None
    common_mistakes: list[str] | None
    prerequisites: list[str] | None
    source_attribution: str | None
