"""Resolve which local Ollama model should handle a given AI task."""

from __future__ import annotations

from app.ai.errors import AIProviderConfigurationError
from app.ai.tasks import AITask
from app.config import Settings, get_settings

# Documented production targets; local defaults stay small via OLLAMA_CHAT_MODEL.
PRODUCTION_MODEL_TARGETS: dict[AITask, str] = {
    AITask.GENERAL: "qwen3:32b",
    AITask.CODING: "qwen2.5-coder:32b",
    AITask.REASONING: "deepseek-r1",
    AITask.EMBEDDING: "nomic-embed-text",
}


def resolve_chat_model(
    task: AITask,
    settings: Settings | None = None,
) -> str:
    """Return the configured chat model for a task, falling back to OLLAMA_CHAT_MODEL."""
    if task is AITask.EMBEDDING:
        raise AIProviderConfigurationError(
            "EMBEDDING tasks use resolve_embedding_model(), not resolve_chat_model().",
        )

    resolved = settings or get_settings()
    specialized = {
        AITask.GENERAL: (
            resolved.ollama_model_general.strip() or resolved.ollama_model_tutor.strip()
        ),
        AITask.CODING: resolved.ollama_model_coding.strip(),
        AITask.REASONING: resolved.ollama_model_reasoning.strip(),
    }[task]
    model = specialized or resolved.ollama_chat_model.strip()
    if not model:
        raise AIProviderConfigurationError(
            f"No model configured for AI task '{task.value}'. "
            "Set the task-specific OLLAMA_MODEL_* variable or OLLAMA_CHAT_MODEL.",
        )
    return model


def resolve_embedding_model(settings: Settings | None = None) -> str:
    """Return the configured embedding model (reserved until QP-048)."""
    resolved = settings or get_settings()
    model = resolved.ollama_embedding_model.strip()
    if not model:
        raise AIProviderConfigurationError(
            "OLLAMA_EMBEDDING_MODEL must be set before using embedding tasks.",
        )
    return model


def configured_chat_models(settings: Settings | None = None) -> list[str]:
    """Unique chat models that should be warmed for configured tasks."""
    resolved = settings or get_settings()
    models: list[str] = []
    seen: set[str] = set()
    for task in (AITask.GENERAL, AITask.CODING, AITask.REASONING):
        try:
            model = resolve_chat_model(task, resolved)
        except AIProviderConfigurationError:
            continue
        if model not in seen:
            seen.add(model)
            models.append(model)
    return models
