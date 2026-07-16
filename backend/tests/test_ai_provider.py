from typing import Any, cast

import httpx
import pytest
from fastapi import FastAPI

from app.ai.providers import (
    AIProviderError,
    AIProviderRequest,
    FakeAIProvider,
    FakeProviderMode,
    GeminiProvider,
    OpenAICompatibleProvider,
    ProviderErrorCategory,
)
from app.ai.resolver import AIProviderResolver
from app.config import Settings, get_settings
from app.controllers.ai_coach import get_ai_availability_service, router
from app.controllers.auth import get_auth_service, get_current_user
from app.models.ai_provider import AIAvailabilityStatus
from app.models.user import User
from app.services.ai_availability import AIAvailabilityService


def configured_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "mongodb_uri": "mongodb://localhost:27017",
        "mongodb_database": "rahfit_test",
        "jwt_secret_key": "a" * 32,
    }
    values.update(overrides)
    return cast(Any, Settings)(**values)


def authenticated_user() -> User:
    return User(
        id="user-1",
        email="owner@example.com",
        password_hash="hash-never-exposed",
    )


def provider_request() -> AIProviderRequest:
    return AIProviderRequest(
        system_instructions="Return a short safe response.",
        approved_user_content="Approved content only.",
        max_output_tokens=50,
        metadata={"request_id": "request-1"},
    )


def test_ai_configuration_defaults_are_disabled_and_secret_optional() -> None:
    settings = configured_settings()
    assert settings.ai_feature_enabled is False
    assert settings.ai_provider == "gemini"
    assert settings.gemini_api_key is None
    assert settings.gemini_model == "gemini-2.5-flash"
    assert settings.ai_timeout == 15
    assert settings.ai_max_output_tokens == 600


def test_ai_configuration_normalizes_values_and_whitespace_key() -> None:
    settings = configured_settings(
        AI_FEATURE_ENABLED=True,
        AI_PROVIDER="  GEMINI  ",
        GEMINI_API_KEY="   ",
        GEMINI_MODEL="  test-model  ",
    )
    assert settings.ai_provider == "gemini"
    assert settings.gemini_model == "test-model"
    assert settings.gemini_api_key is None

    invalid_flag = configured_settings(AI_FEATURE_ENABLED="not-a-boolean")
    assert invalid_flag.ai_feature_enabled is False


def test_gemini_configuration_uses_dedicated_environment_variables() -> None:
    settings = configured_settings(
        AI_PROVIDER="gemini",
        GEMINI_API_KEY="gemini-test-key",
        GEMINI_MODEL=" gemini-custom-model ",
        AI_TIMEOUT="21",
    )

    assert settings.gemini_api_key is not None
    assert settings.gemini_api_key.get_secret_value() == "gemini-test-key"
    assert settings.gemini_model == "gemini-custom-model"
    assert settings.ai_timeout == 21


def test_legacy_openai_provider_remains_explicitly_configurable() -> None:
    resolution = AIProviderResolver(
        configured_settings(
            AI_FEATURE_ENABLED=True,
            AI_PROVIDER="openai",
            AI_API_KEY="legacy-test-key",
            AI_MODEL="legacy-model",
        )
    ).resolve()

    assert isinstance(resolution.provider, OpenAICompatibleProvider)
    assert resolution.provider_name == "openai"
    assert resolution.model_name == "legacy-model"


@pytest.mark.parametrize(
    ("timeout", "tokens"),
    ((0, 0), (61, 4097), ("invalid", "invalid")),
)
def test_invalid_ai_limits_fall_back_safely_without_breaking_startup(
    timeout: object, tokens: object
) -> None:
    settings = configured_settings(
        AI_TIMEOUT=timeout,
        AI_REQUEST_TIMEOUT_SECONDS=timeout,
        AI_MAX_OUTPUT_TOKENS=tokens,
    )
    assert settings.ai_timeout == 15
    assert settings.ai_request_timeout_seconds == 15
    assert settings.ai_max_output_tokens == 600


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({}, AIAvailabilityStatus.DISABLED),
        ({"AI_FEATURE_ENABLED": True}, AIAvailabilityStatus.SETUP_REQUIRED),
        (
            {"AI_FEATURE_ENABLED": True, "GEMINI_API_KEY": "test-key"},
            AIAvailabilityStatus.AVAILABLE,
        ),
        (
            {"AI_FEATURE_ENABLED": True, "AI_PROVIDER": "unknown", "GEMINI_API_KEY": "key"},
            AIAvailabilityStatus.TEMPORARILY_UNAVAILABLE,
        ),
    ),
)
async def test_availability_states_are_stable_and_local(
    overrides: dict[str, object], expected: AIAvailabilityStatus
) -> None:
    result = await AIAvailabilityService(configured_settings(**overrides)).get_availability()
    assert result.status == expected
    assert "key" not in result.model_dump()


