from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from app.dedup.text import text_hash
from app.dependencies import get_ai_provider
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
from app.schemas.ai_extraction import (
    AIStructuredExtractionResult,
    ExtractedDraftSummary,
)
from app.services.admin_import import (
    ImportExtractionError,
    ImportPolicyError,
    import_note_resource,
    import_pdf_resource,
    import_question_resource,
    import_url_resource,
)
from app.services.import_extracted_draft import (
    DraftImportOptions,
    create_extracted_draft_from_resource,
)
from app.services.source_policy import SourcePolicyResult
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


def _allow_policy() -> SourcePolicyResult:
    from app.models.enums import (
        AllowlistStatus,
        LicenseStatus,
        RobotsStatus,
        SourcePolicyDecision,
    )

    return SourcePolicyResult(
        decision=SourcePolicyDecision.ALLOW,
        allowlist_status=AllowlistStatus.NOT_CONFIGURED,
        robots_status=RobotsStatus.ALLOWED,
        license_status=LicenseStatus.PERMISSIVE,
        attribution_required=False,
        attribution_present=True,
        reasons=("ok",),
        host="example.com",
    )


def _deny_policy() -> SourcePolicyResult:
    from app.models.enums import (
        AllowlistStatus,
        LicenseStatus,
        RobotsStatus,
        SourcePolicyDecision,
    )

    return SourcePolicyResult(
        decision=SourcePolicyDecision.DENY,
        allowlist_status=AllowlistStatus.DENIED,
        robots_status=RobotsStatus.ALLOWED,
        license_status=LicenseStatus.MISSING,
        attribution_required=True,
        attribution_present=False,
        reasons=("host not on allowlist",),
        host="bad.example",
    )


def _ai_result(
    *,
    draft_ids: list[int] | None = None,
    method: str = "ai:structured:url_trafilatura",
) -> AIStructuredExtractionResult:
    ids = draft_ids or [10]
    return AIStructuredExtractionResult(
        summary="Source summary from AI",
        topic_slug=_TOPIC_SLUG,
        subtopic_slug=None,
        source_title="Extracted title",
        model_version="qwen2.5:3b",
        extraction_method=method,
        cache_hit=False,
        drafts=[
            ExtractedDraftSummary(
                id=draft_id,
                object_type=ExtractedObjectType.QUESTION,
                title=f"Draft {draft_id}",
                confidence_score=0.9,
            )
            for draft_id in ids
        ],
    )


def test_import_url_resource_runs_policy_and_ai_extraction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    _mock_import_session(session)
    provider = MagicMock()

    monkeypatch.setattr(
        "app.services.admin_import.check_resource_policy",
        lambda resource: _allow_policy(),
    )
    monkeypatch.setattr(
        "app.services.admin_import.extract_structured_drafts_from_resource",
        lambda *args, **kwargs: _ai_result(draft_ids=[10, 11]),
    )

    result = import_url_resource(
        session,
        UrlImportCreate(
            url="https://example.com/bayes",
            title="Bayes notes",
            license="CC-BY-4.0",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.QUESTION,
        ),
        provider=provider,
    )

    assert session.add.call_count >= 1
    session.flush.assert_called()
    session.commit.assert_called_once()
    saved = session.add.call_args_list[0].args[0]
    assert isinstance(saved, Resource)
    assert saved.source_type is ResourceSourceType.URL
    assert saved.url == "https://example.com/bayes"
    assert saved.title == "Bayes notes"
    assert saved.license == "CC-BY-4.0"
    assert saved.status is ContentStatus.DRAFT
    assert saved.raw_text_hash == text_hash("https://example.com/bayes")
    assert result.id == 1
    assert result.extracted_object_id == 10
    assert result.extracted_object_ids == [10, 11]
    assert result.draft_count == 2
    assert result.extraction_method == "ai:structured:url_trafilatura"
    assert result.policy_decision == "allow"
    assert result.source_type is ResourceSourceType.URL


def test_import_url_resource_denies_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock()
    _mock_import_session(session)
    monkeypatch.setattr(
        "app.services.admin_import.check_resource_policy",
        lambda resource: _deny_policy(),
    )

    with pytest.raises(ImportPolicyError, match="source policy denied"):
        import_url_resource(
            session,
            UrlImportCreate(
                url="https://bad.example/secret",
                topic_slug=_TOPIC_SLUG,
            ),
            provider=MagicMock(),
        )
    session.rollback.assert_called()
    session.commit.assert_not_called()


