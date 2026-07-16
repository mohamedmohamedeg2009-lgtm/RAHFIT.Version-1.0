from dataclasses import dataclass
from typing import Any, cast

import pytest
from google.genai import errors, types
from pydantic import BaseModel, ConfigDict

from app.ai.exceptions import (
    AIProviderError,
    AITimeoutError,
    AIValidationError,
    ProviderErrorCategory,
)
from app.ai.provider import AIProviderRequest
from app.ai.providers import GeminiProvider


class StructuredAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str
    score: int


@dataclass
class FakeUsage:
    prompt_token_count: int | None = 11
    candidates_token_count: int | None = 7
    total_token_count: int | None = 18


@dataclass
class FakeResponse:
    text: str | None
    parsed: object = None
    usage_metadata: FakeUsage | None = None
    response_id: str | None = "gemini-request-1"


class FakeModels:
    def __init__(
        self,
        response: FakeResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.response = response or FakeResponse("Safe response.", usage_metadata=FakeUsage())
        self.error = error
        self.calls: list[dict[str, object]] = []

    async def generate_content(self, **kwargs: object) -> FakeResponse:
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.response

    async def get(self, *, model: str) -> object:
        if self.error is not None:
            raise self.error
        return {"name": model}


class FakeClient:
    def __init__(self, models: FakeModels) -> None:
        self.models = models


def provider(models: FakeModels) -> GeminiProvider:
    return GeminiProvider(
        api_key="test-key-never-logged",
        model="gemini-test-model",
        request_timeout_seconds=5,
        max_output_tokens=200,
        client=cast(Any, FakeClient(models)),
    )


def request() -> AIProviderRequest:
    return AIProviderRequest(
        system_instructions="Return safe content.",
        approved_user_content='{"sections":[]}',
        max_output_tokens=80,
        metadata={"request_id": "request-1"},
    )


@pytest.mark.asyncio
async def test_gemini_provider_generates_text_with_configured_bounds() -> None:
    models = FakeModels()

    result = await provider(models).generate_text(request())

    assert result.text == "Safe response."
    assert result.provider == "gemini"
    assert result.model == "gemini-test-model"
    assert result.usage.total_tokens == 18
    assert result.provider_request_id == "gemini-request-1"
    assert len(models.calls) == 1
    call = models.calls[0]
    assert call["model"] == "gemini-test-model"
    assert call["contents"] == '{"sections":[]}'
    config = cast(types.GenerateContentConfig, call["config"])
    assert config.max_output_tokens == 80
    assert config.system_instruction == "Return safe content."


@pytest.mark.asyncio
async def test_gemini_provider_requests_and_validates_structured_output() -> None:
    parsed = StructuredAnswer(message="Approved answer.", score=91)
    models = FakeModels(
        FakeResponse(
            text=parsed.model_dump_json(),
            parsed=parsed,
            usage_metadata=FakeUsage(),
        )
    )

    result = await provider(models).generate_json(request(), StructuredAnswer)

    assert result.structured_payload == {"message": "Approved answer.", "score": 91}
    config = cast(types.GenerateContentConfig, models.calls[0]["config"])
    assert config.response_mime_type == "application/json"
    assert config.response_schema is StructuredAnswer


@pytest.mark.asyncio
async def test_gemini_provider_rejects_invalid_structured_output() -> None:
    models = FakeModels(FakeResponse(text='{"message":"missing score"}'))

    with pytest.raises(AIValidationError):
        await provider(models).generate_json(request(), StructuredAnswer)


@pytest.mark.asyncio
async def test_gemini_provider_maps_timeout_and_rate_limit_without_secret_leak() -> None:
    timeout_provider = provider(FakeModels(error=TimeoutError()))
    with pytest.raises(AITimeoutError) as timeout:
        await timeout_provider.generate_text(request())
    assert timeout.value.category == ProviderErrorCategory.TIMEOUT

    rate_provider = provider(
        FakeModels(error=errors.ClientError(429, {"error": {"message": "test-key"}}))
    )
    with pytest.raises(AIProviderError) as rate_limit:
        await rate_provider.generate_text(request())
    assert rate_limit.value.category == ProviderErrorCategory.RATE_LIMITED
    assert "test-key-never-logged" not in str(rate_limit.value)


@pytest.mark.asyncio
async def test_gemini_health_check_is_isolated_and_non_throwing() -> None:
    assert await provider(FakeModels()).health_check() is True
    assert await provider(FakeModels(error=RuntimeError("offline"))).health_check() is False
