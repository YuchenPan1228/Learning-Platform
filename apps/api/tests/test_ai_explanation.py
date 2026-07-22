from datetime import UTC, datetime
from typing import cast
from unittest.mock import MagicMock

import pytest
from app.ai.types import AIChatResult, AITokenUsage
from app.dependencies import get_ai_provider
from app.models.ai_cache_entry import AICacheEntry
from app.models.enums import AICacheResultKind, Difficulty
from app.models.question import Question
from app.services.ai_explanation import (
    AIExplanationResponseError,
    generate_question_explanation,
    generate_question_hints,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient


def _question() -> Question:
    return Question(
        id=42,
        title="Two Heads Given One Head",
        body="Two fair coins are flipped. Given at least one head, find P(HH).",
        canonical_solution="Condition on HH, HT, and TH. Only HH works, so the answer is 1/3.",
        expected_solution_pattern="Update the conditional sample space.",
        common_mistakes=["Answering 1/2 without updating the sample space"],
        difficulty=Difficulty.MEDIUM,
        topic_id=1,
        updated_at=datetime(2026, 7, 17, tzinfo=UTC),
    )


def _provider(*, content: str) -> MagicMock:
    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.return_value = AIChatResult(
        content=content,
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=80, output_tokens=35),
        latency_ms=150,
    )
    return provider


def test_generate_question_hints_calls_provider_and_caches_result() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row
    provider = _provider(content='{"hints":["List the reduced sample space."]}')

    response = generate_question_hints(
        session,
        provider,
        question=_question(),
        user_answer="I think it is 1/2.",
    )

    assert response.question_id == 42
    assert response.cache_hit is False
    assert response.hints == ["List the reduced sample space."]
    provider.chat.assert_called_once()
    assert provider.chat.call_args.kwargs["response_schema"] is not None
    cached = session.add.call_args.args[0]
    assert isinstance(cached, AICacheEntry)
    assert cached.result_kind == AICacheResultKind.HINT


def test_generate_question_hints_allows_empty_answer() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row
    provider = _provider(content='{"hints":["Identify the sample space first."]}')

    response = generate_question_hints(
        session,
        provider,
        question=_question(),
        user_answer="",
    )

    assert response.hints == ["Identify the sample space first."]
    user_message = provider.chat.call_args.args[0][1]
    assert '"user_answer": ""' in user_message.content


def test_generate_question_explanation_calls_provider_and_caches_result() -> None:
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row
    provider = _provider(
        content='{"explanation":"Condition on HH, HT, TH. Only HH works, so 1/3."}',
    )

    response = generate_question_explanation(
        session,
        provider,
        question=_question(),
        user_answer="I think it is 1/2.",
    )

    assert response.question_id == 42
    assert response.cache_hit is False
    assert "1/3" in response.explanation
    provider.chat.assert_called_once()
    assert provider.chat.call_args.kwargs["model"] == "qwen2.5:3b"
    system_message = provider.chat.call_args.args[0][0]
    assert "canonical solution" in system_message.content
    assert "common mistakes" in system_message.content.lower()

    cached = session.add.call_args.args[0]
    assert isinstance(cached, AICacheEntry)
    assert cached.result_kind == AICacheResultKind.EXPLANATION
    assert "common_mistakes" not in cached.response_json


def test_generate_question_explanation_uses_cached_result() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row
    session.scalar.return_value = AICacheEntry(
        provider="ollama",
        model="qwen2.5:3b",
        result_kind=AICacheResultKind.EXPLANATION,
        prompt_template_version="question-explanation:v5",
        prompt_hash="a" * 64,
        input_object_version="question:42:v1",
        response_json={
            "explanation": "Cached explanation.",
        },
    )
    provider = _provider(content='{"explanation":"unused"}')

    response = generate_question_explanation(
        session,
        provider,
        question=_question(),
        user_answer="1/2",
    )

    assert response.cache_hit is True
    assert response.explanation == "Cached explanation."
    provider.chat.assert_not_called()
    usage_log = session.add.call_args.args[0]
    assert usage_log.cache_hit is True
    assert usage_log.latency_ms == 0


def test_generate_question_explanation_rejects_invalid_provider_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_JSON_REPAIR_ATTEMPTS", "0")
    from app.config import get_settings

    get_settings.cache_clear()
    session = MagicMock()
    session.scalar.return_value = None
    provider = _provider(content="not-json")

    with pytest.raises(AIExplanationResponseError, match="invalid structured JSON"):
        generate_question_explanation(
            session,
            provider,
            question=_question(),
            user_answer="1/2",
        )
    get_settings.cache_clear()


@pytest.mark.integration
def test_explanation_endpoint_generates_then_uses_cache(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider(
        content='{"explanation":"Use the binomial coefficient C(10,7)/2^10."}',
    )
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        question_id = client.get("/questions", params={"limit": 1}).json()[0]["id"]

        first = client.post(
            f"/questions/{question_id}/explanation",
            json={"answer": "My attempted answer"},
        )
        second = client.post(
            f"/questions/{question_id}/explanation",
            json={"answer": "My attempted answer"},
        )
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert first.status_code == 200
    assert first.json()["cache_hit"] is False
    assert first.json()["explanation"]
    assert "common_mistakes" not in first.json()
    assert second.status_code == 200
    assert second.json()["cache_hit"] is True
    provider.chat.assert_called_once()


@pytest.mark.integration
def test_hints_endpoint_generates(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider(content='{"hints":["Count equally likely outcomes."]}')
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        question_id = client.get("/questions", params={"limit": 1}).json()[0]["id"]
        response = client.post(
            f"/questions/{question_id}/hints",
            json={"answer": "My attempted answer"},
        )
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert response.status_code == 200
    assert response.json()["hints"]
    assert response.json()["cache_hit"] is False


@pytest.mark.integration
def test_hints_endpoint_allows_empty_answer(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider(content='{"hints":["Start from the definition."]}')
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        question_id = client.get("/questions", params={"limit": 1}).json()[0]["id"]
        empty = client.post(f"/questions/{question_id}/hints", json={"answer": ""})
        missing = client.post(f"/questions/{question_id}/hints", json={})
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert empty.status_code == 200
    assert empty.json()["hints"]
    assert missing.status_code == 200
    assert missing.json()["hints"]
    # Same empty-answer cache key should hit on the second call.
    assert missing.json()["cache_hit"] is True


@pytest.mark.integration
def test_explanation_endpoint_rejects_empty_answer(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider(content='{"explanation":"unused"}')
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        response = client.post("/questions/1/explanation", json={"answer": ""})
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert response.status_code == 422
