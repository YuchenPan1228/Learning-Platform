class AIProviderError(Exception):
    """Base error for AI provider failures."""


class UnsupportedAIProviderError(AIProviderError):
    """Raised when the configured provider has no adapter yet."""


class AIProviderConfigurationError(AIProviderError):
    """Raised when provider settings are incomplete or invalid."""


class AIProviderRequestError(AIProviderError):
    """Raised when an upstream model request fails."""
