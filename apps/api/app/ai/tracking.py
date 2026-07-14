from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.ai.provider import AIProvider
from app.ai.types import AIChatResult, AIMessage
from app.services.ai_usage import record_ai_usage_from_chat_result


class TrackingAIProvider(AIProvider):
    """Wraps an AI provider and persists usage metrics after each chat call."""

    def __init__(self, provider: AIProvider, session: Session) -> None:
        self._provider = provider
        self._session = session

    @property
    def provider_name(self) -> str:
        return self._provider.provider_name

    @property
    def chat_model(self) -> str:
        return self._provider.chat_model

    def chat(
        self,
        messages: Sequence[AIMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
        cache_hit: bool = False,
        prompt_hash: str | None = None,
        input_object_version: str | None = None,
    ) -> AIChatResult:
        result = self._provider.chat(
            messages,
            model=model,
            temperature=temperature,
            cache_hit=cache_hit,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        )
        record_ai_usage_from_chat_result(
            self._session,
            result,
            cache_hit=cache_hit,
            prompt_hash=prompt_hash,
            input_object_version=input_object_version,
        )
        return result
