from enum import StrEnum
from time import perf_counter
from typing import Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field


class ProviderErrorCategory(StrEnum):
    DISABLED = "provider_disabled"
    NOT_CONFIGURED = "provider_not_configured"
    UNAVAILABLE = "provider_unavailable"
    TIMEOUT = "provider_timeout"
    RATE_LIMITED = "provider_rate_limited"
    INVALID_RESPONSE = "provider_invalid_response"
    AUTHENTICATION_FAILED = "provider_authentication_failure"
    UNEXPECTED = "unexpected_provider_failure"


class ProviderAvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class AIProviderError(Exception):
    """Stable internal provider failure without raw vendor details."""

    def __init__(self, category: ProviderErrorCategory, provider: str, model: str) -> None:
        super().__init__(category.value)
        self.category = category
        self.provider = provider
        self.model = model


class AIProviderRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    system_instructions: str = Field(min_length=1, max_length=10000)
    approved_user_content: str = Field(min_length=1, max_length=30000)
    max_output_tokens: int | None = Field(default=None, ge=1, le=4096)
    metadata: dict[str, str] = Field(default_factory=dict)


class AITokenUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class AIProviderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1, max_length=20000)
    structured_payload: dict[str, object] | None = None
    provider: str
    model: str
    usage: AITokenUsage = Field(default_factory=AITokenUsage)
    latency_ms: int = Field(ge=0)
    provider_request_id: str | None = Field(default=None, max_length=200)


class AIProvider(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def model(self) -> str: ...

    @property
    def request_timeout_seconds(self) -> float: ...

    @property
    def max_output_tokens(self) -> int: ...

    @property
    def availability(self) -> ProviderAvailabilityStatus: ...

    async def generate(self, request: AIProviderRequest) -> AIProviderResponse: ...


class OpenAICompatibleProvider:
    """Provider-neutral adapter boundary around an OpenAI-compatible HTTP API."""

    name = "openai"
    endpoint = "https://api.openai.com/v1/chat/completions"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        request_timeout_seconds: float,
        max_output_tokens: int,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self.model = model
        self.request_timeout_seconds = request_timeout_seconds
        self.max_output_tokens = max_output_tokens
        self._transport = transport

    @property
    def availability(self) -> ProviderAvailabilityStatus:
        return ProviderAvailabilityStatus.AVAILABLE

    async def generate(self, request: AIProviderRequest) -> AIProviderResponse:
        started = perf_counter()
        token_limit = min(
            request.max_output_tokens or self.max_output_tokens, self.max_output_tokens
        )
        try:
            async with httpx.AsyncClient(
                timeout=self.request_timeout_seconds, transport=self._transport
            ) as client:
                response = await client.post(
                    self.endpoint,
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": request.system_instructions},
                            {"role": "user", "content": request.approved_user_content},
                        ],
                        "max_tokens": token_limit,
                    },
                )
        except httpx.TimeoutException as exc:
            raise self._error(ProviderErrorCategory.TIMEOUT) from exc
        except httpx.HTTPError as exc:
            raise self._error(ProviderErrorCategory.UNAVAILABLE) from exc
        except Exception as exc:
            raise self._error(ProviderErrorCategory.UNEXPECTED) from exc

        if response.status_code in {401, 403}:
            raise self._error(ProviderErrorCategory.AUTHENTICATION_FAILED)
        if response.status_code == 429:
            raise self._error(ProviderErrorCategory.RATE_LIMITED)
        if response.status_code >= 500:
            raise self._error(ProviderErrorCategory.UNAVAILABLE)
        if response.status_code >= 400:
            raise self._error(ProviderErrorCategory.UNEXPECTED)
        try:
            payload = response.json()
            text = payload["choices"][0]["message"]["content"]
            if not isinstance(text, str) or not text.strip():
                raise ValueError
            usage = payload.get("usage") if isinstance(payload, dict) else None
            usage = usage if isinstance(usage, dict) else {}
            request_id = payload.get("id") if isinstance(payload, dict) else None
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise self._error(ProviderErrorCategory.INVALID_RESPONSE) from exc
        return AIProviderResponse(
            text=text.strip(),
            provider=self.name,
            model=self.model,
            usage=AITokenUsage(
                input_tokens=self._non_negative_int(usage.get("prompt_tokens")),
                output_tokens=self._non_negative_int(usage.get("completion_tokens")),
                total_tokens=self._non_negative_int(usage.get("total_tokens")),
            ),
            latency_ms=round((perf_counter() - started) * 1000),
            provider_request_id=request_id if isinstance(request_id, str) else None,
        )

    def _error(self, category: ProviderErrorCategory) -> AIProviderError:
        return AIProviderError(category, self.name, self.model)

    @staticmethod
    def _non_negative_int(value: object) -> int | None:
        return value if isinstance(value, int) and value >= 0 else None


class FakeProviderMode(StrEnum):
    SUCCESS = "success"
    TIMEOUT = "timeout"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"
    INVALID_RESPONSE = "invalid_response"


class FakeAIProvider:
    """Deterministic provider for explicit test injection only."""

    name = "fake"
    model = "fake-deterministic-model"
    request_timeout_seconds = 1.0
    max_output_tokens = 100
    availability = ProviderAvailabilityStatus.AVAILABLE

    def __init__(self, mode: FakeProviderMode = FakeProviderMode.SUCCESS) -> None:
        self.mode = mode
        self.requests: list[AIProviderRequest] = []

    async def generate(self, request: AIProviderRequest) -> AIProviderResponse:
        self.requests.append(request)
        categories = {
            FakeProviderMode.TIMEOUT: ProviderErrorCategory.TIMEOUT,
            FakeProviderMode.RATE_LIMITED: ProviderErrorCategory.RATE_LIMITED,
            FakeProviderMode.UNAVAILABLE: ProviderErrorCategory.UNAVAILABLE,
            FakeProviderMode.INVALID_RESPONSE: ProviderErrorCategory.INVALID_RESPONSE,
        }
        if self.mode in categories:
            raise AIProviderError(categories[self.mode], self.name, self.model)
        return AIProviderResponse(
            text="Deterministic test response.",
            provider=self.name,
            model=self.model,
            usage=AITokenUsage(input_tokens=8, output_tokens=4, total_tokens=12),
            latency_ms=1,
            provider_request_id="fake-request-1",
        )
