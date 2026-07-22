from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import ContentStatus, Difficulty, ExtractedObjectType, ResourceSourceType
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource

_MANUAL_IMPORT_METHOD = "manual:import"
_NOTE_SOURCE_TYPES = frozenset(
    {
        ResourceSourceType.MANUAL,
        ResourceSourceType.BOOK_NOTE,
    }
)
_QUESTION_PLACEHOLDER_BODY = (
    "Edit this draft with the interview question stem. "
    "Add context from the linked source before publishing."
)
_FLASHCARD_PLACEHOLDER_BACK = (
    "Edit this draft with the flashcard answer before publishing."
)


@dataclass(frozen=True, slots=True)
class DraftImportOptions:
    object_type: ExtractedObjectType
    topic_slug: str
    subtopic_slug: str | None = None


@dataclass(frozen=True, slots=True)
class QuestionDraftFields:
    title: str
    body: str
    short_answer: str | None = None
    difficulty: Difficulty | None = None


def create_extracted_draft_from_resource(
    session: Session,
    resource: Resource,
    *,
    options: DraftImportOptions,
    question_fields: QuestionDraftFields | None = None,
) -> ExtractedObject:
    extracted = ExtractedObject(
        resource_id=resource.id,
        object_type=options.object_type,
        payload_json=_build_import_payload(
            resource,
            options=options,
            question_fields=question_fields,
        ),
        confidence_score=1.0,
        quality_score=None,
        status=ContentStatus.DRAFT,
        extraction_method=_MANUAL_IMPORT_METHOD,
        model_version=None,
    )
    session.add(extracted)
    return extracted


def _build_import_payload(
    resource: Resource,
    *,
    options: DraftImportOptions,
    question_fields: QuestionDraftFields | None = None,
) -> dict[str, Any]:
    if question_fields is not None:
        return _payload_for_question(
            title=question_fields.title,
            body=question_fields.body,
            options=options,
            short_answer=question_fields.short_answer,
            difficulty=question_fields.difficulty,
            extracted_text=question_fields.body,
        )

    title = _blank_to_none(resource.title)
    summary = _blank_to_none(resource.summary)

    if resource.source_type == ResourceSourceType.URL:
        return _payload_for_url(resource, title=title, summary=summary, options=options)

    if resource.source_type in _NOTE_SOURCE_TYPES:
        return _payload_for_note(title=title, note_text=summary, options=options)

    if resource.source_type == ResourceSourceType.PDF:
        return _payload_for_pdf(title=title, summary=summary, options=options)

    if options.object_type is ExtractedObjectType.FLASHCARD:
        display_title = title or "Imported flashcard"
        return _payload_for_flashcard(
            front=display_title,
            back=summary or _FLASHCARD_PLACEHOLDER_BACK,
            options=options,
            extracted_text=summary,
        )

    display_title = title or "Imported question"
    return _payload_for_question(
        title=display_title,
        body=summary or _QUESTION_PLACEHOLDER_BODY,
        options=options,
        extracted_text=summary or display_title,
    )


def _topic_fields(options: DraftImportOptions) -> dict[str, Any]:
    payload: dict[str, Any] = {"topic_slug": options.topic_slug}
    if options.subtopic_slug is not None:
        payload["subtopic_slug"] = options.subtopic_slug
    return payload


def _payload_for_question(
    *,
    title: str,
    body: str,
    options: DraftImportOptions,
    short_answer: str | None = None,
    difficulty: Difficulty | None = None,
    extracted_text: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "title": title,
        "body": body,
        "extracted_text": extracted_text or body,
        **_topic_fields(options),
    }
    if short_answer is not None:
        payload["short_answer"] = short_answer
    if difficulty is not None:
        payload["difficulty"] = difficulty.value
    return payload


def _payload_for_flashcard(
    *,
    front: str,
    back: str,
    options: DraftImportOptions,
    extracted_text: str | None = None,
) -> dict[str, Any]:
    return {
        "front": front,
        "back": back,
        "title": front,
        "extracted_text": extracted_text or back,
        **_topic_fields(options),
    }


def _payload_for_url(
    resource: Resource,
    *,
    title: str | None,
    summary: str | None,
    options: DraftImportOptions,
) -> dict[str, Any]:
    display_title = title or resource.url or "Imported URL"
    if options.object_type is ExtractedObjectType.FLASHCARD:
        return _payload_for_flashcard(
            front=display_title,
            back=summary or _FLASHCARD_PLACEHOLDER_BACK,
            options=options,
            extracted_text=summary or resource.url,
        )

    body = summary or _QUESTION_PLACEHOLDER_BODY
    return _payload_for_question(
        title=display_title,
        body=body,
        options=options,
        extracted_text=summary or resource.url,
    )


def _payload_for_note(
    *,
    title: str | None,
    note_text: str | None,
    options: DraftImportOptions,
) -> dict[str, Any]:
    if note_text is None:
        raise ValueError("note import requires non-empty note text")

    if options.object_type is ExtractedObjectType.FLASHCARD:
        front = title or _first_line(note_text) or "Imported flashcard"
        return _payload_for_flashcard(
            front=front,
            back=note_text,
            options=options,
            extracted_text=note_text,
        )

    display_title = title or _first_line(note_text) or "Imported question"
    return _payload_for_question(
        title=display_title,
        body=note_text,
        options=options,
        extracted_text=note_text,
    )


def _payload_for_pdf(
    *,
    title: str | None,
    summary: str | None,
    options: DraftImportOptions,
) -> dict[str, Any]:
    if title is None:
        raise ValueError("pdf import requires a title")

    if options.object_type is ExtractedObjectType.FLASHCARD:
        return _payload_for_flashcard(
            front=title,
            back=summary or _FLASHCARD_PLACEHOLDER_BACK,
            options=options,
            extracted_text=summary or title,
        )

    return _payload_for_question(
        title=title,
        body=summary or _QUESTION_PLACEHOLDER_BODY,
        options=options,
        extracted_text=summary or title,
    )


def _first_line(text: str) -> str:
    line = text.strip().splitlines()[0].strip()
    return line[:200]


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
