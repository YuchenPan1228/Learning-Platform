from unittest.mock import MagicMock

import pytest
from app.ai.structured import StructuredOutputError, chat_structured
from app.ai.types import AIChatResult, AIMessage, AIMessageRole, AITokenUsage
from pydantic import BaseModel, Field


class _SampleModel(BaseModel):
    answer: str = Field(min_length=1)


def _result(content: str) -> AIChatResult:
    return AIChatResult(
        content=content,
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=1, output_tokens=1),
        latency_ms=10,
    )


def test_chat_structured_validates_schema_payload() -> None:
    provider = MagicMock()
    provider.chat.return_value = _result('{"answer":"ok"}')

    parsed, result = chat_structured(
        provider,
        [AIMessage(role=AIMessageRole.USER, content="hi")],
        response_model=_SampleModel,
        repair_attempts=0,
    )

    assert parsed.answer == "ok"
    assert result.content == '{"answer":"ok"}'
    assert provider.chat.call_args.kwargs["response_schema"] == _SampleModel.model_json_schema()


def test_chat_structured_repairs_invalid_json_once() -> None:
    provider = MagicMock()
    provider.chat.side_effect = [
        _result("not-json"),
        _result('{"answer":"fixed"}'),
    ]

    parsed, _result_value = chat_structured(
        provider,
        [AIMessage(role=AIMessageRole.USER, content="hi")],
        response_model=_SampleModel,
        repair_attempts=1,
    )

    assert parsed.answer == "fixed"
    assert provider.chat.call_count == 2


def test_chat_structured_raises_after_exhausted_repairs() -> None:
    provider = MagicMock()
    provider.chat.return_value = _result("still-bad")

    with pytest.raises(StructuredOutputError, match="after 2 attempt"):
        chat_structured(
            provider,
            [AIMessage(role=AIMessageRole.USER, content="hi")],
            response_model=_SampleModel,
            repair_attempts=1,
        )
