from enum import StrEnum

from pydantic import ValidationError

from app.ai.exceptions import (
    AIProviderError,
    AITimeoutError,
    AIValidationError,
    ProviderErrorCategory,
)
from app.ai.provider import (
    AIProvider,
    AIProviderRequest,
    AIProviderResponse,
    AITokenUsage,
    ProviderAvailabilityStatus,
    ResponseModelT,
)


class MockProviderMode(StrEnum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"


class MockProvider(AIProvider):
    """Deterministic, network-free provider available only through explicit injection."""

    def __init__(
        self,
        mode: MockProviderMode = MockProviderMode.SUCCESS,
        *,
        text: str = "Deterministic test response.",
        structured_payload: dict[str, object] | None = None,
    ) -> None:
        self.mode = mode
        self.text = text
        self.structured_payload = structured_payload
        self.requests: list[AIProviderRequest] = []

    @property
    def name(self) -> str:
        return "mock"

    @property
    def model(self) -> str:
        return "mock-deterministic-model"

    @property
    def request_timeout_seconds(self) -> float:
        return 1.0

    @property
    def max_output_tokens(self) -> int:
        return 100

    @property
    def availability(self) -> ProviderAvailabilityStatus:
        return ProviderAvailabilityStatus.AVAILABLE

    async def generate_text(self, request: AIProviderRequest) -> AIProviderResponse:
        self._record_or_raise(request)
        return self._response()

    async def generate_json(
        self,
        request: AIProviderRequest,
        response_model: type[ResponseModelT],
    ) -> AIProviderResponse:
        self._record_or_raise(request)
        try:
            validated = response_model.model_validate(self.structured_payload or {})
        except ValidationError as exc:
            raise AIValidationError(self.name, self.model) from exc
        return self._response(structured_payload=validated.model_dump())

    async def health_check(self) -> bool:
        return self.mode not in {MockProviderMode.TIMEOUT, MockProviderMode.UNAVAILABLE}

    def _record_or_raise(self, request: AIProviderRequest) -> None:
        self.requests.append(request)
        if self.mode == MockProviderMode.TIMEOUT:
            raise AITimeoutError(self.name, self.model)
        categories = {
            MockProviderMode.RATE_LIMITED: ProviderErrorCategory.RATE_LIMITED,
            MockProviderMode.UNAVAILABLE: ProviderErrorCategory.UNAVAILABLE,
            MockProviderMode.INVALID_RESPONSE: ProviderErrorCategory.INVALID_RESPONSE,
        }
        if self.mode in categories:
            raise AIProviderError(categories[self.mode], self.name, self.model)

    def _response(
        self,
        *,
        structured_payload: dict[str, object] | None = None,
    ) -> AIProviderResponse:
        return AIProviderResponse(
            text=self.text,
            structured_payload=structured_payload,
            provider=self.name,
            model=self.model,
            usage=AITokenUsage(input_tokens=8, output_tokens=4, total_tokens=12),
            latency_ms=1,
            provider_request_id="mock-request-1",
        )


# Backward-compatible names for the original provider infrastructure.
FakeAIProvider = MockProvider
FakeProviderMode = MockProviderMode
