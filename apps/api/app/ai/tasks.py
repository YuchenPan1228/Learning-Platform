"""Task roles used to route AI requests to specialized models."""

from enum import StrEnum


class AITask(StrEnum):
    """High-level AI workload categories for model routing."""

    GENERAL = "general"
    CODING = "coding"
    REASONING = "reasoning"
    EMBEDDING = "embedding"
