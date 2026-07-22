from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator

from app.models.enums import ContentStatus, ResourceSourceType


class UrlImportCreate(BaseModel):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=300)
    author: str | None = Field(default=None, max_length=200)
    license: str | None = Field(default=None, max_length=120)
    attribution: str | None = None
    summary: str | None = None


class NoteImportCreate(BaseModel):
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


class PdfMetadataImportCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    file_path: str | None = Field(default=None, max_length=500)
    author: str | None = Field(default=None, max_length=200)
    publisher: str | None = Field(default=None, max_length=200)
    license: str | None = Field(default=None, max_length=120)
    attribution: str | None = None
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
    created_at: datetime
    updated_at: datetime
