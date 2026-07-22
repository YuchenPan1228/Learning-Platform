from sqlalchemy.orm import Session

from app.dedup.text import text_hash
from app.models.enums import ContentStatus, ResourceSourceType
from app.models.resource import Resource
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfMetadataImportCreate,
    QuestionImportCreate,
    ResourceImportRead,
    UrlImportCreate,
)
from app.services.import_extracted_draft import (
    DraftImportOptions,
    QuestionDraftFields,
    create_extracted_draft_from_resource,
)
from app.services.import_topic_validation import ImportTopicError, validate_import_topics

_NOTE_SOURCE_TYPES = frozenset(
    {
        ResourceSourceType.MANUAL,
        ResourceSourceType.BOOK_NOTE,
    }
)


def import_url_resource(session: Session, payload: UrlImportCreate) -> ResourceImportRead:
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
    return _persist_resource(session, resource, options=draft_options)


def import_note_resource(session: Session, payload: NoteImportCreate) -> ResourceImportRead:
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
    return _persist_resource(session, resource, options=draft_options)


def import_question_resource(
    session: Session,
    payload: QuestionImportCreate,
) -> ResourceImportRead:
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
    return _persist_resource(
        session,
        resource,
        options=draft_options,
        question_fields=question_fields,
    )


def import_pdf_metadata_resource(
    session: Session,
    payload: PdfMetadataImportCreate,
) -> ResourceImportRead:
    draft_options = _draft_options_from_payload(payload)
    _validate_topics(session, draft_options)

    title = payload.title.strip()
    if not title:
        raise ValueError("title must not be blank")

    file_path = _blank_to_none(payload.file_path)
    fingerprint = file_path or title
    resource = Resource(
        source_type=ResourceSourceType.PDF,
        url=file_path,
        title=title,
        author=_blank_to_none(payload.author),
        publisher=_blank_to_none(payload.publisher),
        license=_blank_to_none(payload.license),
        attribution=_blank_to_none(payload.attribution),
        summary=_blank_to_none(payload.summary),
        raw_text_hash=text_hash(fingerprint),
        status=ContentStatus.DRAFT,
    )
    return _persist_resource(session, resource, options=draft_options)


def _persist_resource(
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
        update={"extracted_object_id": extracted.id},
    )


def _draft_options_from_payload(
    payload: UrlImportCreate | NoteImportCreate | QuestionImportCreate | PdfMetadataImportCreate,
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


def _blank_to_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


__all__ = ["ImportTopicError", "import_note_resource", "import_pdf_metadata_resource",
           "import_question_resource", "import_url_resource"]
