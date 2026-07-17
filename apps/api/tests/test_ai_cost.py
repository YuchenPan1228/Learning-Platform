from decimal import Decimal

from app.ai.cost import estimate_chat_cost
from app.ai.types import AITokenUsage


def test_estimate_chat_cost_for_ollama_is_zero() -> None:
    cost = estimate_chat_cost(
        provider="ollama",
        model="qwen2.5:3b",
        token_usage=AITokenUsage(input_tokens=100, output_tokens=50),
    )

    assert cost == Decimal("0")


def test_estimate_chat_cost_for_unknown_provider_defaults_to_zero() -> None:
    cost = estimate_chat_cost(
        provider="openai",
        model="gpt-4o",
        token_usage=AITokenUsage(input_tokens=100, output_tokens=50),
    )

    assert cost == Decimal("0")
