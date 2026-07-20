"""Warm configured Ollama chat models so the first user request is not a cold load."""

from __future__ import annotations

import logging

import httpx

from app.ai.routing import configured_chat_models
from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def models_to_warm(settings: Settings | None = None) -> list[str]:
    """Models to preload. By default only the fallback chat model is warmed."""
    resolved = settings or get_settings()
    if resolved.ai_warmup_specialized_models:
        return configured_chat_models(resolved)
    default_model = resolved.ollama_chat_model.strip()
    if default_model:
        return [default_model]
    return configured_chat_models(resolved)[:1]


def warmup_configured_models(settings: Settings | None = None) -> None:
    """Send a tiny chat completion for models selected for warmup."""
    resolved = settings or get_settings()
    if not resolved.ai_warmup_on_startup:
        return
    if resolved.ai_provider.strip().lower() != "ollama":
        return

    models = models_to_warm(resolved)
    if not models:
        logger.info("AI warmup skipped: no chat models configured.")
        return

    base_url = resolved.ollama_base_url.rstrip("/")
    timeout = min(resolved.ollama_request_timeout_seconds, 60.0)
    with httpx.Client(base_url=base_url, timeout=timeout) as client:
        for model in models:
            try:
                response = client.post(
                    "/api/chat",
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": "ping"}],
                        "stream": False,
                        "options": {"num_predict": 1},
                    },
                )
                response.raise_for_status()
                logger.info("Warmed Ollama model %s", model)
            except httpx.HTTPError as exc:
                logger.warning("Failed to warm Ollama model %s: %s", model, exc)
