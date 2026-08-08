from pydantic import BaseModel

from app.models.enums import ContentStatus, DuplicateMatchType, ExtractedObjectType


class ExtractedDuplicateMatchRead(BaseModel):
    source: str
    object_id: int
    title: str
    match_type: DuplicateMatchType
    similarity_score: float | None = None
    status: ContentStatus | None = None
    confidence_score: float | None = None


class CanonicalSuggestionRead(BaseModel):
    kind: str
    object_id: int
    title: str
    reason: str


class ExtractedDedupeResultRead(BaseModel):
    extracted_object_id: int
    object_type: ExtractedObjectType
    raw_text_hash: str
    normalized_text_hash: str
    normalized_text: str
    matches: list[ExtractedDuplicateMatchRead]
    suggested_canonical: CanonicalSuggestionRead
