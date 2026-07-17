from decimal import Decimal

from app.ai.types import AITokenUsage


def estimate_chat_cost(
    *,
    provider: str,
    model: str,
    token_usage: AITokenUsage,
) -> Decimal:
    del model, token_usage
    if provider == "ollama":
        return Decimal("0")
    return Decimal("0")
