from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from typing import Any

from app.ai.tasks import AITask
from app.ai.types import AIChatResult, AIMessage


class AIProvider(ABC):
    """Provider-agnostic interface for chat-based AI calls."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Stable provider identifier, e.g. ``ollama``."""

    @property
    @abstractmethod
    def chat_model(self) -> str:
        """Default chat model configured for this provider."""

    def model_for_task(self, task: AITask) -> str:
        """Resolve the chat model for a workload category."""
        del task
        return self.chat_model

    @abstractmethod
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
        """Run a non-streaming chat completion."""
