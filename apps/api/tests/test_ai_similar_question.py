from datetime import UTC, datetime
from typing import cast
from unittest.mock import MagicMock, patch

import pytest
from app.ai.types import AIChatResult, AITokenUsage
from app.dependencies import get_ai_provider
from app.models.ai_cache_entry import AICacheEntry
from app.models.enums import (
    AICacheResultKind,
    ContentStatus,
    Difficulty,
    DuplicateMatchType,
)
from app.models.question import Question
from app.services.ai_similar_question import (
    AISimilarQuestionResponseError,
    SimilarQuestionDuplicateError,
    generate_similar_question,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _question() -> Question:
    return Question(
        id=42,
        title="Exactly 7 Heads",
        body="You flip 10 fair coins. What is the probability of exactly 7 heads?",
        short_answer="15/128",
        canonical_solution="C(10,7)/2^10 = 15/128.",
        difficulty=Difficulty.EASY,
        topic_id=1,
        subtopic_id=2,
        updated_at=datetime(2026, 7, 17, tzinfo=UTC),
    )


def _provider() -> MagicMock:
    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.return_value = AIChatResult(
        content=(
            '{"title":"Exactly 6 Heads",'
            '"body":"You flip 9 fair coins. What is the probability of exactly 6 heads?",'
            '"short_answer":"21/128",'
            '"canonical_solution":"C(9,6)/2^9 = 84/512 = 21/128.",'
            '"difficulty":"easy",'
            '"common_mistakes":["Using 2^10 by mistake"],'
            '"expected_solution_pattern":"Binomial coefficient over 2^n",'
            '"estimated_time_seconds":180}'
        ),
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=90, output_tokens=60),
        latency_ms=220,
    )
    return provider


@patch("app.services.ai_similar_question.find_duplicate_matches", return_value=[])
@patch("app.services.ai_similar_question.apply_question_fingerprints")
def test_generate_similar_question_creates_draft(
    _mock_fingerprints: MagicMock,
    _mock_duplicates: MagicMock,
) -> None:
    session = MagicMock()
    session.scalar.return_value = None

    def _refresh(row: object) -> None:
        if isinstance(row, Question):
            row.id = 99

    session.refresh.side_effect = _refresh
    provider = _provider()

    response = generate_similar_question(session, provider, question=_question())

    assert response.cache_hit is False
    assert response.source_question_id == 42
    assert response.draft_question_id == 99
    assert response.generated_from_id == 42
    assert response.status == ContentStatus.DRAFT
    assert response.title == "Exactly 6 Heads"
    provider.chat.assert_called_once()

    draft = next(
        call.args[0] for call in session.add.call_args_list if isinstance(call.args[0], Question)
    )
    assert draft.status == ContentStatus.DRAFT
    assert draft.generated_from_id == 42
    assert draft.extraction_method == "ai_similar_generation"
    assert draft.model_version == "qwen2.5:3b"


def test_generate_similar_question_uses_cached_draft() -> None:
    session = MagicMock()
    draft = Question(
        id=99,
        title="Exactly 6 Heads",
        body="You flip 9 fair coins. What is the probability of exactly 6 heads?",
        short_answer="21/128",
        canonical_solution="C(9,6)/2^9.",
        difficulty=Difficulty.EASY,
        topic_id=1,
        subtopic_id=2,
        status=ContentStatus.DRAFT,
        generated_from_id=42,
    )
    session.scalar.return_value = AICacheEntry(
        provider="ollama",
        model="qwen2.5:3b",
        result_kind=AICacheResultKind.GENERATED_QUESTION,
        prompt_template_version="similar-question:v2",
        prompt_hash="b" * 64,
        input_object_version="question:42:v1",
        response_json={"draft_question_id": 99},
    )
    session.get.return_value = draft
    session.refresh.side_effect = lambda row: row
    provider = _provider()

    response = generate_similar_question(session, provider, question=_question())

    assert response.cache_hit is True
    assert response.draft_question_id == 99
    assert response.generated_from_id == 42
    provider.chat.assert_not_called()


def test_generate_similar_question_rejects_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_JSON_REPAIR_ATTEMPTS", "0")
    from app.config import get_settings

    get_settings.cache_clear()
    session = MagicMock()
    session.scalar.return_value = None
    provider = _provider()
    provider.chat.return_value.content = "not-json"

    with pytest.raises(AISimilarQuestionResponseError, match="invalid structured JSON"):
        generate_similar_question(session, provider, question=_question())
    get_settings.cache_clear()


@patch(
    "app.services.ai_similar_question.find_duplicate_matches",
    return_value=[MagicMock(match_type=DuplicateMatchType.EXACT_RAW)],
)
def test_generate_similar_question_rejects_exact_duplicates(
    _mock_duplicates: MagicMock,
) -> None:
    session = MagicMock()
    session.scalar.return_value = None
    provider = _provider()

    with pytest.raises(SimilarQuestionDuplicateError, match="exactly"):
        generate_similar_question(session, provider, question=_question())


@pytest.mark.integration
def test_similar_endpoint_creates_draft_then_uses_cache(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider()
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        question_id = client.get("/questions", params={"limit": 1}).json()["items"][0]["id"]

        first = client.post(f"/questions/{question_id}/similar")
        second = client.post(f"/questions/{question_id}/similar")
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert first.status_code == 200
    payload = first.json()
    assert payload["cache_hit"] is False
    assert payload["status"] == "draft"
    assert payload["generated_from_id"] == question_id
    assert payload["draft_question_id"] != question_id

    assert second.status_code == 200
    assert second.json()["cache_hit"] is True
    assert second.json()["draft_question_id"] == payload["draft_question_id"]
    provider.chat.assert_called_once()


@pytest.mark.integration
def test_similar_endpoint_returns_404_for_missing_question(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider()
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        response = client.post("/questions/999999/similar")
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert response.status_code == 404
