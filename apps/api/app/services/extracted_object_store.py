from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import ContentStatus, ExtractedObjectType
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource

_QUESTION_REQUIRED_KEYS = frozenset({"title", "body"})
_FLASHCARD_REQUIRED_KEYS = frozenset({"front", "back"})
_PROVENANCE_KEY = "provenance"


class ExtractedObjectStoreError(ValueError):
    """Raised when an extracted object cannot be stored."""


@dataclass(frozen=True, slots=True)
class ProvenanceData:
    """Source lineage persisted as FKs and a durable payload snapshot."""

    resource_id: int | None = None
    topic_job_id: int | None = None
    source_url: str | None = None
    source_title: str | None = None
    source_type: str | None = None
    source_license: str | None = None
    source_attribution: str | None = None
    source_author: str | None = None
    source_publisher: str | None = None


@dataclass(frozen=True, slots=True)
class StoreExtractedObjectInput:
    object_type: ExtractedObjectType
    payload_json: dict[str, Any]
    confidence_score: float | None = None
    quality_score: float | None = None
    extraction_method: str | None = None
    model_version: str | None = None
    provenance: ProvenanceData = field(default_factory=ProvenanceData)
    status: ContentStatus = ContentStatus.DRAFT


def store_extracted_object(
    session: Session,
    data: StoreExtractedObjectInput,
    *,
    commit: bool = False,
) -> ExtractedObject:
    """Persist a typed extracted object with payload, scores, method, and provenance.

    Column-level provenance: resource_id, topic_job_id, extraction_method, model_version.
    Payload embeds a ``provenance`` snapshot so lineage remains after Resource deletion.
    """
    payload = _normalized_payload(data.payload_json)
    _validate_typed_payload(data.object_type, payload)
    confidence = _clamp_score(data.confidence_score, field_name="confidence_score")
    quality = _clamp_score(data.quality_score, field_name="quality_score")
    provenance = _resolve_provenance(session, data.provenance)
    payload_with_provenance = _with_provenance_snapshot(payload, provenance)

    row = ExtractedObject(
        resource_id=provenance.resource_id,
        topic_job_id=provenance.topic_job_id,
        object_type=data.object_type,
        payload_json=payload_with_provenance,
        confidence_score=confidence,
        quality_score=quality,
        status=data.status,
        extraction_method=_blank_to_none(data.extraction_method),
        model_version=_blank_to_none(data.model_version),
    )
    session.add(row)
    session.flush()
    if commit:
        session.commit()
        session.refresh(row)
    return row


def store_extracted_objects(
    session: Session,
    items: list[StoreExtractedObjectInput],
    *,
    commit: bool = True,
) -> list[ExtractedObject]:
    if not items:
        raise ExtractedObjectStoreError("no extracted objects to store")
    rows = [store_extracted_object(session, item, commit=False) for item in items]
    if commit:
        session.commit()
        for row in rows:
            session.refresh(row)
    return rows


def get_stored_extracted_object(session: Session, extracted_object_id: int) -> ExtractedObject:
    row = session.scalar(
        select(ExtractedObject)
        .where(ExtractedObject.id == extracted_object_id)
        .options(
            joinedload(ExtractedObject.resource),
            joinedload(ExtractedObject.topic_job),
        ),
    )
    if row is None:
        raise LookupError(f"extracted object {extracted_object_id} not found")
    return row


def load_provenance_from_resource(
    resource: Resource,
    *,
    topic_job_id: int | None = None,
) -> ProvenanceData:
    return ProvenanceData(
        resource_id=resource.id,
        topic_job_id=topic_job_id,
        source_url=resource.url,
        source_title=resource.title,
        source_type=resource.source_type.value if resource.source_type is not None else None,
        source_license=resource.license,
        source_attribution=resource.attribution,
        source_author=resource.author,
        source_publisher=resource.publisher,
    )


def provenance_from_payload(payload: dict[str, Any]) -> ProvenanceData | None:
    raw = payload.get(_PROVENANCE_KEY)
    if not isinstance(raw, dict):
        return None
    return ProvenanceData(
        resource_id=_optional_int(raw.get("resource_id")),
        topic_job_id=_optional_int(raw.get("topic_job_id")),
        source_url=_optional_str(raw.get("source_url")),
        source_title=_optional_str(raw.get("source_title")),
        source_type=_optional_str(raw.get("source_type")),
        source_license=_optional_str(raw.get("source_license")),
        source_attribution=_optional_str(raw.get("source_attribution")),
        source_author=_optional_str(raw.get("source_author")),
        source_publisher=_optional_str(raw.get("source_publisher")),
    )


