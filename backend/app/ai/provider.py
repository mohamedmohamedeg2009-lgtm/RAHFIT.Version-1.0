from abc import ABC, abstractmethod
from enum import StrEnum
from typing import TypeVar

from pydantic import BaseModel, ConfigDict, Field


class ProviderAvailabilityStatus(StrEnum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"


class AIProviderRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    system_instructions: str = Field(min_length=1, max_length=10_000)
    approved_user_content: str = Field(min_length=1, max_length=30_000)
    max_output_tokens: int | None = Field(default=None, ge=1, le=4_096)
    metadata: dict[str, str] = Field(default_factory=dict)


class AITokenUsage(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class AIProviderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    text: str = Field(min_length=1, max_length=20_000)
    structured_payload: dict[str, object] | None = None
    provider: str
    model: str
    usage: AITokenUsage = Field(default_factory=AITokenUsage)
    latency_ms: int = Field(ge=0)
    provider_request_id: str | None = Field(default=None, max_length=200)


ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)


class AIProvider(ABC):
    """Provider-neutral generation boundary used only by AIService."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def model(self) -> str: ...

    @property
    @abstractmethod
    def request_timeout_seconds(self) -> float: ...

    @property
    @abstractmethod
    def max_output_tokens(self) -> int: ...

    @property
    @abstractmethod
    def availability(self) -> ProviderAvailabilityStatus: ...

    @abstractmethod
    async def generate_text(self, request: AIProviderRequest) -> AIProviderResponse: ...

    @abstractmethod
    async def generate_json(
        self,
        request: AIProviderRequest,
        response_model: type[ResponseModelT],
    ) -> AIProviderResponse: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    async def generate(self, request: AIProviderRequest) -> AIProviderResponse:
        """Compatibility alias for the original provider contract."""

        return await self.generate_text(request)