def test_import_url_resource_surfaces_extraction_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = MagicMock()
    _mock_import_session(session)
    monkeypatch.setattr(
        "app.services.admin_import.check_resource_policy",
        lambda resource: _allow_policy(),
    )

    from app.services.ai_structured_extraction import AIStructuredExtractionError

    def raise_ai(*_args: object, **_kwargs: object) -> None:
        raise AIStructuredExtractionError("model proposed no question or flashcard drafts")

    monkeypatch.setattr(
        "app.services.admin_import.extract_structured_drafts_from_resource",
        raise_ai,
    )

    with pytest.raises(ImportExtractionError, match="no question or flashcard"):
        import_url_resource(
            session,
            UrlImportCreate(url="https://example.com/thin", topic_slug=_TOPIC_SLUG),
            provider=MagicMock(),
        )
    session.rollback.assert_called()


def test_import_note_resource_runs_ai_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    session = MagicMock()
    _mock_import_session(session, resource_id=2, extracted_id=11)
    monkeypatch.setattr(
        "app.services.admin_import.check_resource_policy",
        lambda resource: _allow_policy(),
    )
    monkeypatch.setattr(
        "app.services.admin_import.extract_structured_drafts_from_resource",
        lambda *args, **kwargs: _ai_result(
            draft_ids=[11],
            method="ai:structured:pasted_text",
        ),
    )

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
        provider=MagicMock(),
    )

    saved = session.add.call_args_list[0].args[0]
    assert saved.source_type is ResourceSourceType.BOOK_NOTE
    assert saved.summary == "Bayes theorem relates P(A|B) to P(B|A)."
    assert saved.raw_text_hash == text_hash("Bayes theorem relates P(A|B) to P(B|A).")
    assert saved.url is None
    assert result.summary == "Bayes theorem relates P(A|B) to P(B|A)."
    assert result.extracted_object_id == 11
    assert result.extracted_object_ids == [11]
    assert result.extraction_method == "ai:structured:pasted_text"


def test_note_import_rejects_non_note_source_type() -> None:
    with pytest.raises(ValidationError):
        NoteImportCreate(
            note_text="text",
            source_type=ResourceSourceType.URL,
            topic_slug=_TOPIC_SLUG,
        )


def test_note_import_allows_question_without_title() -> None:
    payload = NoteImportCreate(
        note_text="answer text about martingales",
        topic_slug=_TOPIC_SLUG,
        object_type=ExtractedObjectType.QUESTION,
    )
    assert payload.title is None


