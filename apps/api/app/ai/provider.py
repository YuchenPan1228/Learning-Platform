from abc import ABC, abstractmethod
from collections.abc import Sequence

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

    @abstractmethod
    def chat(
        self,
        messages: Sequence[AIMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIChatResult:
        """Run a non-streaming chat completion."""
