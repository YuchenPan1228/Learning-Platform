"""Structured JSON chat: schema-constrained generation with optional repair."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from app.ai.errors import AIProviderRequestError
from app.ai.json_response import loads_model_json
from app.ai.provider import AIProvider
from app.ai.types import AIChatResult, AIMessage, AIMessageRole
from app.config import get_settings

T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(ValueError):
    """Raised when a model cannot produce schema-valid JSON after retries."""


def chat_structured(
    provider: AIProvider,
    messages: Sequence[AIMessage],
    *,
    response_model: type[T],
    model: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
    repair_attempts: int | None = None,
    cache_hit: bool = False,
    prompt_hash: str | None = None,
    input_object_version: str | None = None,
) -> tuple[T, AIChatResult]:
    """Call the provider with a JSON Schema and validate into ``response_model``.

    On parse/validation failure, optionally asks the model to repair the payload.
    """
    resolved_repairs = (
        repair_attempts
        if repair_attempts is not None
        else get_settings().ai_json_repair_attempts
    )
    attempts = 1 + max(0, resolved_repairs)
    schema = response_model.model_json_schema()
    base_messages = list(messages)
    current_messages = base_messages
    last_error = "unknown error"
    last_result: AIChatResult | None = None

    for attempt in range(attempts):
        try:
            result = provider.chat(
                current_messages,
                model=model,
                temperature=temperature,
                response_schema=schema,
                max_tokens=max_tokens,
                cache_hit=cache_hit,
                prompt_hash=prompt_hash,
                input_object_version=input_object_version,
            )
        except AIProviderRequestError:
            raise
        last_result = result
        try:
            payload = loads_model_json(result.content)
            return response_model.model_validate(payload), result
        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            last_error = str(exc)
            if attempt + 1 >= attempts:
                break
            current_messages = [
                *base_messages,
                AIMessage(role=AIMessageRole.ASSISTANT, content=result.content),
                AIMessage(
                    role=AIMessageRole.USER,
                    content=(
                        "Your previous response did not match the required JSON schema. "
                        f"Validation error: {last_error}. "
                        "Return only a corrected JSON object that satisfies the schema."
                    ),
                ),
            ]

    raise StructuredOutputError(
        f"AI provider returned invalid structured JSON after {attempts} attempt(s): "
        f"{last_error}",
    ) from None