def test_import_pdf_resource_runs_ai_after_upload(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
    from app.config import get_settings

    get_settings.cache_clear()

    session = MagicMock()
    _mock_import_session(session, resource_id=3, extracted_id=12)
    pdf_bytes = b"%PDF-1.4\n%fake pdf content\n"
    monkeypatch.setattr(
        "app.services.admin_import.check_resource_policy",
        lambda resource: _allow_policy(),
    )
    monkeypatch.setattr(
        "app.services.admin_import.extract_structured_drafts_from_resource",
        lambda *args, **kwargs: _ai_result(
            draft_ids=[12],
            method="ai:structured:pdf_pymupdf",
        ),
    )

    result = import_pdf_resource(
        session,
        PdfImportCreate(
            title="Interview Math PDF",
            topic_slug=_TOPIC_SLUG,
            object_type=ExtractedObjectType.QUESTION,
        ),
        provider=MagicMock(),
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
    assert result.id == 3
    assert result.extracted_object_id == 12
    assert result.extraction_method == "ai:structured:pdf_pymupdf"
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
            provider=MagicMock(),
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
    assert result.extracted_object_ids == [13]
    assert result.extraction_method == "manual:import"


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


def _extraction_payload() -> dict[str, object]:
    return {
        "summary": "Notes on conditional probability.",
        "topic_slug": "probability",
        "subtopic_slug": None,
        "source_title": "Conditional probability",
        "questions": [
            {
                "title": "Independence check",
                "body": "When are events A and B independent?",
                "short_answer": "P(A and B)=P(A)P(B)",
                "difficulty": "easy",
                "confidence_score": 0.9,
            }
        ],
        "flashcards": [
            {
                "front": "Independence formula",
                "back": "P(A and B) = P(A)P(B)",
                "confidence_score": 0.85,
            }
        ],
    }


@pytest.mark.integration
def test_admin_import_endpoints_create_resources(
    seeded_database: None,
    require_postgres: None,
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import json

    from app.ai.types import AIChatResult, AITokenUsage
    from app.main import app
    from app.services.source_extraction import ExtractedSourceText
    from app.models.enums import ExtractionMethod

    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.return_value = AIChatResult(
        content=json.dumps(_extraction_payload()),
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=10, output_tokens=20),
        latency_ms=5,
    )

    def fake_extract(resource: Resource, **_kwargs: object) -> ExtractedSourceText:
        if resource.source_type is ResourceSourceType.URL:
            return ExtractedSourceText(
                text=(
                    "Conditional probability notes. Independence means P(A and B) = P(A)P(B). "
                    "Bayes theorem updates priors."
                ),
                method=ExtractionMethod.URL_TRAFILATURA,
                source_url=resource.url,
                title=resource.title,
            )
        if resource.source_type is ResourceSourceType.PDF:
            return ExtractedSourceText(
                text="PDF text about fair dice probability for quant interviews.",
                method=ExtractionMethod.PDF_PYMUPDF,
                source_url=resource.url,
                title=resource.title,
            )
        return ExtractedSourceText(
            text=resource.summary or "Empty notes",
            method=ExtractionMethod.PASTED_TEXT,
            title=resource.title,
        )

    monkeypatch.setattr(
        "app.services.ai_structured_extraction.extract_from_resource",
        fake_extract,
    )
    app.dependency_overrides[get_ai_provider] = lambda: provider

    try:
        url_response = client.post(
            "/admin/import/url",
            json={
                "url": "https://example.com/conditional-probability",
                "title": "Conditional probability",
                "topic_slug": _TOPIC_SLUG,
                "object_type": "question",
            },
        )
        assert url_response.status_code == 200, url_response.text
        url_body = url_response.json()
        assert url_body["source_type"] == "url"
        assert url_body["status"] == "draft"
        assert url_body["url"] == "https://example.com/conditional-probability"
        assert url_body["draft_count"] >= 1
        assert url_body["extraction_method"].startswith("ai:structured:")
        assert isinstance(url_body["extracted_object_ids"], list)
        assert url_body["extracted_object_id"] in url_body["extracted_object_ids"]

        note_response = client.post(
            "/admin/import/note",
            json={
                "note_text": "Independence means P(A and B) = P(A)P(B).",
                "title": "Independence",
                "source_type": "manual",
                "topic_slug": _TOPIC_SLUG,
                "object_type": "question",
            },
        )
        assert note_response.status_code == 200, note_response.text
        note_body = note_response.json()
        assert note_body["source_type"] == "manual"
        assert note_body["draft_count"] >= 1
        assert note_body["extraction_method"].startswith("ai:structured:")

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
        assert question_body["extraction_method"] == "manual:import"

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
        assert pdf_response.status_code == 200, pdf_response.text
        pdf_body = pdf_response.json()
        assert pdf_body["source_type"] == "pdf"
        assert pdf_body["url"] is not None
        assert pdf_body["url"].startswith("pdfs/")
        assert pdf_body["title"] == "Local PDF"
        assert isinstance(pdf_body["extracted_object_id"], int)
        assert pdf_body["extraction_method"].startswith("ai:structured:")

        review_response = client.get("/admin/review")
        assert review_response.status_code == 200
        review_items = review_response.json()["items"]
        extracted_ids = {item["id"] for item in review_items}
        for draft_id in url_body["extracted_object_ids"]:
            assert draft_id in extracted_ids
        for draft_id in note_body["extracted_object_ids"]:
            assert draft_id in extracted_ids
        assert question_body["extracted_object_id"] in extracted_ids
        assert pdf_body["extracted_object_id"] in extracted_ids

        url_draft = next(
            item for item in review_items if item["id"] == url_body["extracted_object_id"]
        )
        assert url_draft["status"] == "draft"
        assert url_draft["payload_json"]["topic_slug"] == _TOPIC_SLUG
        assert url_draft["resource"]["id"] == url_body["id"]
        assert url_draft["extraction_method"].startswith("ai:structured:")
        assert url_draft["object_type"] == "question"

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
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)