def _resolve_provenance(session: Session, provenance: ProvenanceData) -> ProvenanceData:
    if provenance.resource_id is None:
        return provenance

    resource = session.get(Resource, provenance.resource_id)
    if resource is None:
        raise ExtractedObjectStoreError(f"resource {provenance.resource_id} not found")

    loaded = load_provenance_from_resource(resource, topic_job_id=provenance.topic_job_id)
    # Explicit caller fields win over Resource defaults when provided.
    return ProvenanceData(
        resource_id=provenance.resource_id,
        topic_job_id=provenance.topic_job_id,
        source_url=_prefer(provenance.source_url, loaded.source_url),
        source_title=_prefer(provenance.source_title, loaded.source_title),
        source_type=_prefer(provenance.source_type, loaded.source_type),
        source_license=_prefer(provenance.source_license, loaded.source_license),
        source_attribution=_prefer(provenance.source_attribution, loaded.source_attribution),
        source_author=_prefer(provenance.source_author, loaded.source_author),
        source_publisher=_prefer(provenance.source_publisher, loaded.source_publisher),
    )


def _prefer(preferred: str | None, fallback: str | None) -> str | None:
    return preferred if preferred is not None else fallback


def _with_provenance_snapshot(
    payload: dict[str, Any],
    provenance: ProvenanceData,
) -> dict[str, Any]:
    snapshot = {
        key: value
        for key, value in {
            "resource_id": provenance.resource_id,
            "topic_job_id": provenance.topic_job_id,
            "source_url": provenance.source_url,
            "source_title": provenance.source_title,
            "source_type": provenance.source_type,
            "source_license": provenance.source_license,
            "source_attribution": provenance.source_attribution,
            "source_author": provenance.source_author,
            "source_publisher": provenance.source_publisher,
        }.items()
        if value is not None
    }
    merged = dict(payload)
    if snapshot:
        merged[_PROVENANCE_KEY] = snapshot
        # Convenience mirrors used by publish/review when no Resource join is available.
        if "source_url" not in merged and provenance.source_url is not None:
            merged["source_url"] = provenance.source_url
        if "source_title" not in merged and provenance.source_title is not None:
            merged["source_title"] = provenance.source_title
    return merged


def _validate_typed_payload(
    object_type: ExtractedObjectType,
    payload: dict[str, Any],
) -> None:
    if object_type is ExtractedObjectType.QUESTION:
        _require_non_blank_keys(payload, _QUESTION_REQUIRED_KEYS, object_type)
        return
    if object_type is ExtractedObjectType.FLASHCARD:
        _require_non_blank_keys(payload, _FLASHCARD_REQUIRED_KEYS, object_type)
        return
    if object_type is ExtractedObjectType.CONCEPT:
        if not _optional_str(payload.get("name")) and not _optional_str(payload.get("title")):
            raise ExtractedObjectStoreError(
                "concept payload requires non-blank name or title",
            )
        return
    if object_type is ExtractedObjectType.FORMULA:
        if not _optional_str(payload.get("formula")) and not _optional_str(payload.get("latex")):
            raise ExtractedObjectStoreError(
                "formula payload requires non-blank formula or latex",
            )
        return
    if object_type is ExtractedObjectType.EXAMPLE:
        if not _optional_str(payload.get("body")) and not _optional_str(payload.get("text")):
            raise ExtractedObjectStoreError(
                "example payload requires non-blank body or text",
            )


def _require_non_blank_keys(
    payload: dict[str, Any],
    keys: frozenset[str],
    object_type: ExtractedObjectType,
) -> None:
    missing = [key for key in sorted(keys) if not _optional_str(payload.get(key))]
    if missing:
        raise ExtractedObjectStoreError(
            f"{object_type.value} payload missing required fields: {', '.join(missing)}",
        )


def _normalized_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict) or not payload:
        raise ExtractedObjectStoreError("payload_json must be a non-empty object")
    return dict(payload)


def _clamp_score(value: float | None, *, field_name: str) -> float | None:
    if value is None:
        return None
    if value < 0 or value > 1:
        raise ExtractedObjectStoreError(f"{field_name} must be between 0 and 1")
    return float(value)


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def _optional_str(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _optional_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None
