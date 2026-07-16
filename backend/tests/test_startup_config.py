import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.api.router import router
from app.config.settings import Settings, get_settings


def required_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "rahfit_test")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)


def test_unrelated_debug_environment_does_not_break_startup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("DEBUG", "release")
    monkeypatch.delenv("RAHFIT_DEBUG", raising=False)

    settings = Settings(_env_file=None)

    assert settings.debug is False


def test_invalid_namespaced_debug_is_rejected_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("RAHFIT_DEBUG", "release")

    with pytest.raises(ValidationError, match="RAHFIT_DEBUG|app_debug|bool"):
        Settings(_env_file=None)


def test_local_cors_defaults_are_explicit_and_credential_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    settings = Settings(_env_file=None)

    assert set(settings.allowed_origins) == {
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    }
    assert "*" not in settings.allowed_origins


def test_auth_routes_remain_registered_in_the_application_router() -> None:
    paths = {route.path for route in router.routes}

    assert {"/auth/register", "/auth/login", "/auth/refresh", "/auth/me", "/auth/logout"} <= paths


def test_backend_configuration_starts_without_ai_key_when_ai_is_disabled_or_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.delenv("AI_API_KEY", raising=False)

    monkeypatch.setenv("AI_FEATURE_ENABLED", "false")
    disabled = Settings(_env_file=None)
    monkeypatch.setenv("AI_FEATURE_ENABLED", "true")
    setup_required = Settings(_env_file=None)

    assert disabled.ai_feature_enabled is False
    assert disabled.ai_api_key is None
    assert setup_required.ai_feature_enabled is True
    assert setup_required.ai_api_key is None


def test_only_ai_availability_route_is_registered() -> None:
    ai_paths = {route.path for route in router.routes if route.path.startswith("/ai-coach")}
    assert ai_paths == {"/ai-coach/availability"}


@pytest.mark.parametrize(
    "origin",
    (
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ),
)
def test_cors_middleware_accepts_each_configured_vite_origin(
    origin: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    required_environment(monkeypatch)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    get_settings.cache_clear()
    from app.main import create_app

    response = TestClient(create_app()).options(
        "/api/v1/auth/register",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"
    get_settings.cache_clear()
