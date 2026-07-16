from app.ai.resolver import AIProviderResolver
from app.config import Settings
from app.models.ai_provider import AIAvailability, AIAvailabilityStatus


class AIAvailabilityService:
    """Report configuration-derived availability without calling an external provider."""

    MESSAGES = {
        AIAvailabilityStatus.DISABLED: "AI features are disabled in this environment.",
        AIAvailabilityStatus.SETUP_REQUIRED: "AI provider setup is required.",
        AIAvailabilityStatus.AVAILABLE: "AI provider infrastructure is available.",
        AIAvailabilityStatus.TEMPORARILY_UNAVAILABLE: (
            "AI provider infrastructure is temporarily unavailable."
        ),
    }

    def __init__(self, settings: Settings, resolver: AIProviderResolver | None = None) -> None:
        self.settings = settings
        self.resolver = resolver or AIProviderResolver(settings)

    async def get_availability(self) -> AIAvailability:
        resolution = self.resolver.resolve()
        return AIAvailability(
            feature_enabled=self.settings.ai_feature_enabled,
            status=resolution.status,
            provider=resolution.provider_name,
            model=resolution.model_name,
            reason_code=resolution.reason_code,
            message=self.MESSAGES[resolution.status],
        )
