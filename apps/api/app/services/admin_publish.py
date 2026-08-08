from __future__ import annotations

from copy import deepcopy
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.dedup.detection import DuplicateMatch, find_duplicate_matches
from app.dedup.fingerprints import apply_question_fingerprints
from app.models.concept import Concept
from app.models.enums import (
    ContentStatus,
    Difficulty,
    DuplicateMatchType,
    ExtractedObjectType,
)
from app.models.extracted_object import ExtractedObject
from app.models.flashcard import Flashcard
from app.models.question import Question
from app.models.topic import Topic
from app.schemas.admin_publish import PublishedObjectRef, PublishExtractedObjectResponse
from app.schemas.duplicate import DuplicateMatchRead
from app.seeds.utils import slugify


class PublishError(ValueError):
    """Raised when an extracted object cannot be published."""


class PublishDuplicateError(PublishError):
    """Raised when publishing would create an exact duplicate question."""

    def __init__(self, message: str, *, matches: list[DuplicateMatch]) -> None:
        super().__init__(message)
        self.matches = matches


_PUBLISHED_KEY = "published"
_DEFAULT_EXTRACTION_PREFIX = "ingestion:extracted_object"
_EXACT_DUPLICATE_TYPES = {
    DuplicateMatchType.EXACT_RAW,
    DuplicateMatchType.EXACT_NORMALIZED,
}


def publish_extracted_object(
    session: Session,
    extracted_object_id: int,
) -> PublishExtractedObjectResponse:
    extracted = _get_extracted_object(session, extracted_object_id)
    if extracted.status is not ContentStatus.APPROVED:
        raise PublishError("only approved extracted objects can be published")
    if _published_ref(extracted.payload_json) is not None:
        raise PublishError("extracted object has already been published")

    topic_id = _resolve_topic_id(session, extracted)
    subtopic_id = _resolve_subtopic_id(session, extracted)
    provenance = _provenance_fields(extracted)

    if extracted.object_type is ExtractedObjectType.QUESTION:
        published, duplicate_warnings = _publish_question(
            session,
            extracted,
            topic_id=topic_id,
            subtopic_id=subtopic_id,
            provenance=provenance,
        )
        published_ref = PublishedObjectRef(kind="question", id=published.id)
    elif extracted.object_type in {
        ExtractedObjectType.CONCEPT,
        ExtractedObjectType.FORMULA,
        ExtractedObjectType.EXAMPLE,
    }:
        concept = _publish_concept(session, extracted, topic_id=topic_id)
        published_ref = PublishedObjectRef(kind="concept", id=concept.id)
        duplicate_warnings = []
    elif extracted.object_type is ExtractedObjectType.FLASHCARD:
        raise PublishError(
            "flashcard publishing is disabled; reject leftover flashcard drafts "
            "or re-import as questions",
        )
    else:
        raise PublishError(f"unsupported extracted object type: {extracted.object_type.value}")

    extracted.payload_json = _with_published_ref(extracted.payload_json, published_ref)
    session.add(extracted)
    session.commit()

    return PublishExtractedObjectResponse(
        extracted_object_id=extracted.id,
        object_type=extracted.object_type,
        published=published_ref,
        duplicate_warnings=duplicate_warnings,
    )


