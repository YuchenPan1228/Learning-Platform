from pydantic import BaseModel, Field

from app.schemas.concept import ConceptSummaryRead


class ConceptUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, min_length=1, max_length=120)
    definition: str | None = None
    formula: str | None = None
    intuition: str | None = None
    worked_example: str | None = None
    common_mistakes: str | None = None
    interview_tips: str | None = None
    prerequisites: str | None = None


class ConceptListResponse(BaseModel):
    items: list[ConceptSummaryRead]
