from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from app.ai.tracking import TrackingAIProvider
from app.ai.types import AIChatResult, AIMessage, AIMessageRole, AITokenUsage
from app.models.ai_usage_log import AIUsageLog
from app.services.ai_usage import AIUsageRecordInput, record_ai_usage


def test_record_ai_usage_persists_expected_fields() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row

    result = record_ai_usage(
        session,
        AIUsageRecordInput(
            provider="ollama",
            model="qwen2.5:3b",
            input_tokens=12,
            output_tokens=18,
            latency_ms=240,
            cache_hit=False,
            prompt_hash="abc123",
            input_object_version="question:v3",
        ),
    )

    session.add.assert_called_once()
    session.commit.assert_called_once()
    session.refresh.assert_called_once()

    saved = session.add.call_args.args[0]
    assert isinstance(saved, AIUsageLog)
    assert saved.provider == "ollama"
    assert saved.model == "qwen2.5:3b"
    assert saved.input_tokens == 12
    assert saved.output_tokens == 18
    assert saved.latency_ms == 240
    assert saved.estimated_cost_usd == Decimal("0")
    assert saved.cache_hit is False
    assert saved.prompt_hash == "abc123"
    assert saved.input_object_version == "question:v3"
    assert result is saved


def test_tracking_provider_records_usage_after_chat() -> None:
    session = MagicMock()
    session.refresh.side_effect = lambda row: row
    inner = MagicMock()
    inner.provider_name = "ollama"
    inner.chat_model = "qwen2.5:3b"
    inner.chat.return_value = AIChatResult(
        content="Hint: use Bayes.",
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=10, output_tokens=5),
        latency_ms=120,
    )

    provider = TrackingAIProvider(inner, session)
    result = provider.chat(
        [AIMessage(role=AIMessageRole.USER, content="Need a hint.")],
        cache_hit=True,
        prompt_hash="deadbeef",
        input_object_version="attempt:v1",
    )

    assert result.content == "Hint: use Bayes."
    inner.chat.assert_called_once_with(
        [AIMessage(role=AIMessageRole.USER, content="Need a hint.")],
        model=None,
        temperature=None,
        json_mode=False,
        response_schema=None,
        max_tokens=None,
        cache_hit=True,
        prompt_hash="deadbeef",
        input_object_version="attempt:v1",
    )
    session.add.assert_called_once()
    saved = session.add.call_args.args[0]
    assert saved.cache_hit is True
    assert saved.prompt_hash == "deadbeef"
    assert saved.input_object_version == "attempt:v1"


@pytest.mark.integration
def test_record_ai_usage_writes_to_database(
    migrated_database: None,
    require_postgres: None,
) -> None:
    from app.db import get_session_factory

    session = get_session_factory()()
    try:
        log = record_ai_usage(
            session,
            AIUsageRecordInput(
                provider="ollama",
                model="qwen2.5:3b",
                input_tokens=None,
                output_tokens=7,
                latency_ms=95,
                cache_hit=False,
            ),
        )

        assert log.id is not None
        assert log.provider == "ollama"
        assert log.input_tokens is None
        assert log.output_tokens == 7
        assert log.estimated_cost_usd == Decimal("0")
    finally:
        session.close()
