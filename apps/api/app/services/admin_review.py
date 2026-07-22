from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.enums import ContentStatus, ExtractedObjectType
from app.models.extracted_object import ExtractedObject
from app.schemas.admin_review import (
    ExtractedObjectEdit,
    ExtractedObjectReviewRead,
    ResourceProvenanceRead,
)
from app.services.import_topic_validation import ImportTopicError, validate_import_topics

_REVIEW_OBJECT_TYPES = frozenset(
    {
        ExtractedObjectType.QUESTION,
        ExtractedObjectType.FLASHCARD,
    }
)


class ReviewQueueError(ValueError):
    """Raised when a review-queue mutation is invalid."""


def list_review_items(
    session: Session,
    *,
    status: ContentStatus = ContentStatus.DRAFT,
    object_type: ExtractedObjectType | None = None,
) -> list[ExtractedObjectReviewRead]:
    statement = (
        select(ExtractedObject)
        .options(joinedload(ExtractedObject.resource))
        .where(ExtractedObject.status == status)
        .order_by(ExtractedObject.created_at.asc(), ExtractedObject.id.asc())
    )
    if object_type is not None:
        statement = statement.where(ExtractedObject.object_type == object_type)

    rows = session.scalars(statement).unique().all()
    return [_to_review_read(row) for row in rows]


def get_review_item(session: Session, extracted_object_id: int) -> ExtractedObjectReviewRead:
    row = _get_extracted_object(session, extracted_object_id)
    return _to_review_read(row)


def edit_review_item(
    session: Session,
    extracted_object_id: int,
    payload: ExtractedObjectEdit,
) -> ExtractedObjectReviewRead:
    row = _get_extracted_object(session, extracted_object_id)
    if row.status is not ContentStatus.DRAFT:
        raise ReviewQueueError("only draft extracted objects can be edited")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise ReviewQueueError("no fields provided to edit")

    if "object_type" in updates and updates["object_type"] is not None:
        if updates["object_type"] not in _REVIEW_OBJECT_TYPES:
            raise ReviewQueueError("object_type must be question or flashcard")

    # Provenance fields (resource_id, topic_job_id, extraction_method, model_version)
    # are intentionally omitted from ExtractedObjectEdit and never mutated here.
    if "payload_json" in updates and updates["payload_json"] is not None:
        _validate_payload_topics(session, updates["payload_json"])
        row.payload_json = updates["payload_json"]
    if "object_type" in updates and updates["object_type"] is not None:
        row.object_type = updates["object_type"]
    if "confidence_score" in updates:
        row.confidence_score = updates["confidence_score"]
    if "quality_score" in updates:
        row.quality_score = updates["quality_score"]

    session.add(row)
    session.commit()
    return get_review_item(session, extracted_object_id)


def approve_review_item(
    session: Session,
    extracted_object_id: int,
) -> ExtractedObjectReviewRead:
    return _set_status(session, extracted_object_id, ContentStatus.APPROVED)


def reject_review_item(
    session: Session,
    extracted_object_id: int,
) -> ExtractedObjectReviewRead:
    return _set_status(session, extracted_object_id, ContentStatus.REJECTED)


def _set_status(
    session: Session,
    extracted_object_id: int,
    status: ContentStatus,
) -> ExtractedObjectReviewRead:
    row = _get_extracted_object(session, extracted_object_id)
    if row.status is not ContentStatus.DRAFT:
        raise ReviewQueueError("only draft extracted objects can change review status")

    row.status = status
    session.add(row)
    session.commit()
    return get_review_item(session, extracted_object_id)


def _get_extracted_object(session: Session, extracted_object_id: int) -> ExtractedObject:
    row = session.scalar(
        select(ExtractedObject)
        .options(joinedload(ExtractedObject.resource))
        .where(ExtractedObject.id == extracted_object_id)
    )
    if row is None:
        raise LookupError(f"extracted object {extracted_object_id} not found")
    return row


def _to_review_read(row: ExtractedObject) -> ExtractedObjectReviewRead:
    resource = None
    if row.resource is not None:
        resource = ResourceProvenanceRead.model_validate(row.resource)
    return ExtractedObjectReviewRead(
        id=row.id,
        resource_id=row.resource_id,
        topic_job_id=row.topic_job_id,
        object_type=row.object_type,
        payload_json=row.payload_json,
        confidence_score=row.confidence_score,
        quality_score=row.quality_score,
        duplicate_cluster_id=row.duplicate_cluster_id,
        status=row.status,
        extraction_method=row.extraction_method,
        model_version=row.model_version,
        created_at=row.created_at,
        updated_at=row.updated_at,
        resource=resource,
    )


def _validate_payload_topics(session: Session, payload_json: dict[str, object]) -> None:
    topic_slug = payload_json.get("topic_slug")
    if topic_slug is None:
        return
    if not isinstance(topic_slug, str) or not topic_slug.strip():
        raise ReviewQueueError("topic_slug must be a non-empty string")

    subtopic_slug = payload_json.get("subtopic_slug")
    normalized_subtopic = None
    if subtopic_slug is not None:
        if not isinstance(subtopic_slug, str) or not subtopic_slug.strip():
            raise ReviewQueueError("subtopic_slug must be a non-empty string when provided")
        normalized_subtopic = subtopic_slug.strip()

    try:
        validate_import_topics(
            session,
            topic_slug=topic_slug.strip(),
            subtopic_slug=normalized_subtopic,
        )
    except ImportTopicError as exc:
        raise ReviewQueueError(str(exc)) from exc
