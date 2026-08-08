from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from app.dedup.text import text_hash
from app.models.enums import ContentStatus, ExtractedObjectType, ResourceSourceType
from app.models.extracted_object import ExtractedObject
from app.models.resource import Resource
from app.models.topic import Topic
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfImportCreate,
    QuestionImportCreate,
    UrlImportCreate,
)
from app.services.admin_import import (
    import_note_resource,
    import_pdf_resource,
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

    def refresh(row: object) -> None:
        if isinstance(row, Resource):
            _attach_persisted_fields(row, resource_id)
        elif isinstance(row, ExtractedObject):
            _attach_extracted_fields(row, extracted_id)

    def flush() -> None:
        for call in session.add.call_args_list:
            row = call.args[0]
            if isinstance(row, Resource) and getattr(row, "id", None) is None:
                _attach_persisted_fields(row, resource_id)
            elif isinstance(row, ExtractedObject) and getattr(row, "id", None) is None:
                _attach_extracted_fields(row, extracted_id)

    def get(model: object, object_id: object) -> Resource | None:
        if model is Resource:
            for call in session.add.call_args_list:
                row = call.args[0]
                if isinstance(row, Resource) and row.id == object_id:
                    return row
        return None

    session.refresh.side_effect = refresh
    session.flush.side_effect = flush
    session.get.side_effect = get


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
    assert session.flush.call_count >= 1
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
    assert extracted.payload_json["provenance"]["resource_id"] == 1
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


def test_import_pdf_resource_stores_uploaded_file_without_parsing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    from app.config import get_settings

    get_settings.cache_clear()

    session = MagicMock()
    _mock_import_session(session, resource_id=3, extracted_id=12)
    pdf_bytes = b"%PDF-1.4\n%fake pdf content\n"

    result = import_pdf_resource(
        session,
        PdfImportCreate(
            title="Interview Math PDF",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.FLASHCARD,
        ),
        filename="interview-math.pdf",
        content_type="application/pdf",
        content=pdf_bytes,
    )

    saved = session.add.call_args_list[0].args[0]
    assert saved.source_type is ResourceSourceType.PDF
    assert saved.url is not None
    assert saved.url.startswith("pdfs/")
    assert saved.url.endswith("interview-math.pdf")
    assert saved.title == "Interview Math PDF"
    assert saved.status is ContentStatus.DRAFT
    assert len(saved.raw_text_hash or "") == 64
    assert (tmp_path / "uploads" / saved.url).is_file()
    extracted = session.add.call_args_list[1].args[0]
    assert extracted.object_type is ExtractedObjectType.FLASHCARD
    assert extracted.payload_json["front"] == "Interview Math PDF"
    assert result.id == 3
    assert result.extracted_object_id == 12
    get_settings.cache_clear()


def test_import_pdf_rejects_non_pdf_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    from app.config import get_settings

    get_settings.cache_clear()
    session = MagicMock()
    _mock_import_session(session)

    with pytest.raises(ValueError, match="not a valid PDF"):
        import_pdf_resource(
            session,
            PdfImportCreate(topic_slug=_TOPIC_SLUG, object_type=ExtractedObjectType.QUESTION),
            filename="notes.pdf",
            content_type="application/pdf",
            content=b"not a pdf",
        )
    get_settings.cache_clear()


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
    session.get.return_value = resource

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
        data={
            "title": "Local PDF",
            "topic_slug": _TOPIC_SLUG,
            "object_type": "question",
        },
        files={
            "file": ("quant-notes.pdf", b"%PDF-1.4\n%test\n", "application/pdf"),
        },
    )
    assert pdf_response.status_code == 200
    pdf_body = pdf_response.json()
    assert pdf_body["source_type"] == "pdf"
    assert pdf_body["url"] is not None
    assert pdf_body["url"].startswith("pdfs/")
    assert pdf_body["title"] == "Local PDF"
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
