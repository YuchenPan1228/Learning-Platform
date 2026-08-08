from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from app.models.enums import Difficulty, ExtractedObjectType


class AIProposedQuestionDraft(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str = Field(min_length=1, max_length=300)
    body: str = Field(
        min_length=1,
        validation_alias=AliasChoices("body", "question", "stem", "prompt", "text"),
    )
    short_answer: str | None = Field(
        default=None,
        validation_alias=AliasChoices("short_answer", "answer", "solution_short"),
    )
    canonical_solution: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "canonical_solution",
            "solution",
            "worked_solution",
            "explanation",
        ),
    )
    difficulty: Difficulty | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class AIStructuredExtractionContent(BaseModel):
    """Schema the model must return for structured source parsing (QP-043)."""

    summary: str | None = Field(default=None, max_length=2000)
    topic_slug: str | None = Field(default=None, max_length=120)
    subtopic_slug: str | None = Field(default=None, max_length=120)
    source_title: str | None = Field(default=None, max_length=300)
    questions: list[AIProposedQuestionDraft] = Field(default_factory=list, max_length=10)


class ExtractedDraftSummary(BaseModel):
    id: int
    object_type: ExtractedObjectType
    title: str | None = None
    confidence_score: float | None = None


class AIStructuredExtractionResult(BaseModel):
    summary: str | None
    topic_slug: str | None
    subtopic_slug: str | None
    source_title: str | None
    model_version: str
    extraction_method: str
    cache_hit: bool
    drafts: list[ExtractedDraftSummary]
