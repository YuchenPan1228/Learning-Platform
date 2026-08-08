from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from app.models.enums import ContentStatus, Difficulty, ExtractedObjectType, ResourceSourceType

_IMPORT_OBJECT_TYPES = frozenset(
    {
        ExtractedObjectType.QUESTION,
    }
)


class ImportDraftOptions(BaseModel):
    object_type: ExtractedObjectType = ExtractedObjectType.QUESTION
    topic_slug: str = Field(min_length=1, max_length=120)
    subtopic_slug: str | None = Field(default=None, max_length=120)

    @field_validator("object_type")
    @classmethod
    def validate_import_object_type(cls, value: ExtractedObjectType) -> ExtractedObjectType:
        if value not in _IMPORT_OBJECT_TYPES:
            raise ValueError("object_type must be question")
        return value


class UrlImportCreate(ImportDraftOptions):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=300)
    author: str | None = Field(default=None, max_length=200)
    license: str | None = Field(default=None, max_length=120)
    attribution: str | None = None
    summary: str | None = None


class NoteImportCreate(ImportDraftOptions):
    note_text: str = Field(min_length=1)
    title: str | None = Field(default=None, max_length=300)
    author: str | None = Field(default=None, max_length=200)
    license: str | None = Field(default=None, max_length=120)
    attribution: str | None = None
    source_type: ResourceSourceType = ResourceSourceType.MANUAL

    @field_validator("source_type")
    @classmethod
    def validate_note_source_type(cls, value: ResourceSourceType) -> ResourceSourceType:
        if value not in {ResourceSourceType.MANUAL, ResourceSourceType.BOOK_NOTE}:
            raise ValueError("source_type must be manual or book_note")
        return value


class QuestionImportCreate(ImportDraftOptions):
    title: str = Field(min_length=1, max_length=300)
    body: str = Field(min_length=1)
    short_answer: str | None = None
    difficulty: Difficulty | None = None
    author: str | None = Field(default=None, max_length=200)
    license: str | None = Field(default=None, max_length=120)
    attribution: str | None = None

    @model_validator(mode="after")
    def validate_question_import(self) -> Self:
        if self.object_type is not ExtractedObjectType.QUESTION:
            raise ValueError("question import requires object_type question")
        return self


class PdfImportCreate(ImportDraftOptions):
    title: str | None = Field(default=None, max_length=300)
    summary: str | None = None


class ResourceImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_type: ResourceSourceType
    url: str | None
    title: str | None
    author: str | None
    publisher: str | None
    license: str | None
    attribution: str | None
    summary: str | None
    raw_text_hash: str | None
    status: ContentStatus
    # First draft id (convenience); full list is extracted_object_ids.
    extracted_object_id: int | None = None
    extracted_object_ids: list[int] = Field(default_factory=list)
    draft_count: int = 0
    extraction_method: str | None = None
    policy_decision: str | None = None
    created_at: datetime
    updated_at: datetime
