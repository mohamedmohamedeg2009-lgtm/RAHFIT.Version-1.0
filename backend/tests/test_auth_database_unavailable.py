from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.controllers.auth import router


def test_auth_login_returns_503_when_database_is_unavailable() -> None:
    settings = Settings(
        _env_file=None,
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )

    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.state.database = SimpleNamespace()
    app.dependency_overrides[get_settings] = lambda: settings

    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "secure-password-123"},
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "database_unavailable"