def _publish_question(
    session: Session,
    extracted: ExtractedObject,
    *,
    topic_id: int,
    subtopic_id: int | None,
    provenance: dict[str, Any],
) -> tuple[Question, list[DuplicateMatchRead]]:
    payload = extracted.payload_json
    title = _require_string(payload, "title", fallback_keys=("name",))
    body = _require_string(payload, "body", fallback_keys=("text", "question"))

    matches = find_duplicate_matches(session, title=title, body=body)
    exact_matches = [match for match in matches if match.match_type in _EXACT_DUPLICATE_TYPES]
    if exact_matches:
        raise PublishDuplicateError(
            "question matches an existing question exactly; refusing to publish duplicate",
            matches=exact_matches,
        )

    question = Question(
        title=title,
        body=body,
        canonical_solution=_optional_string(payload, "canonical_solution", "solution"),
        short_answer=_optional_string(payload, "short_answer", "answer"),
        difficulty=_parse_difficulty(payload.get("difficulty")),
        estimated_time_seconds=_optional_int(payload, "estimated_time_seconds"),
        topic_id=topic_id,
        subtopic_id=subtopic_id,
        company_hint=_optional_string(payload, "company_hint"),
        quality_score=extracted.quality_score,
        expected_solution_pattern=_optional_string(payload, "expected_solution_pattern"),
        common_mistakes=_optional_string_list(payload, "common_mistakes"),
        prerequisites=_optional_string_list(payload, "prerequisites"),
        generated_from_id=_optional_int(payload, "generated_from_question_id"),
        status=ContentStatus.APPROVED,
        **provenance,
    )
    apply_question_fingerprints(question)
    session.add(question)
    session.commit()
    session.refresh(question)

    duplicate_warnings = [
        _duplicate_match_read(match)
        for match in matches
        if match.match_type not in _EXACT_DUPLICATE_TYPES
    ]
    return question, duplicate_warnings


def _publish_concept(session: Session, extracted: ExtractedObject, *, topic_id: int) -> Concept:
    payload = extracted.payload_json
    if extracted.object_type is ExtractedObjectType.FORMULA:
        name = _optional_string(payload, "name", "concept", "title")
        if name is None:
            latex = _optional_string(payload, "latex", "formula")
            if latex is None:
                raise PublishError("formula draft requires name or latex")
            name = latex[:200]
        formula = _optional_string(payload, "latex", "formula")
        definition = _optional_string(payload, "definition", "summary")
        worked_example = None
    elif extracted.object_type is ExtractedObjectType.EXAMPLE:
        name = _require_string(payload, "name", fallback_keys=("title", "concept"))
        worked_example = _require_string(payload, "example", fallback_keys=("body", "text"))
        formula = _optional_string(payload, "formula", "latex")
        definition = _optional_string(payload, "definition", "summary")
    else:
        name = _require_string(payload, "name", fallback_keys=("title",))
        definition = _optional_string(payload, "definition", "summary")
        formula = _optional_string(payload, "formula", "latex")
        worked_example = _optional_string(payload, "worked_example", "example")

    base_slug = _optional_string(payload, "slug") or slugify(name)
    slug = _unique_concept_slug(session, base_slug)

    concept = Concept(
        slug=slug,
        name=name,
        topic_id=topic_id,
        definition=definition,
        formula=formula,
        intuition=_optional_string(payload, "intuition"),
        worked_example=worked_example,
        common_mistakes=_optional_string(payload, "common_mistakes"),
        interview_tips=_optional_string(payload, "interview_tips"),
        prerequisites=_optional_string(payload, "prerequisites"),
    )
    session.add(concept)
    session.commit()
    session.refresh(concept)
    return concept


def _publish_flashcard(
    session: Session,
    extracted: ExtractedObject,
    *,
    topic_id: int,
    provenance: dict[str, Any],
) -> Flashcard:
    payload = extracted.payload_json
    front = _require_string(payload, "front", fallback_keys=("title", "question"))
    back = _require_string(payload, "back", fallback_keys=("answer", "definition"))

    flashcard = Flashcard(
        front=front,
        back=back,
        topic_id=topic_id,
        source_id=provenance.get("source_id"),
        difficulty=_parse_optional_difficulty(payload.get("difficulty")),
    )
    session.add(flashcard)
    session.commit()
    session.refresh(flashcard)
    return flashcard


def _get_extracted_object(session: Session, extracted_object_id: int) -> ExtractedObject:
    extracted = session.scalar(
        select(ExtractedObject)
        .options(joinedload(ExtractedObject.resource), joinedload(ExtractedObject.topic_job))
        .where(ExtractedObject.id == extracted_object_id)
    )
    if extracted is None:
        raise LookupError(f"extracted object {extracted_object_id} not found")
    return extracted


