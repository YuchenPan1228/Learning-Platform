from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from app.dedup.text import text_hash
from app.models.enums import ContentStatus, ExtractedObjectType, ResourceSourceType
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.models.topic import Topic
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfMetadataImportCreate,
    QuestionImportCreate,
    UrlImportCreate,
)
from app.services.admin_import import (
    import_note_resource,
    import_pdf_metadata_resource,
    import_question_resource,
    import_url_resource,
)
from app.services.import_extracted_draft import (
    DraftImportOptions,
    create_extracted_draft_from_resource,
)
from fastapi.testclient import TestClient
from pydantic import ValidationError

_TOPIC_SLUG = "probability"


def _attach_persisted_fields(row: Resource, resource_id: int) -> None:
    row.id = resource_id
    now = datetime.now(UTC)
    row.created_at = now
    row.updated_at = now


def _attach_extracted_fields(row: ExtractedObject, extracted_id: int) -> None:
    row.id = extracted_id
    now = datetime.now(UTC)
    row.created_at = now
    row.updated_at = now


def _mock_import_session(
    session: MagicMock,
    *,
    resource_id: int = 1,
    extracted_id: int = 10,
) -> None:
    topic = Topic(
        id=1,
        slug=_TOPIC_SLUG,
        name="Probability",
        order_index=0,
        parent_topic_id=None,
    )
    session.scalar.return_value = topic

    flush_count = {"value": 0}

    def refresh(row: object) -> None:
        if isinstance(row, Resource):
            _attach_persisted_fields(row, resource_id)
        elif isinstance(row, ExtractedObject):
            _attach_extracted_fields(row, extracted_id)

    def flush() -> None:
        flush_count["value"] += 1
        if flush_count["value"] == 1:
            for call in session.add.call_args_list:
                row = call.args[0]
                if isinstance(row, Resource):
                    _attach_persisted_fields(row, resource_id)

    session.refresh.side_effect = refresh
    session.flush.side_effect = flush


def test_import_url_resource_creates_question_draft_without_crawling() -> None:
    session = MagicMock()
    _mock_import_session(session)

    result = import_url_resource(
        session,
        UrlImportCreate(
            url="https://example.com/bayes",
            title="Bayes notes",
            license="CC-BY-4.0",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.QUESTION,
        ),
    )

    assert session.add.call_count == 2
    session.flush.assert_called_once()
    session.commit.assert_called_once()
    saved = session.add.call_args_list[0].args[0]
    assert isinstance(saved, Resource)
    assert saved.source_type is ResourceSourceType.URL
    assert saved.url == "https://example.com/bayes"
    assert saved.title == "Bayes notes"
    assert saved.license == "CC-BY-4.0"
    assert saved.status is ContentStatus.DRAFT
    assert saved.raw_text_hash == text_hash("https://example.com/bayes")
    extracted = session.add.call_args_list[1].args[0]
    assert isinstance(extracted, ExtractedObject)
    assert extracted.object_type is ExtractedObjectType.QUESTION
    assert extracted.resource_id == 1
    assert extracted.payload_json["topic_slug"] == _TOPIC_SLUG
    assert extracted.extraction_method == "manual:import"
    assert result.id == 1
    assert result.extracted_object_id == 10
    assert result.source_type is ResourceSourceType.URL


def test_import_note_resource_stores_text_as_question_body() -> None:
    session = MagicMock()
    _mock_import_session(session, resource_id=2, extracted_id=11)

    result = import_note_resource(
        session,
        NoteImportCreate(
            note_text="  Bayes theorem relates P(A|B) to P(B|A).  ",
            title="Bayes note",
            source_type=ResourceSourceType.BOOK_NOTE,
            attribution="Handwritten study notes",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.QUESTION,
        ),
    )

    saved = session.add.call_args_list[0].args[0]
    assert saved.source_type is ResourceSourceType.BOOK_NOTE
    assert saved.summary == "Bayes theorem relates P(A|B) to P(B|A)."
    assert saved.raw_text_hash == text_hash("Bayes theorem relates P(A|B) to P(B|A).")
    assert saved.url is None
    assert saved.status is ContentStatus.DRAFT
    extracted = session.add.call_args_list[1].args[0]
    assert extracted.payload_json["body"] == "Bayes theorem relates P(A|B) to P(B|A)."
    assert extracted.payload_json["topic_slug"] == _TOPIC_SLUG
    assert result.summary == "Bayes theorem relates P(A|B) to P(B|A)."
    assert result.extracted_object_id == 11


def test_note_import_rejects_non_note_source_type() -> None:
    with pytest.raises(ValidationError):
        NoteImportCreate(
            note_text="text",
            source_type=ResourceSourceType.URL,
            topic_slug=_TOPIC_SLUG,
        )


def test_flashcard_note_import_requires_front_title() -> None:
    with pytest.raises(ValidationError):
        NoteImportCreate(
            note_text="answer text",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.FLASHCARD,
        )


def test_import_pdf_metadata_stores_path_without_parsing() -> None:
    session = MagicMock()
    _mock_import_session(session, resource_id=3, extracted_id=12)

    result = import_pdf_metadata_resource(
        session,
        PdfMetadataImportCreate(
            title="Interview Math PDF",
            file_path="/Users/me/docs/interview-math.pdf",
            publisher="Self",
            license="All rights reserved",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.FLASHCARD,
        ),
    )

    saved = session.add.call_args_list[0].args[0]
    assert saved.source_type is ResourceSourceType.PDF
    assert saved.url == "/Users/me/docs/interview-math.pdf"
    assert saved.title == "Interview Math PDF"
    assert saved.publisher == "Self"
    assert saved.status is ContentStatus.DRAFT
    assert saved.raw_text_hash == text_hash("/Users/me/docs/interview-math.pdf")
    extracted = session.add.call_args_list[1].args[0]
    assert extracted.object_type is ExtractedObjectType.FLASHCARD
    assert extracted.payload_json["front"] == "Interview Math PDF"
    assert result.id == 3
    assert result.extracted_object_id == 12


