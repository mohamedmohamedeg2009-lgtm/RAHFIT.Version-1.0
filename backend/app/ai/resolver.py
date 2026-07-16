from dataclasses import dataclass

from app.ai.provider import AIProvider
from app.ai.providers import GeminiProvider, OpenAICompatibleProvider
from app.config import Settings
from app.models.ai_provider import AIAvailabilityStatus


@dataclass(frozen=True)
class ProviderResolution:
    provider: AIProvider | None
    status: AIAvailabilityStatus
    provider_name: str | None
    model_name: str | None
    reason_code: str


class AIProviderResolver:
    """Resolve configuration and adapters locally without making a provider request."""

    def __init__(self, settings: Settings, override: AIProvider | None = None) -> None:
        self.settings = settings
        self.override = override

    def resolve(self) -> ProviderResolution:
        if self.override is not None:
            return ProviderResolution(
                provider=self.override,
                status=AIAvailabilityStatus.AVAILABLE,
                provider_name=self.override.name,
                model_name=self.override.model,
                reason_code="ai_provider_available",
            )
        if not self.settings.ai_feature_enabled:
            return ProviderResolution(
                provider=None,
                status=AIAvailabilityStatus.DISABLED,
                provider_name=None,
                model_name=None,
                reason_code="ai_feature_disabled",
            )
        if self.settings.ai_provider not in {"gemini", "openai"}:
            return ProviderResolution(
                provider=None,
                status=AIAvailabilityStatus.TEMPORARILY_UNAVAILABLE,
                provider_name=self.settings.ai_provider or None,
                model_name=self.settings.ai_model,
                reason_code="ai_provider_unsupported",
            )
        key = (
            self.settings.gemini_api_key
            if self.settings.ai_provider == "gemini"
            else self.settings.ai_api_key
        )
        if key is None or not key.get_secret_value().strip():
            return ProviderResolution(
                provider=None,
                status=AIAvailabilityStatus.SETUP_REQUIRED,
                provider_name=self.settings.ai_provider,
                model_name=(
                    self.settings.gemini_model
                    if self.settings.ai_provider == "gemini"
                    else self.settings.ai_model
                ),
                reason_code="ai_provider_setup_required",
            )
        if self.settings.ai_provider == "gemini":
            provider: AIProvider = GeminiProvider(
                api_key=key.get_secret_value(),
                model=self.settings.gemini_model,
                request_timeout_seconds=self.settings.ai_timeout,
                max_output_tokens=self.settings.ai_max_output_tokens,
            )
        else:
            provider = OpenAICompatibleProvider(
                api_key=key.get_secret_value(),
                model=self.settings.ai_model,
                request_timeout_seconds=self.settings.ai_request_timeout_seconds,
                max_output_tokens=self.settings.ai_max_output_tokens,
            )
        return ProviderResolution(
            provider=provider,
            status=AIAvailabilityStatus.AVAILABLE,
            provider_name=provider.name,
            model_name=provider.model,
            reason_code="ai_provider_available",
        )
