import pytest
from fastapi import FastAPI
from fastapi.routing import APIRoute
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


def test_cors_origins_are_parsed_from_the_production_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "https://app.example.com/, https://preview.example.com/ ",
    )

    settings = Settings(_env_file=None)

    assert settings.allowed_origins == ["https://app.example.com", "https://preview.example.com"]


@pytest.mark.parametrize("origins", ("", " , ", "https://app.example.com,*"))
def test_cors_configuration_rejects_empty_or_wildcard_origins(
    origins: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("ALLOWED_ORIGINS", origins)

    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS"):
        Settings(_env_file=None)


def test_auth_routes_remain_registered_in_the_application_router() -> None:
    paths = {route.path for route in router.routes if isinstance(route, APIRoute)}

    assert {"/auth/register", "/auth/login", "/auth/refresh", "/auth/me", "/auth/logout"} <= paths


def test_health_route_reports_database_readiness_without_exposing_details(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    get_settings.cache_clear()
    from app.main import create_app

    class Admin:
        async def command(self, name: str) -> dict[str, int]:
            assert name == "ping"
            return {"ok": 1}

    class Client:
        admin = Admin()

    class Database:
        client = Client()

    app = create_app()
    app.state.database = Database()
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_health_route_returns_safe_database_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)
    get_settings.cache_clear()
    from app.main import create_app

    response = TestClient(create_app()).get("/health")

    assert response.status_code == 503
    assert response.json()["code"] == "database_unavailable"
    get_settings.cache_clear()


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


def test_invalid_ai_feature_flag_is_rejected_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("AI_FEATURE_ENABLED", "enabled-maybe")

    with pytest.raises(ValidationError, match="AI_FEATURE_ENABLED"):
        Settings(_env_file=None)


def test_production_rejects_development_secrets_and_email_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "replace-with-a-long-random-secret-at-least-32-characters")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")
    monkeypatch.setenv("EMAIL_PROVIDER", "smtp")
    monkeypatch.setenv("PASSWORD_RESET_URL", "https://app.example.com/reset-password")

    with pytest.raises(ValidationError, match="JWT_SECRET_KEY"):
        Settings(_env_file=None)


def test_production_requires_smtp_and_secure_reset_url(monkeypatch: pytest.MonkeyPatch) -> None:
    required_environment(monkeypatch)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv(
        "JWT_SECRET_KEY", "prod-test-secret-A7!x9#q2$Lm4%Rv6^Tw8&Yz0*Bc3+De5=Fg7_Hj9-Kn1"
    )
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://app.example.com")

    with pytest.raises(ValidationError, match="EMAIL_PROVIDER"):
        Settings(_env_file=None)


@pytest.mark.asyncio
async def test_lifespan_closes_mongodb_when_index_initialization_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    required_environment(monkeypatch)
    get_settings.cache_clear()
    from app import main

    class Database:
        database = object()
        disconnected = False

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            self.disconnected = True

    database = Database()

    async def fail_index_initialization(_: object) -> None:
        raise RuntimeError("index creation failed")

    monkeypatch.setattr(main, "MongoDatabase", lambda _: database)
    monkeypatch.setattr(main, "initialize_indexes", fail_index_initialization)

    with pytest.raises(RuntimeError, match="index creation failed"):
        async with main.lifespan(FastAPI()):
            pass

    assert database.disconnected is True
    get_settings.cache_clear()


def test_ai_provider_and_conversation_routes_exclude_public_messages() -> None:
    ai_paths = {
        route.path
        for route in router.routes
        if isinstance(route, APIRoute) and route.path.startswith("/ai-coach")
    }
    assert ai_paths == {
        "/ai-coach/availability",
        "/ai-coach/conversations",
        "/ai-coach/conversations/{conversation_id}",
        "/ai-coach/conversations/{conversation_id}/close",
    }


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
