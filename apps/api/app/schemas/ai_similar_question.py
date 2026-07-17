from pydantic import BaseModel, Field

from app.models.enums import ContentStatus, Difficulty


class GeneratedQuestionContent(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1)
    short_answer: str | None = None
    canonical_solution: str | None = None
    difficulty: Difficulty
    common_mistakes: list[str] = Field(default_factory=list)
    expected_solution_pattern: str | None = None
    estimated_time_seconds: int | None = Field(default=None, ge=1)


class SimilarQuestionResponse(BaseModel):
    source_question_id: int
    draft_question_id: int
    generated_from_id: int
    cache_hit: bool
    title: str
    body: str
    short_answer: str | None
    canonical_solution: str | None
    difficulty: Difficulty
    common_mistakes: list[str] | None
    expected_solution_pattern: str | None
    estimated_time_seconds: int | None
    status: ContentStatus
    topic_id: int
    subtopic_id: int | None