def test_import_question_resource_creates_ready_to_review_draft() -> None:
    session = MagicMock()
    _mock_import_session(session, resource_id=4, extracted_id=13)

    result = import_question_resource(
        session,
        QuestionImportCreate(
            title="Bayes follow-up",
            body="Given P(A)=0.3 and P(B|A)=0.5, what is P(A and B)?",
            short_answer="0.15",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.QUESTION,
        ),
    )

    extracted = session.add.call_args_list[1].args[0]
    assert extracted.object_type is ExtractedObjectType.QUESTION
    assert extracted.payload_json["title"] == "Bayes follow-up"
    assert extracted.payload_json["short_answer"] == "0.15"
    assert result.extracted_object_id == 13


def test_create_extracted_draft_from_resource_builds_question_payload() -> None:
    resource = Resource(
        source_type=ResourceSourceType.MANUAL,
        title="Bayes note",
        summary="P(A|B) = P(B|A)P(A)/P(B)",
        status=ContentStatus.DRAFT,
    )
    resource.id = 5
    session = MagicMock()

    extracted = create_extracted_draft_from_resource(
        session,
        resource,
        options=DraftImportOptions(
            object_type=ExtractedObjectType.QUESTION,
            topic_slug=_TOPIC_SLUG,
        ),
    )

    session.add.assert_called_once_with(extracted)
    assert extracted.resource_id == 5
    assert extracted.object_type is ExtractedObjectType.QUESTION
    assert extracted.payload_json["title"] == "Bayes note"
    assert extracted.payload_json["body"] == "P(A|B) = P(B|A)P(A)/P(B)"
    assert extracted.payload_json["topic_slug"] == _TOPIC_SLUG
    assert extracted.extraction_method == "manual:import"


@pytest.mark.integration
def test_admin_import_endpoints_create_resources(
    seeded_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    url_response = client.post(
        "/admin/import/url",
        json={
            "url": "https://example.com/conditional-probability",
            "title": "Conditional probability",
            "topic_slug": _TOPIC_SLUG,
            "object_type": "question",
        },
    )
    assert url_response.status_code == 200
    url_body = url_response.json()
    assert url_body["source_type"] == "url"
    assert url_body["status"] == "draft"
    assert url_body["url"] == "https://example.com/conditional-probability"

    note_response = client.post(
        "/admin/import/note",
        json={
            "note_text": "Independence means P(A and B) = P(A)P(B).",
            "title": "Independence",
            "source_type": "manual",
            "topic_slug": _TOPIC_SLUG,
            "object_type": "flashcard",
        },
    )
    assert note_response.status_code == 200
    note_body = note_response.json()
    assert note_body["source_type"] == "manual"
    assert note_body["summary"].startswith("Independence means")

    question_response = client.post(
        "/admin/import/question",
        json={
            "title": "Dice parity",
            "body": "You roll two fair dice. What is P(sum is even)?",
            "topic_slug": _TOPIC_SLUG,
            "object_type": "question",
        },
    )
    assert question_response.status_code == 200
    question_body = question_response.json()

    pdf_response = client.post(
        "/admin/import/pdf",
        json={
            "title": "Local PDF",
            "file_path": "/tmp/quant-notes.pdf",
            "author": "Yuchen",
            "topic_slug": _TOPIC_SLUG,
            "object_type": "question",
        },
    )
    assert pdf_response.status_code == 200
    pdf_body = pdf_response.json()
    assert pdf_body["source_type"] == "pdf"
    assert pdf_body["url"] == "/tmp/quant-notes.pdf"
    assert pdf_body["author"] == "Yuchen"
    assert isinstance(pdf_body["extracted_object_id"], int)

    review_response = client.get("/admin/review")
    assert review_response.status_code == 200
    review_items = review_response.json()["items"]
    extracted_ids = {item["id"] for item in review_items}
    assert url_body["extracted_object_id"] in extracted_ids
    assert note_body["extracted_object_id"] in extracted_ids
    assert question_body["extracted_object_id"] in extracted_ids
    assert pdf_body["extracted_object_id"] in extracted_ids

    url_draft = next(item for item in review_items if item["id"] == url_body["extracted_object_id"])
    assert url_draft["status"] == "draft"
    assert url_draft["object_type"] == "question"
    assert url_draft["payload_json"]["topic_slug"] == _TOPIC_SLUG
    assert url_draft["resource"]["id"] == url_body["id"]
    assert url_draft["extraction_method"] == "manual:import"

    flashcard_draft = next(
        item for item in review_items if item["id"] == note_body["extracted_object_id"]
    )
    assert flashcard_draft["object_type"] == "flashcard"
    assert flashcard_draft["payload_json"]["front"] == "Independence"

    invalid_topic = client.post(
        "/admin/import/question",
        json={
            "title": "Bad topic",
            "body": "Question body",
            "topic_slug": "not-a-real-topic",
            "object_type": "question",
        },
    )
    assert invalid_topic.status_code == 400
