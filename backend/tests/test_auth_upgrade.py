from datetime import UTC, datetime
from typing import Any

import pytest

from app.config import Settings
from app.models.user import User
from app.security.google import GooglePayload
from app.services.auth import AuthenticationError, AuthService


class UpgradeFakeUserStore:
    def __init__(self) -> None:
        self.users: dict[str, User] = {}

    async def create(self, email: str, password_hash: str) -> User:
        user = User(
            id=str(len(self.users) + 1),
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.users[user.id] = user
        return user

    async def create_google_user(
        self, email: str, display_name: str | None, provider_subject: str
    ) -> User:
        user = User(
            id=str(len(self.users) + 1),
            email=email,
            password_hash="",
            display_name=display_name,
            provider="google",
            provider_subject=provider_subject,
            verified_email=email,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.users[user.id] = user
        return user

    async def find_by_email(self, email: str) -> User | None:
        return next((user for user in self.users.values() if user.email == email), None)

    async def find_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def find_by_provider(self, provider: str, provider_subject: str) -> User | None:
        return next(
            (
                user
                for user in self.users.values()
                if user.provider == provider and user.provider_subject == provider_subject
            ),
            None,
        )

    async def link_google_account(
        self, user_id: str, provider_subject: str, verified_email: str
    ) -> bool:
        user = self.users.get(user_id)
        if not user:
            return False
        updated = user.model_copy(
            update={
                "provider": "google",
                "provider_subject": provider_subject,
                "verified_email": verified_email,
                "updated_at": datetime.now(UTC),
            }
        )
        self.users[user_id] = updated
        return True

    async def update_password_and_revoke_tokens(self, user_id: str, password_hash: str) -> bool:
        user = self.users.get(user_id)
        if not user:
            return False
        updated = user.model_copy(
            update={
                "password_hash": password_hash,
                "token_version": user.token_version + 1,
                "updated_at": datetime.now(UTC),
            }
        )
        self.users[user_id] = updated
        return True

    async def increment_token_version(self, user_id: str, expected_version: int) -> User | None:
        user = self.users.get(user_id)
        if not user or user.token_version != expected_version:
            return None
        updated = user.model_copy(
            update={"token_version": user.token_version + 1, "updated_at": datetime.now(UTC)}
        )
        self.users[user_id] = updated
        return updated


class FakePasswordResetRepository:
    def __init__(self) -> None:
        self.tokens: list[dict[str, Any]] = []

    async def create_token(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        # Invalidate old
        for t in self.tokens:
            if t["user_id"] == user_id:
                t["used_at"] = datetime.now(UTC)
        self.tokens.append(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "used_at": None,
                "created_at": datetime.now(UTC),
            }
        )

    async def find_active_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        now = datetime.now(UTC)
        return next(
            (
                t
                for t in self.tokens
                if t["token_hash"] == token_hash and t["used_at"] is None and t["expires_at"] > now
            ),
            None,
        )

    async def mark_token_used(self, token_hash: str) -> bool:
        for t in self.tokens:
            if t["token_hash"] == token_hash and t["used_at"] is None:
                t["used_at"] = datetime.now(UTC)
                return True
        return False


class FakeEmailService:
    def __init__(self) -> None:
        self.sent_mails: list[dict[str, Any]] = []

    async def send_password_reset_email(self, to_email: str, token: str) -> None:
        self.sent_mails.append({"to": to_email, "token": token})


@pytest.fixture
def auth_upgrade_settings() -> Settings:
    return Settings(
        _env_file=None,
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
        google_client_id="test-client-id",
        password_reset_token_ttl_minutes=15,
        email_provider="development",
    )


@pytest.mark.asyncio
async def test_google_login_new_user(auth_upgrade_settings: Settings) -> None:
    store = UpgradeFakeUserStore()
    service = AuthService(store, auth_upgrade_settings)

    payload = GooglePayload(
        sub="google-sub-123",
        email="test-google@example.com",
        email_verified=True,
        name="Google User",
    )

    result = await service.login_google(payload)
    assert result.user.email == "test-google@example.com"
    assert result.user.provider == "google"
    assert result.user.provider_subject == "google-sub-123"


@pytest.mark.asyncio
async def test_google_login_existing_linking(auth_upgrade_settings: Settings) -> None:
    store = UpgradeFakeUserStore()
    service = AuthService(store, auth_upgrade_settings)

    # Register via email/password first
    await service.register("linked@example.com", "secure-password-123")

    payload = GooglePayload(
        sub="google-sub-linked",
        email="linked@example.com",
        email_verified=True,
        name="Linked User",
    )

    result = await service.login_google(payload)
    assert result.user.email == "linked@example.com"
    assert result.user.provider == "google"
    assert result.user.provider_subject == "google-sub-linked"


@pytest.mark.asyncio
async def test_forgot_and_reset_password_flow(auth_upgrade_settings: Settings) -> None:
    store = UpgradeFakeUserStore()
    service = AuthService(store, auth_upgrade_settings)
    resets_repo = FakePasswordResetRepository()
    email_service = FakeEmailService()

    # Create user
    user = await service.register("reset@example.com", "secure-password-123")
    old_hash = store.users[user.user.id].password_hash

    # Request reset
    await service.forgot_password("reset@example.com", resets_repo, email_service)
    assert len(email_service.sent_mails) == 1
    token = email_service.sent_mails[0]["token"]

    # Invalidate old password
    await service.reset_password(token, "new-password-987", resets_repo)
    new_hash = store.users[user.user.id].password_hash

    assert old_hash != new_hash
    # Check that token is marked used/inactive
    assert len(resets_repo.tokens) == 1
    assert resets_repo.tokens[0]["used_at"] is not None

    # Try to reuse token - should fail
    with pytest.raises(AuthenticationError):
        await service.reset_password(token, "another-password-111", resets_repo)
