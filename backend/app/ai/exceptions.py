from enum import StrEnum


class ProviderErrorCategory(StrEnum):
    DISABLED = "provider_disabled"
    NOT_CONFIGURED = "provider_not_configured"
    UNAVAILABLE = "provider_unavailable"
    TIMEOUT = "provider_timeout"
    RATE_LIMITED = "provider_rate_limited"
    INVALID_RESPONSE = "provider_invalid_response"
    AUTHENTICATION_FAILED = "provider_authentication_failure"
    UNEXPECTED = "unexpected_provider_failure"


class AIProviderError(Exception):
    """Stable provider failure that never exposes raw vendor details."""

    def __init__(self, category: ProviderErrorCategory, provider: str, model: str) -> None:
        super().__init__(category.value)
        self.category = category
        self.provider = provider
        self.model = model


class AITimeoutError(AIProviderError):
    def __init__(self, provider: str, model: str) -> None:
        super().__init__(ProviderErrorCategory.TIMEOUT, provider, model)


class AIValidationError(AIProviderError):
    def __init__(
        self,
        provider: str,
        model: str,
        reason_code: str = "ai_output_validation_failed",
    ) -> None:
        super().__init__(ProviderErrorCategory.INVALID_RESPONSE, provider, model)
        self.reason_code = reason_code


class AISafetyError(Exception):
    """Generation was rejected by the deterministic pre-generation safety boundary."""

    def __init__(self, reason_code: str) -> None:
        super().__init__("ai_safety_rejected")
        self.reason_code = reason_code
