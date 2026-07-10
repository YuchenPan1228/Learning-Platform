from pydantic import BaseModel, ConfigDict

from app.models.enums import ConceptEdgeRelationshipType


class ConceptSummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    topic_id: int
    topic_slug: str


class ConceptRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    topic_id: int
    topic_slug: str
    definition: str | None
    formula: str | None
    intuition: str | None
    common_mistakes: str | None
    interview_tips: str | None
    prerequisites: str | None


class ConceptNeighborRead(BaseModel):
    slug: str
    name: str
    relationship_type: ConceptEdgeRelationshipType
    direction: str


class ConceptDetailRead(ConceptRead):
    neighbors: list[ConceptNeighborRead]
