from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from app.dedup.text import text_hash
from app.models.enums import ContentStatus, ResourceSourceType
from app.models.resource import Resource
from app.schemas.admin_import import (
    NoteImportCreate,
    PdfMetadataImportCreate,
    UrlImportCreate,
)
from app.services.admin_import import (
    import_note_resource,
    import_pdf_metadata_resource,
    import_url_resource,
)
from fastapi.testclient import TestClient
from pydantic import ValidationError


def _attach_persisted_fields(row: Resource, resource_id: int) -> None:
    row.id = resource_id
    now = datetime.now(UTC)
    row.created_at = now
    row.updated_at = now


def test_import_url_resource_creates_draft_without_crawling() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: _attach_persisted_fields(row, 1)

    result = import_url_resource(
        session,
        UrlImportCreate(
            url="https://example.com/bayes",
            title="Bayes notes",
            license="CC-BY-4.0",
        ),
    )

    session.add.assert_called_once()
    session.commit.assert_called_once()
    saved = session.add.call_args.args[0]
    assert isinstance(saved, Resource)
    assert saved.source_type is ResourceSourceType.URL
    assert saved.url == "https://example.com/bayes"
    assert saved.title == "Bayes notes"
    assert saved.license == "CC-BY-4.0"
    assert saved.status is ContentStatus.DRAFT
    assert saved.raw_text_hash == text_hash("https://example.com/bayes")
    assert result.id == 1
    assert result.source_type is ResourceSourceType.URL


def test_import_note_resource_stores_text_as_summary() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: _attach_persisted_fields(row, 2)

    result = import_note_resource(
        session,
        NoteImportCreate(
            note_text="  Bayes theorem relates P(A|B) to P(B|A).  ",
            title="Bayes note",
            source_type=ResourceSourceType.BOOK_NOTE,
            attribution="Handwritten study notes",
        ),
    )

    saved = session.add.call_args.args[0]
    assert saved.source_type is ResourceSourceType.BOOK_NOTE
    assert saved.summary == "Bayes theorem relates P(A|B) to P(B|A)."
    assert saved.raw_text_hash == text_hash("Bayes theorem relates P(A|B) to P(B|A).")
    assert saved.url is None
    assert saved.status is ContentStatus.DRAFT
    assert result.summary == "Bayes theorem relates P(A|B) to P(B|A)."


def test_note_import_rejects_non_note_source_type() -> None:
    with pytest.raises(ValidationError):
        NoteImportCreate(
            note_text="text",
            source_type=ResourceSourceType.URL,
        )


def test_import_pdf_metadata_stores_path_without_parsing() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: _attach_persisted_fields(row, 3)

    result = import_pdf_metadata_resource(
        session,
        PdfMetadataImportCreate(
            title="Interview Math PDF",
            file_path="/Users/me/docs/interview-math.pdf",
            publisher="Self",
            license="All rights reserved",
        ),
    )

    saved = session.add.call_args.args[0]
    assert saved.source_type is ResourceSourceType.PDF
    assert saved.url == "/Users/me/docs/interview-math.pdf"
    assert saved.title == "Interview Math PDF"
    assert saved.publisher == "Self"
    assert saved.status is ContentStatus.DRAFT
    assert saved.raw_text_hash == text_hash("/Users/me/docs/interview-math.pdf")
    assert result.id == 3


@pytest.mark.integration
def test_admin_import_endpoints_create_resources(
    migrated_database: None,
    require_postgres: None,
    client: TestClient,
) -> None:
    url_response = client.post(
        "/admin/import/url",
        json={
            "url": "https://example.com/conditional-probability",
            "title": "Conditional probability",
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
        },
    )
    assert note_response.status_code == 200
    note_body = note_response.json()
    assert note_body["source_type"] == "manual"
    assert note_body["summary"].startswith("Independence means")

    pdf_response = client.post(
        "/admin/import/pdf",
        json={
            "title": "Local PDF",
            "file_path": "/tmp/quant-notes.pdf",
            "author": "Yuchen",
        },
    )
    assert pdf_response.status_code == 200
    pdf_body = pdf_response.json()
    assert pdf_body["source_type"] == "pdf"
    assert pdf_body["url"] == "/tmp/quant-notes.pdf"
    assert pdf_body["author"] == "Yuchen"
