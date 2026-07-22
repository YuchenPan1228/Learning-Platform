from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import ContentStatus, ExtractedObjectType, ResourceSourceType
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource

_MANUAL_IMPORT_METHOD = "manual:import"
_NOTE_SOURCE_TYPES = frozenset(
    {
        ResourceSourceType.MANUAL,
        ResourceSourceType.BOOK_NOTE,
    }
)


def create_extracted_draft_from_resource(session: Session, resource: Resource) -> ExtractedObject:
    extracted = ExtractedObject(
        resource_id=resource.id,
        object_type=_default_object_type(resource),
        payload_json=_build_import_payload(resource),
        confidence_score=1.0,
        quality_score=None,
        status=ContentStatus.DRAFT,
        extraction_method=_MANUAL_IMPORT_METHOD,
        model_version=None,
    )
    session.add(extracted)
    return extracted


def _default_object_type(_resource: Resource) -> ExtractedObjectType:
    return ExtractedObjectType.CONCEPT


def _build_import_payload(resource: Resource) -> dict[str, Any]:
    title = _blank_to_none(resource.title)
    summary = _blank_to_none(resource.summary)

    if resource.source_type == ResourceSourceType.URL:
        return _payload_for_url(resource, title=title, summary=summary)

    if resource.source_type in _NOTE_SOURCE_TYPES:
        return _payload_for_note(title=title, note_text=summary)

    if resource.source_type == ResourceSourceType.PDF:
        return _payload_for_pdf(title=title, summary=summary)

    name = title or "Imported resource"
    return {
        "name": name,
        "title": name,
        "extracted_text": summary,
        "summary": summary,
    }


def _payload_for_url(
    resource: Resource,
    *,
    title: str | None,
    summary: str | None,
) -> dict[str, Any]:
    display_title = title or resource.url or "Imported URL"
    extracted_text = summary or resource.url
    payload: dict[str, Any] = {
        "name": display_title,
        "title": display_title,
        "extracted_text": extracted_text,
    }
    if summary is not None:
        payload["summary"] = summary
        payload["definition"] = summary
    return payload


def _payload_for_note(*, title: str | None, note_text: str | None) -> dict[str, Any]:
    if note_text is None:
        raise ValueError("note import requires non-empty note text")

    display_title = title or _first_line(note_text) or "Imported note"
    return {
        "name": display_title,
        "title": display_title,
        "definition": note_text,
        "extracted_text": note_text,
        "summary": note_text,
    }


def _payload_for_pdf(*, title: str | None, summary: str | None) -> dict[str, Any]:
    if title is None:
        raise ValueError("pdf import requires a title")

    extracted_text = summary or title
    payload: dict[str, Any] = {
        "name": title,
        "title": title,
        "extracted_text": extracted_text,
    }
    if summary is not None:
        payload["summary"] = summary
        payload["definition"] = summary
    return payload


def _first_line(text: str) -> str:
    line = text.strip().splitlines()[0].strip()
    return line[:200]


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None
