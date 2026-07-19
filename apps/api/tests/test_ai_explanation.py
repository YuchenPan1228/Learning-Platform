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


def _provider() -> MagicMock:
    provider = MagicMock()
    provider.provider_name = "ollama"
    provider.chat_model = "qwen2.5:3b"
    provider.model_for_task.return_value = "qwen2.5:3b"
    provider.chat.return_value = AIChatResult(
        content=(
            '{"explanation":"Condition on the reduced sample space.",'
            '"hints":["List equally likely outcomes after conditioning."],'
            '"common_mistakes":["Keeping TT in the sample space."]}'
        ),
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=80, output_tokens=35),
        latency_ms=150,
    )
    return provider


def test_generate_question_explanation_calls_provider_and_caches_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_JSON_REPAIR_ATTEMPTS", "0")
    from app.config import get_settings

    get_settings.cache_clear()
    session = MagicMock()
    session.scalar.return_value = None
    session.refresh.side_effect = lambda row: row
    provider = _provider()

    response = generate_question_explanation(
        session,
        provider,
        question=_question(),
        user_answer="I think it is 1/2.",
    )

    assert response.question_id == 42
    assert response.cache_hit is False
    assert response.explanation == "Condition on the reduced sample space."
    assert response.hints == ["List equally likely outcomes after conditioning."]
    provider.chat.assert_called_once()
    assert provider.chat.call_args.kwargs["response_schema"] is not None
    assert provider.chat.call_args.kwargs["model"] == "qwen2.5:3b"
    system_message = provider.chat.call_args.args[0][0]
    assert "teach the correct answer step by step" in system_message.content
    assert "final answer" in system_message.content

    cached = session.add.call_args.args[0]
    assert isinstance(cached, AICacheEntry)
    assert cached.result_kind == AICacheResultKind.EXPLANATION
    assert cached.response_json["common_mistakes"] == ["Keeping TT in the sample space."]
    get_settings.cache_clear()


def test_generate_question_explanation_uses_cached_result() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row
    session.scalar.return_value = AICacheEntry(
        provider="ollama",
        model="qwen2.5:3b",
        result_kind=AICacheResultKind.EXPLANATION,
        prompt_template_version="question-explanation:v4",
        prompt_hash="a" * 64,
        input_object_version="question:42:v1",
        response_json={
            "explanation": "Cached explanation.",
            "hints": ["Cached hint."],
            "common_mistakes": ["Cached mistake."],
        },
    )
    provider = _provider()

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
    provider = _provider()
    provider.chat.return_value.content = "not-json"

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
    provider = _provider()
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
    assert first.json()["hints"]
    assert second.status_code == 200
    assert second.json()["cache_hit"] is True
    provider.chat.assert_called_once()


@pytest.mark.integration
def test_explanation_endpoint_rejects_empty_answer(
    client: TestClient,
    seeded_database: None,
    require_postgres: None,
) -> None:
    provider = _provider()
    app = cast(FastAPI, client.app)
    app.dependency_overrides[get_ai_provider] = lambda: provider
    try:
        response = client.post("/questions/1/explanation", json={"answer": ""})
    finally:
        app.dependency_overrides.pop(get_ai_provider, None)

    assert response.status_code == 422
