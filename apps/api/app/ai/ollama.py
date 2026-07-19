import time
from collections.abc import Mapping, Sequence
from typing import Any

import httpx

from app.ai.errors import AIProviderConfigurationError, AIProviderRequestError
from app.ai.provider import AIProvider
from app.ai.tasks import AITask
from app.ai.types import AIChatResult, AIMessage, AITokenUsage


class OllamaProvider(AIProvider):
    """Local Ollama adapter for chat completions."""

    def __init__(
        self,
        *,
        base_url: str,
        chat_model: str,
        request_timeout_seconds: float,
        model_by_task: Mapping[AITask, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        normalized_base_url = base_url.rstrip("/")
        if not normalized_base_url:
            raise AIProviderConfigurationError("OLLAMA_BASE_URL must be set.")

        self._base_url = normalized_base_url
        self._chat_model = chat_model.strip()
        self._request_timeout_seconds = request_timeout_seconds
        self._model_by_task = {
            task: model.strip()
            for task, model in (model_by_task or {}).items()
            if model.strip()
        }
        self._http_client = http_client
        self._owns_http_client = http_client is None

        if not self._chat_model and not self._model_by_task:
            raise AIProviderConfigurationError(
                "OLLAMA_CHAT_MODEL must be set before using the Ollama provider.",
            )
        if not self._chat_model:
            # Prefer tutor, then any configured task model, as the default identity.
            self._chat_model = (
                self._model_by_task.get(AITask.TUTOR)
                or next(iter(self._model_by_task.values()))
            )

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def chat_model(self) -> str:
        return self._chat_model

    def model_for_task(self, task: AITask) -> str:
        if task is AITask.EMBEDDING:
            raise AIProviderConfigurationError(
                "OllamaProvider.model_for_task does not resolve embedding models.",
            )
        return self._model_by_task.get(task) or self._chat_model

    def chat(
        self,
        messages: Sequence[AIMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        json_mode: bool = False,
        response_schema: Mapping[str, Any] | None = None,
        cache_hit: bool = False,
        prompt_hash: str | None = None,
        input_object_version: str | None = None,
    ) -> AIChatResult:
        del cache_hit, prompt_hash, input_object_version
        resolved_model = (model or self._chat_model).strip()
        if not resolved_model:
            raise AIProviderConfigurationError("A chat model must be configured.")

        payload: dict[str, Any] = {
            "model": resolved_model,
            "messages": [
                {"role": message.role.value, "content": message.content} for message in messages
            ],
            "stream": False,
        }
        if response_schema is not None:
            payload["format"] = dict(response_schema)
        elif json_mode:
            payload["format"] = "json"
        if temperature is not None:
            payload["options"] = {"temperature": temperature}

        started_at = time.perf_counter()
        try:
            response = self._get_client().post(
                "/api/chat",
                json=payload,
                timeout=self._request_timeout_seconds,
            )
            response.raise_for_status()
            body = response.json()
        except httpx.HTTPStatusError as exc:
            raise AIProviderRequestError(
                f"Ollama returned HTTP {exc.response.status_code}.",
            ) from exc
        except httpx.HTTPError as exc:
            raise AIProviderRequestError("Ollama request failed.") from exc

        latency_ms = int((time.perf_counter() - started_at) * 1000)
        message = body.get("message")
        if not isinstance(message, dict):
            raise AIProviderRequestError("Ollama response did not include a message.")

        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise AIProviderRequestError("Ollama response did not include message content.")

        response_model = body.get("model")
        resolved_response_model = (
            response_model if isinstance(response_model, str) and response_model else resolved_model
        )

        return AIChatResult(
            content=content,
            provider=self.provider_name,
            model=resolved_response_model,
            token_usage=AITokenUsage(
                input_tokens=_coerce_token_count(body.get("prompt_eval_count")),
                output_tokens=_coerce_token_count(body.get("eval_count")),
            ),
            latency_ms=latency_ms,
        )

    def close(self) -> None:
        if self._owns_http_client and self._http_client is not None:
            self._http_client.close()
            self._http_client = None

    def _get_client(self) -> httpx.Client:
        if self._http_client is None:
            self._http_client = httpx.Client(base_url=self._base_url)
        return self._http_client


def _coerce_token_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None
