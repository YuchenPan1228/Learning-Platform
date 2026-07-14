from functools import lru_cache

from app.ai.errors import UnsupportedAIProviderError
from app.ai.ollama import OllamaProvider
from app.ai.provider import AIProvider
from app.config import Settings, get_settings

SUPPORTED_AI_PROVIDERS = frozenset({"ollama"})


def create_ai_provider(settings: Settings | None = None) -> AIProvider:
    resolved = settings or get_settings()
    provider_name = resolved.ai_provider.strip().lower()

    if provider_name == "ollama":
        return OllamaProvider(
            base_url=resolved.ollama_base_url,
            chat_model=resolved.ollama_chat_model,
            request_timeout_seconds=resolved.ollama_request_timeout_seconds,
        )

    raise UnsupportedAIProviderError(
        f"AI provider '{resolved.ai_provider}' is not supported yet. "
        f"Supported providers: {', '.join(sorted(SUPPORTED_AI_PROVIDERS))}.",
    )


@lru_cache
def get_ai_provider() -> AIProvider:
    return create_ai_provider()
