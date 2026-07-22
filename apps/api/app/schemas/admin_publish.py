from typing import Literal

from pydantic import BaseModel

from app.models.enums import ExtractedObjectType
from app.schemas.duplicate import DuplicateMatchRead


class PublishedObjectRef(BaseModel):
    kind: Literal["concept", "question", "flashcard"]
    id: int


class PublishExtractedObjectResponse(BaseModel):
    extracted_object_id: int
    object_type: ExtractedObjectType
    published: PublishedObjectRef
    duplicate_warnings: list[DuplicateMatchRead]
