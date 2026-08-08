from pydantic import BaseModel, Field

from app.models.enums import Difficulty, ExtractedObjectType


class AIProposedQuestionDraft(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1)
    short_answer: str | None = None
    canonical_solution: str | None = None
    difficulty: Difficulty | None = None
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class AIProposedFlashcardDraft(BaseModel):
    front: str = Field(min_length=1, max_length=300)
    back: str = Field(min_length=1)
    confidence_score: float | None = Field(default=None, ge=0, le=1)


class AIStructuredExtractionContent(BaseModel):
    """Schema the model must return for structured source parsing (QP-043)."""

    summary: str | None = Field(default=None, max_length=2000)
    topic_slug: str | None = Field(default=None, max_length=120)
    subtopic_slug: str | None = Field(default=None, max_length=120)
    source_title: str | None = Field(default=None, max_length=300)
    questions: list[AIProposedQuestionDraft] = Field(default_factory=list, max_length=10)
    flashcards: list[AIProposedFlashcardDraft] = Field(default_factory=list, max_length=15)


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
