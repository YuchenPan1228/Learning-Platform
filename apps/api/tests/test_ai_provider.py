import json

import httpx
import pytest
from app.ai.errors import (
    AIProviderConfigurationError,
    AIProviderRequestError,
    UnsupportedAIProviderError,
)
from app.ai.factory import create_ai_provider, get_ai_provider
from app.ai.ollama import OllamaProvider
from app.ai.types import AIMessage, AIMessageRole
from app.config import Settings, get_settings


def _ollama_settings(**overrides: str | float) -> Settings:
    values: dict[str, str | float] = {
        "AI_PROVIDER": "ollama",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_CHAT_MODEL": "qwen2.5:3b",
        "OLLAMA_EMBEDDING_MODEL": "",
        "OLLAMA_REQUEST_TIMEOUT_SECONDS": 30.0,
    }
    values.update(overrides)
    return Settings(**values)


def test_settings_load_ai_provider_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    monkeypatch.setenv("OLLAMA_CHAT_MODEL", "llama3.2")
    monkeypatch.setenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.ai_provider == "ollama"
    assert settings.ollama_base_url == "http://127.0.0.1:11434"
    assert settings.ollama_chat_model == "llama3.2"
    assert settings.ollama_embedding_model == "nomic-embed-text"

    get_settings.cache_clear()


def test_create_ai_provider_defaults_to_ollama() -> None:
    provider = create_ai_provider(_ollama_settings())

    assert provider.provider_name == "ollama"
    assert provider.chat_model == "qwen2.5:3b"


def test_create_ai_provider_rejects_unsupported_provider() -> None:
    settings = _ollama_settings(AI_PROVIDER="openai")

    with pytest.raises(UnsupportedAIProviderError, match="openai"):
        create_ai_provider(settings)


def test_ollama_provider_requires_chat_model() -> None:
    with pytest.raises(AIProviderConfigurationError, match="OLLAMA_CHAT_MODEL"):
        OllamaProvider(
            base_url="http://localhost:11434",
            chat_model="",
            request_timeout_seconds=30.0,
        )


def test_ollama_provider_chat_parses_success_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        assert request.method == "POST"
        assert json.loads(request.content) == {
            "model": "qwen2.5:3b",
            "messages": [{"role": "user", "content": "Explain Bayes' theorem."}],
            "stream": False,
            "options": {"temperature": 0.2},
        }
        return httpx.Response(
            200,
            json={
                "model": "qwen2.5:3b",
                "message": {
                    "role": "assistant",
                    "content": "Bayes' theorem relates prior and posterior odds.",
                },
                "prompt_eval_count": 12,
                "eval_count": 18,
            },
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://test")
    provider = OllamaProvider(
        base_url="http://test",
        chat_model="qwen2.5:3b",
        request_timeout_seconds=30.0,
        http_client=client,
    )

    result = provider.chat(
        [AIMessage(role=AIMessageRole.USER, content="Explain Bayes' theorem.")],
        temperature=0.2,
    )

    assert result.provider == "ollama"
    assert result.model == "qwen2.5:3b"
    assert result.content == "Bayes' theorem relates prior and posterior odds."
    assert result.token_usage.input_tokens == 12
    assert result.token_usage.output_tokens == 18
    assert result.latency_ms >= 0


def test_ollama_provider_chat_raises_on_http_error() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"error": "model unavailable"})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://test")
    provider = OllamaProvider(
        base_url="http://test",
        chat_model="qwen2.5:3b",
        request_timeout_seconds=30.0,
        http_client=client,
    )

    with pytest.raises(AIProviderRequestError, match="HTTP 500"):
        provider.chat([AIMessage(role=AIMessageRole.USER, content="Hello")])


def test_ollama_provider_chat_raises_on_missing_content() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"model": "qwen2.5:3b", "message": {"role": "assistant"}},
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport, base_url="http://test")
    provider = OllamaProvider(
        base_url="http://test",
        chat_model="qwen2.5:3b",
        request_timeout_seconds=30.0,
        http_client=client,
    )

    with pytest.raises(AIProviderRequestError, match="message content"):
        provider.chat([AIMessage(role=AIMessageRole.USER, content="Hello")])


def test_get_ai_provider_is_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AI_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_CHAT_MODEL", "qwen2.5:3b")
    get_settings.cache_clear()
    get_ai_provider.cache_clear()

    first = get_ai_provider()
    second = get_ai_provider()

    assert first is second

    get_ai_provider.cache_clear()
    get_settings.cache_clear()
