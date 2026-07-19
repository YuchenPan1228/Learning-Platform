from app.ai.errors import AIProviderConfigurationError
from app.ai.routing import PRODUCTION_MODEL_TARGETS, resolve_chat_model, resolve_embedding_model
from app.ai.tasks import AITask
from app.config import Settings


def _settings(**overrides: str | float) -> Settings:
    defaults: dict[str, str | float] = {
        "ai_provider": "ollama",
        "ollama_base_url": "http://localhost:11434",
        "ollama_chat_model": "qwen2.5:3b",
        "ollama_model_tutor": "",
        "ollama_model_coding": "",
        "ollama_model_reasoning": "",
        "ollama_embedding_model": "",
        "ollama_request_timeout_seconds": 30.0,
        "ai_json_repair_attempts": 1,
    }
    merged = {**defaults, **overrides}
    return Settings.model_construct(
        ai_provider=str(merged["ai_provider"]),
        ollama_base_url=str(merged["ollama_base_url"]),
        ollama_chat_model=str(merged["ollama_chat_model"]),
        ollama_model_tutor=str(merged["ollama_model_tutor"]),
        ollama_model_coding=str(merged["ollama_model_coding"]),
        ollama_model_reasoning=str(merged["ollama_model_reasoning"]),
        ollama_embedding_model=str(merged["ollama_embedding_model"]),
        ollama_request_timeout_seconds=float(merged["ollama_request_timeout_seconds"]),
        ai_json_repair_attempts=int(merged["ai_json_repair_attempts"]),
    )


def test_resolve_chat_model_falls_back_to_default() -> None:
    settings = _settings()
    assert resolve_chat_model(AITask.TUTOR, settings) == "qwen2.5:3b"
    assert resolve_chat_model(AITask.CODING, settings) == "qwen2.5:3b"
    assert resolve_chat_model(AITask.REASONING, settings) == "qwen2.5:3b"


def test_resolve_chat_model_prefers_specialized_override() -> None:
    settings = _settings(
        ollama_model_tutor="qwen3:8b",
        ollama_model_coding="qwen2.5-coder:7b",
        ollama_model_reasoning="deepseek-r1:8b",
    )
    assert resolve_chat_model(AITask.TUTOR, settings) == "qwen3:8b"
    assert resolve_chat_model(AITask.CODING, settings) == "qwen2.5-coder:7b"
    assert resolve_chat_model(AITask.REASONING, settings) == "deepseek-r1:8b"


def test_resolve_chat_model_rejects_embedding_task() -> None:
    try:
        resolve_chat_model(AITask.EMBEDDING, _settings())
        raise AssertionError("expected configuration error")
    except AIProviderConfigurationError as exc:
        assert "resolve_embedding_model" in str(exc)


def test_resolve_embedding_model_requires_config() -> None:
    try:
        resolve_embedding_model(_settings())
        raise AssertionError("expected configuration error")
    except AIProviderConfigurationError as exc:
        assert "OLLAMA_EMBEDDING_MODEL" in str(exc)


def test_resolve_embedding_model_returns_configured_value() -> None:
    settings = _settings(ollama_embedding_model="nomic-embed-text")
    assert resolve_embedding_model(settings) == "nomic-embed-text"


def test_production_targets_cover_all_tasks() -> None:
    assert set(PRODUCTION_MODEL_TARGETS) == set(AITask)
    assert PRODUCTION_MODEL_TARGETS[AITask.TUTOR] == "qwen3:32b"
    assert PRODUCTION_MODEL_TARGETS[AITask.CODING] == "qwen2.5-coder:32b"
    assert PRODUCTION_MODEL_TARGETS[AITask.REASONING] == "deepseek-r1"
    assert PRODUCTION_MODEL_TARGETS[AITask.EMBEDDING] == "nomic-embed-text"
