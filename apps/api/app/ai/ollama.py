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
        default_num_predict: int | None = None,
        model_by_task: Mapping[AITask, str] | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        normalized_base_url = base_url.rstrip("/")
        if not normalized_base_url:
            raise AIProviderConfigurationError("OLLAMA_BASE_URL must be set.")

        self._base_url = normalized_base_url
        self._chat_model = chat_model.strip()
        self._request_timeout_seconds = request_timeout_seconds
        self._default_num_predict = default_num_predict
        self._model_by_task = {
            task: model.strip() for task, model in (model_by_task or {}).items() if model.strip()
        }
        self._http_client = http_client
        self._owns_http_client = http_client is None

        if not self._chat_model and not self._model_by_task:
            raise AIProviderConfigurationError(
                "OLLAMA_CHAT_MODEL must be set before using the Ollama provider.",
            )
        if not self._chat_model:
            # Prefer general, then any configured task model, as the default identity.
            self._chat_model = self._model_by_task.get(AITask.GENERAL) or next(
                iter(self._model_by_task.values())
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
        max_tokens: int | None = None,
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

        options: dict[str, Any] = {}
        if temperature is not None:
            options["temperature"] = temperature
        num_predict = max_tokens if max_tokens is not None else self._default_num_predict
        if num_predict is not None:
            options["num_predict"] = num_predict
        if options:
            payload["options"] = options

        started_at = time.perf_counter()
        try:
            body = self._post_chat(payload)
        except httpx.HTTPStatusError as exc:
            # Full JSON Schema grammars often fail on smaller models (anyOf/$defs).
            # Fall back to free-form JSON mode and let chat_structured validate.
            if (
                response_schema is not None
                and exc.response is not None
                and exc.response.status_code == 400
            ):
                payload["format"] = "json"
                try:
                    body = self._post_chat(payload)
                except httpx.TimeoutException as timeout_exc:
                    raise AIProviderRequestError(
                        f"Ollama timed out after {self._request_timeout_seconds:.0f}s "
                        f"using model '{resolved_model}'. "
                        "For local use, clear heavy OLLAMA_MODEL_* overrides or raise "
                        "OLLAMA_REQUEST_TIMEOUT_SECONDS.",
                    ) from timeout_exc
                except httpx.HTTPStatusError as retry_exc:
                    raise AIProviderRequestError(
                        _ollama_http_error_message(retry_exc, resolved_model),
                    ) from retry_exc
                except httpx.HTTPError as http_exc:
                    raise AIProviderRequestError(
                        f"Ollama request failed using model '{resolved_model}'.",
                    ) from http_exc
            else:
                raise AIProviderRequestError(
                    _ollama_http_error_message(exc, resolved_model),
                ) from exc
        except httpx.TimeoutException as exc:
            raise AIProviderRequestError(
                f"Ollama timed out after {self._request_timeout_seconds:.0f}s "
                f"using model '{resolved_model}'. "
                "For local use, clear heavy OLLAMA_MODEL_* overrides or raise "
                "OLLAMA_REQUEST_TIMEOUT_SECONDS.",
            ) from exc
        except httpx.HTTPError as exc:
            raise AIProviderRequestError(
                f"Ollama request failed using model '{resolved_model}'.",
            ) from exc

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

    def _post_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self._get_client().post(
            "/api/chat",
            json=payload,
            timeout=self._request_timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()
        if not isinstance(body, dict):
            raise AIProviderRequestError("Ollama response was not a JSON object.")
        return body


def _ollama_http_error_message(exc: httpx.HTTPStatusError, model: str) -> str:
    detail = ""
    try:
        payload = exc.response.json()
        if isinstance(payload, dict):
            error = payload.get("error")
            if isinstance(error, str) and error.strip():
                detail = f" {error.strip()}"
            elif isinstance(error, dict):
                message = error.get("message")
                if isinstance(message, str) and message.strip():
                    detail = f" {message.strip()}"
    except ValueError:
        text = (exc.response.text or "").strip()
        if text:
            detail = f" {text[:300]}"
    return f"Ollama returned HTTP {exc.response.status_code} using model '{model}'.{detail}"


def _coerce_token_count(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int) and value >= 0:
        return value
    return None
