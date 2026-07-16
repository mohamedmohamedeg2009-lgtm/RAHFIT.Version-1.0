from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.controllers.auth import get_auth_service, router
from app.models.user import User
from app.security.jwt import create_access_token, create_refresh_token, decode_token
from app.services.auth import AuthenticationError, AuthService, EmailAlreadyRegisteredError


class FakeUserStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def create(self, email: str, password_hash: str) -> User:
        if await self.find_by_email(email):
            from app.repositories.users import UserAlreadyExistsError

            raise UserAlreadyExistsError
        user = User(
            id=str(len(self.users) + 1),
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.users[user.id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def find_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def increment_token_version(self, user_id: str, expected_version: int) -> User | None:
        user = self.users.get(user_id)
        if not user or user.token_version != expected_version:
            return None
        updated = user.model_copy(
            update={"token_version": user.token_version + 1, "updated_at": datetime.now(UTC)}
        )
        self.users[user_id] = updated
        return updated


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )


@pytest.mark.asyncio
async def test_register_login_refresh_and_logout_invalidates_tokens(settings: Settings) -> None:
    store = FakeUserStore()
    service = AuthService(store, settings)

    registered = await service.register("User@Example.com".lower(), "secure-password-123")
    access_payload = decode_token(registered.access_token, settings)
    refresh_payload = decode_token(registered.refresh_token, settings)

    assert access_payload.token_type == "access"
    assert refresh_payload.token_type == "refresh"
    assert (await service.get_current_user(access_payload)).email == "user@example.com"

    refreshed = await service.refresh(refresh_payload)
    await service.logout(decode_token(refreshed.access_token, settings))

    with pytest.raises(AuthenticationError):
        await service.get_current_user(access_payload)
    with pytest.raises(AuthenticationError):
        await service.refresh(refresh_payload)


@pytest.mark.asyncio
async def test_register_rejects_duplicate_and_login_rejects_wrong_password(
    settings: Settings,
) -> None:
    service = AuthService(FakeUserStore(), settings)
    await service.register("user@example.com", "secure-password-123")

    with pytest.raises(EmailAlreadyRegisteredError):
        await service.register("user@example.com", "secure-password-123")
    with pytest.raises(AuthenticationError):
        await service.login("user@example.com", "incorrect-password-123")


def test_token_type_cannot_be_used_for_another_flow(settings: Settings) -> None:
    access = create_access_token("user-id", settings)
    refresh = create_refresh_token("user-id", 0, settings)

    assert decode_token(access, settings).token_type == "access"
    assert decode_token(refresh, settings).token_type == "refresh"


def test_authentication_endpoints_support_the_core_session_flow(settings: Settings) -> None:
    service = AuthService(FakeUserStore(), settings)
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_auth_service] = lambda: service
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "secure-password-123"},
    )
    assert registration.status_code == 201
    tokens = registration.json()
    authorization = {"Authorization": f"Bearer {tokens['access_token']}"}

    current_user = client.get("/api/v1/auth/me", headers=authorization)
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "user@example.com"

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "secure-password-123"},
    )
    assert duplicate.status_code == 409
    assert "password" not in duplicate.text.lower()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "secure-password-123"},
    )
    assert login.status_code == 200

    invalid_login = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "incorrect-password-123"},
    )
    assert invalid_login.status_code == 401
    assert "password" not in invalid_login.text.lower()

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200

    logout = client.post("/api/v1/auth/logout", headers=authorization)
    assert logout.status_code == 200
    assert client.get("/api/v1/auth/me", headers=authorization).status_code == 401