def _resolve_topic_id(session: Session, extracted: ExtractedObject) -> int:
    if extracted.topic_job is not None:
        return extracted.topic_job.topic_id

    topic_slug = _optional_string(extracted.payload_json, "topic_slug")
    if topic_slug is not None:
        topic_id = session.scalar(select(Topic.id).where(Topic.slug == topic_slug))
        if topic_id is not None:
            return topic_id
        raise PublishError(f"unknown topic_slug '{topic_slug}'")

    raise PublishError("topic is required via topic_job_id or topic_slug in payload")


def _resolve_subtopic_id(session: Session, extracted: ExtractedObject) -> int | None:
    subtopic_slug = _optional_string(extracted.payload_json, "subtopic_slug")
    if subtopic_slug is None:
        return None
    subtopic_id = session.scalar(select(Topic.id).where(Topic.slug == subtopic_slug))
    if subtopic_id is None:
        raise PublishError(f"unknown subtopic_slug '{subtopic_slug}'")
    return subtopic_id


def _provenance_fields(extracted: ExtractedObject) -> dict[str, Any]:
    resource = extracted.resource
    extraction_method = (
        extracted.extraction_method or f"{_DEFAULT_EXTRACTION_PREFIX}:{extracted.id}"
    )
    fields: dict[str, Any] = {
        "extraction_method": extraction_method,
        "model_version": extracted.model_version,
    }
    if resource is not None:
        fields.update(
            {
                "source_id": resource.id,
                "source_url": resource.url,
                "source_title": resource.title,
                "source_license": resource.license,
                "source_attribution": resource.attribution,
            }
        )
    return fields


def _published_ref(payload: dict[str, Any]) -> PublishedObjectRef | None:
    published = payload.get(_PUBLISHED_KEY)
    if not isinstance(published, dict):
        return None
    kind = published.get("kind")
    object_id = published.get("id")
    if kind in {"concept", "question", "flashcard"} and isinstance(object_id, int):
        return PublishedObjectRef(kind=kind, id=object_id)
    return None


def _with_published_ref(
    payload: dict[str, Any],
    published: PublishedObjectRef,
) -> dict[str, Any]:
    updated = deepcopy(payload)
    updated[_PUBLISHED_KEY] = published.model_dump()
    return updated


def _unique_concept_slug(session: Session, base_slug: str) -> str:
    slug = base_slug[:120]
    if session.scalar(select(Concept.id).where(Concept.slug == slug)) is None:
        return slug

    suffix = 2
    while suffix < 10_000:
        candidate = f"{base_slug[:110]}-{suffix}"
        if session.scalar(select(Concept.id).where(Concept.slug == candidate)) is None:
            return candidate
        suffix += 1

    raise PublishError("unable to allocate a unique concept slug")


def _duplicate_match_read(match: DuplicateMatch) -> DuplicateMatchRead:
    return DuplicateMatchRead(
        question_id=match.question_id,
        title=match.title,
        match_type=match.match_type,
        similarity_score=match.similarity_score,
    )


def _require_string(
    payload: dict[str, Any],
    key: str,
    *,
    fallback_keys: tuple[str, ...] = (),
) -> str:
    value = _optional_string(payload, key, *fallback_keys)
    if value is None:
        keys = ", ".join((key, *fallback_keys))
        raise PublishError(f"payload is missing required text field ({keys})")
    return value


def _optional_string(payload: dict[str, Any], key: str, *fallback_keys: str) -> str | None:
    for candidate_key in (key, *fallback_keys):
        value = payload.get(candidate_key)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped:
                return stripped
    return None


def _optional_int(payload: dict[str, Any], key: str) -> int | None:
    value = payload.get(key)
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _optional_string_list(payload: dict[str, Any], key: str) -> list[str] | None:
    value = payload.get(key)
    if not isinstance(value, list):
        return None
    items = [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return items or None


def _parse_difficulty(value: Any) -> Difficulty:
    if isinstance(value, str):
        try:
            return Difficulty(value.lower())
        except ValueError:
            return Difficulty.MEDIUM
    return Difficulty.MEDIUM


def _parse_optional_difficulty(value: Any) -> Difficulty | None:
    if not isinstance(value, str):
        return None
    try:
        return Difficulty(value.lower())
    except ValueError:
        return None