def test_provider_resolver_can_be_overridden_without_global_state() -> None:
    fake = FakeAIProvider()
    resolution = AIProviderResolver(configured_settings(), override=fake).resolve()
    assert resolution.provider is fake
    assert resolution.status == AIAvailabilityStatus.AVAILABLE


def test_fake_provider_cannot_be_selected_from_production_configuration() -> None:
    resolution = AIProviderResolver(
        configured_settings(
            app_env="production",
            AI_FEATURE_ENABLED=True,
            AI_PROVIDER="fake",
            AI_API_KEY="not-used",
        )
    ).resolve()
    assert resolution.provider is None
    assert resolution.status == AIAvailabilityStatus.TEMPORARILY_UNAVAILABLE


@pytest.mark.asyncio
async def test_fake_provider_is_deterministic_and_records_typed_request() -> None:
    fake = FakeAIProvider()
    first = await fake.generate(provider_request())
    second = await fake.generate(provider_request())
    assert first == second
    assert first.text == "Deterministic test response."
    assert first.usage.input_tokens == 8
    assert first.usage.output_tokens == 4
    assert first.usage.total_tokens == 12
    assert len(fake.requests) == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mode", "category"),
    (
        (FakeProviderMode.TIMEOUT, ProviderErrorCategory.TIMEOUT),
        (FakeProviderMode.RATE_LIMITED, ProviderErrorCategory.RATE_LIMITED),
        (FakeProviderMode.UNAVAILABLE, ProviderErrorCategory.UNAVAILABLE),
        (FakeProviderMode.INVALID_RESPONSE, ProviderErrorCategory.INVALID_RESPONSE),
    ),
)
async def test_fake_provider_simulates_stable_failures(
    mode: FakeProviderMode, category: ProviderErrorCategory
) -> None:
    with pytest.raises(AIProviderError) as captured:
        await FakeAIProvider(mode).generate(provider_request())
    assert captured.value.category == category


@pytest.mark.asyncio
async def test_configured_adapter_parses_response_and_token_metadata_defensively() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        return httpx.Response(
            200,
            json={
                "id": "provider-request-1",
                "choices": [{"message": {"content": "Provider response."}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

    provider = OpenAICompatibleProvider(
        api_key="test-only-key",
        model="test-model",
        request_timeout_seconds=5,
        max_output_tokens=100,
        transport=httpx.MockTransport(handler),
    )
    response = await provider.generate(provider_request())
    assert response.text == "Provider response."
    assert response.usage.total_tokens == 15
    assert response.provider_request_id == "provider-request-1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "category"),
    (
        (401, ProviderErrorCategory.AUTHENTICATION_FAILED),
        (429, ProviderErrorCategory.RATE_LIMITED),
        (503, ProviderErrorCategory.UNAVAILABLE),
    ),
)
async def test_configured_adapter_maps_vendor_statuses_to_stable_errors(
    status_code: int, category: ProviderErrorCategory
) -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, request=request)

    provider = OpenAICompatibleProvider(
        api_key="test-only-key",
        model="test-model",
        request_timeout_seconds=5,
        max_output_tokens=100,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(AIProviderError) as captured:
        await provider.generate(provider_request())
    assert captured.value.category == category
    assert "test-only-key" not in str(captured.value)


@pytest.mark.asyncio
async def test_availability_endpoint_is_authenticated_and_secret_free() -> None:
    settings = configured_settings(
        AI_FEATURE_ENABLED=True,
        GEMINI_API_KEY="super-secret-test-key",
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_current_user] = authenticated_user
    app.dependency_overrides[get_ai_availability_service] = lambda: AIAvailabilityService(settings)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/ai-coach/availability")
    assert response.status_code == 200
    assert response.json()["status"] == "available"
    assert "super-secret-test-key" not in response.text


@pytest.mark.asyncio
async def test_availability_endpoint_rejects_guests() -> None:
    settings = configured_settings()
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_auth_service] = lambda: object()
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/ai-coach/availability")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_availability_does_not_call_provider_or_log_api_key(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    settings = configured_settings(
        AI_FEATURE_ENABLED=True,
        GEMINI_API_KEY="never-log-this-key",
    )

    async def forbidden_generate(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Availability must not call the provider.")

    monkeypatch.setattr(GeminiProvider, "generate_text", forbidden_generate)
    result = await AIAvailabilityService(settings).get_availability()
    assert result.status == AIAvailabilityStatus.AVAILABLE
    assert "never-log-this-key" not in caplog.text
