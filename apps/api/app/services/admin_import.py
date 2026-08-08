from pathlib import Path

from sqlalchemy.orm import Session

from app.ai.provider import AIProvider
from app.dedup.text import text_hash
from app.models.enums import ContentStatus, ResourceSourceType, SourcePolicyDecision
from app.models.resource import Resource
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfImportCreate,
    QuestionImportCreate,
    ResourceImportRead,
    UrlImportCreate,
)
from app.services.ai_structured_extraction import (
    AIStructuredExtractionError,
    extract_structured_drafts_from_resource,
)
from app.services.import_extracted_draft import (
    DraftImportOptions,
    QuestionDraftFields,
    create_extracted_draft_from_resource,
)
from app.services.import_topic_validation import ImportTopicError, validate_import_topics
from app.services.pdf_upload import store_pdf_upload
from app.services.source_extraction import SourceExtractionError
from app.services.source_policy import check_resource_policy

_NOTE_SOURCE_TYPES = frozenset(
    {
        ResourceSourceType.MANUAL,
        ResourceSourceType.BOOK_NOTE,
    }
)


class ImportPolicyError(ValueError):
    """Raised when source policy denies automatic extraction for an import."""


class ImportExtractionError(ValueError):
    """Raised when page/PDF/note text extraction or AI drafting fails."""


def import_url_resource(
    session: Session,
    payload: UrlImportCreate,
    *,
    provider: AIProvider,
) -> ResourceImportRead:
    draft_options = _draft_options_from_payload(payload)
    _validate_topics(session, draft_options)

    url = str(payload.url)
    resource = Resource(
        source_type=ResourceSourceType.URL,
        url=url,
        title=_blank_to_none(payload.title),
        author=_blank_to_none(payload.author),
        license=_blank_to_none(payload.license),
        attribution=_blank_to_none(payload.attribution),
        summary=_blank_to_none(payload.summary),
        raw_text_hash=text_hash(url),
        status=ContentStatus.DRAFT,
    )
    return _persist_with_ai_extraction(
        session,
        resource,
        options=draft_options,
        provider=provider,
    )


def import_note_resource(
    session: Session,
    payload: NoteImportCreate,
    *,
    provider: AIProvider,
) -> ResourceImportRead:
    if payload.source_type not in _NOTE_SOURCE_TYPES:
        raise ValueError(
            f"note import source_type must be manual or book_note, got {payload.source_type.value}",
        )

    note_text = payload.note_text.strip()
    if not note_text:
        raise ValueError("note_text must not be blank")

    draft_options = _draft_options_from_payload(payload)
    _validate_topics(session, draft_options)

    resource = Resource(
        source_type=payload.source_type,
        title=_blank_to_none(payload.title),
        author=_blank_to_none(payload.author),
        license=_blank_to_none(payload.license),
        attribution=_blank_to_none(payload.attribution),
        summary=note_text,
        raw_text_hash=text_hash(note_text),
        status=ContentStatus.DRAFT,
    )
    return _persist_with_ai_extraction(
        session,
        resource,
        options=draft_options,
        provider=provider,
    )


def import_question_resource(
    session: Session,
    payload: QuestionImportCreate,
) -> ResourceImportRead:
    """Structured question paste still creates a single ready-to-review draft (no AI)."""
    draft_options = _draft_options_from_payload(payload)
    _validate_topics(session, draft_options)

    body = payload.body.strip()
    title = payload.title.strip()
    if not body:
        raise ValueError("body must not be blank")
    if not title:
        raise ValueError("title must not be blank")

    resource = Resource(
        source_type=ResourceSourceType.MANUAL,
        title=title,
        author=_blank_to_none(payload.author),
        license=_blank_to_none(payload.license),
        attribution=_blank_to_none(payload.attribution),
        summary=body,
        raw_text_hash=text_hash(f"{title}\n{body}"),
        status=ContentStatus.DRAFT,
    )
    question_fields = QuestionDraftFields(
        title=title,
        body=body,
        short_answer=_blank_to_none(payload.short_answer),
        difficulty=payload.difficulty,
    )
    return _persist_manual_resource(
        session,
        resource,
        options=draft_options,
        question_fields=question_fields,
    )


def import_pdf_resource(
    session: Session,
    payload: PdfImportCreate,
    *,
    provider: AIProvider,
    filename: str | None,
    content_type: str | None,
    content: bytes,
) -> ResourceImportRead:
    draft_options = _draft_options_from_payload(payload)
    _validate_topics(session, draft_options)

    stored = store_pdf_upload(
        filename=filename,
        content_type=content_type,
        content=content,
    )
    title = _blank_to_none(payload.title) or _title_from_filename(stored.original_filename)
    resource = Resource(
        source_type=ResourceSourceType.PDF,
        url=stored.relative_path,
        title=title,
        summary=_blank_to_none(payload.summary),
        raw_text_hash=stored.content_sha256,
        status=ContentStatus.DRAFT,
    )
    return _persist_with_ai_extraction(
        session,
        resource,
        options=draft_options,
        provider=provider,
    )


def _persist_with_ai_extraction(
    session: Session,
    resource: Resource,
    *,
    options: DraftImportOptions,
    provider: AIProvider,
) -> ResourceImportRead:
    session.add(resource)
    session.flush()

    policy = check_resource_policy(resource)
    if policy.decision is SourcePolicyDecision.DENY:
        session.rollback()
        reasons = "; ".join(policy.reasons) if policy.reasons else "source policy denied"
        raise ImportPolicyError(f"source policy denied import: {reasons}")

    try:
        extraction = extract_structured_drafts_from_resource(
            session,
            provider,
            resource,
            topic_slug_hint=options.topic_slug,
            subtopic_slug_hint=options.subtopic_slug,
            commit=False,
        )
    except (AIStructuredExtractionError, SourceExtractionError) as exc:
        session.rollback()
        raise ImportExtractionError(str(exc)) from exc

    if extraction.source_title and not resource.title:
        resource.title = extraction.source_title
    # Keep pasted note body intact; only fill missing URL/PDF summaries from AI.
    if extraction.summary and resource.source_type in {
        ResourceSourceType.URL,
        ResourceSourceType.PDF,
    }:
        if not resource.summary:
            resource.summary = extraction.summary

    draft_ids = [draft.id for draft in extraction.drafts if draft.id is not None]
    if not draft_ids:
        session.rollback()
        raise ImportExtractionError("AI extraction produced no review drafts")

    session.add(resource)
    session.commit()
    session.refresh(resource)

    return ResourceImportRead.model_validate(resource).model_copy(
        update={
            "extracted_object_id": draft_ids[0],
            "extracted_object_ids": draft_ids,
            "draft_count": len(draft_ids),
            "extraction_method": extraction.extraction_method,
            "policy_decision": policy.decision.value,
        },
    )


def _persist_manual_resource(
    session: Session,
    resource: Resource,
    *,
    options: DraftImportOptions,
    question_fields: QuestionDraftFields | None = None,
) -> ResourceImportRead:
    session.add(resource)
    session.flush()
    extracted = create_extracted_draft_from_resource(
        session,
        resource,
        options=options,
        question_fields=question_fields,
    )
    session.commit()
    session.refresh(resource)
    session.refresh(extracted)
    return ResourceImportRead.model_validate(resource).model_copy(
        update={
            "extracted_object_id": extracted.id,
            "extracted_object_ids": [extracted.id],
            "draft_count": 1,
            "extraction_method": extracted.extraction_method,
            "policy_decision": None,
        },
    )


def _draft_options_from_payload(
    payload: UrlImportCreate | NoteImportCreate | QuestionImportCreate | PdfImportCreate,
) -> DraftImportOptions:
    return DraftImportOptions(
        object_type=payload.object_type,
        topic_slug=payload.topic_slug.strip(),
        subtopic_slug=_blank_to_none(payload.subtopic_slug),
    )


def _validate_topics(session: Session, options: DraftImportOptions) -> None:
    validate_import_topics(
        session,
        topic_slug=options.topic_slug,
        subtopic_slug=options.subtopic_slug,
    )


def _title_from_filename(filename: str) -> str:
    stem = Path(filename).stem.strip() or "Uploaded PDF"
    return stem[:300]


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


__all__ = [
    "ImportExtractionError",
    "ImportPolicyError",
    "ImportTopicError",
    "import_note_resource",
    "import_pdf_resource",
    "import_question_resource",
    "import_url_resource",
]
