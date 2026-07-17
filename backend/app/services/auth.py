from dataclasses import dataclass
from typing import Any, Protocol

from app.config import Settings
from app.models.user import User
from app.repositories.users import UserAlreadyExistsError
from app.security.google import GooglePayload
from app.security.jwt import TokenPayload, create_token_pair
from app.security.passwords import hash_password, verify_password


class AuthenticationError(Exception):
    """Raised when authentication credentials or tokens are not valid."""


class EmailAlreadyRegisteredError(Exception):
    """Raised when registration would duplicate an existing user."""


class UserStore(Protocol):
    async def create(self, email: str, password_hash: str) -> User: ...

    async def find_by_email(self, email: str) -> User | None: ...

    async def find_by_id(self, user_id: str) -> User | None: ...

    async def find_by_provider(self, provider: str, provider_subject: str) -> User | None: ...

    async def link_google_account(
        self, user_id: str, provider_subject: str, verified_email: str
    ) -> bool: ...

    async def create_google_user(
        self, email: str, display_name: str | None, provider_subject: str
    ) -> User: ...

    async def update_password_and_revoke_tokens(self, user_id: str, password_hash: str) -> bool: ...

    async def increment_token_version(self, user_id: str, expected_version: int) -> User | None: ...


@dataclass(frozen=True)
class AuthResult:
    user: User
    access_token: str
    refresh_token: str


class AuthService:
    """Authentication business rules; controllers only map requests and responses."""

    def __init__(self, users: UserStore, settings: Settings) -> None:
        self.users = users
        self.settings = settings

    async def register(self, email: str, password: str) -> AuthResult:
        if await self.users.find_by_email(email):
            raise EmailAlreadyRegisteredError
        try:
            user = await self.users.create(email, hash_password(password))
        except UserAlreadyExistsError as exc:
            raise EmailAlreadyRegisteredError from exc
        return self._issue_tokens(user)

    async def login(self, email: str, password: str) -> AuthResult:
        user = await self.users.find_by_email(email)
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            raise AuthenticationError
        return self._issue_tokens(user)

    async def refresh(self, payload: TokenPayload) -> AuthResult:
        if payload.token_type != "refresh":
            raise AuthenticationError
        user = await self._validated_user(payload)
        return self._issue_tokens(user)

    async def get_current_user(self, payload: TokenPayload) -> User:
        if payload.token_type != "access":
            raise AuthenticationError
        return await self._validated_user(payload)

    async def logout(self, payload: TokenPayload) -> None:
        user = await self.get_current_user(payload)
        if not await self.users.increment_token_version(user.id, user.token_version):
            raise AuthenticationError

    async def login_google(self, payload: GooglePayload) -> AuthResult:
        # 1. Check if user already exists with Google subject ID
        user = await self.users.find_by_provider("google", payload.sub)
        if user:
            if not user.is_active:
                raise AuthenticationError("This user account is inactive.")
            return self._issue_tokens(user)

        # 2. Check if user already exists with matching email
        user = await self.users.find_by_email(payload.email)
        if user:
            if not user.is_active:
                raise AuthenticationError("This user account is inactive.")
            # Safe linking policy: check if already linked to a different provider/subject
            if user.provider:
                raise AuthenticationError("This email is already associated with another provider.")
            # Link Google account
            linked = await self.users.link_google_account(user.id, payload.sub, payload.email)
            if not linked:
                raise AuthenticationError("Failed to link Google account.")
            # Refetch to get updated model state
            user = await self.users.find_by_id(user.id)
            if not user:
                raise AuthenticationError("Failed to retrieve user after linking.")
            return self._issue_tokens(user)

        # 3. Register a new user via Google
        try:
            user = await self.users.create_google_user(payload.email, payload.name, payload.sub)
        except UserAlreadyExistsError as exc:
            raise AuthenticationError("A user with this email already exists.") from exc
        return self._issue_tokens(user)

    async def forgot_password(self, email: str, resets_repo: Any, email_service: Any) -> None:
        user = await self.users.find_by_email(email)
        if not user or not user.is_active:
            # Silently return to prevent user enumeration
            return

        import hashlib
        import secrets
        from datetime import UTC, datetime, timedelta

        # Cryptographically secure random token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        ttl = self.settings.password_reset_token_ttl_minutes
        expires_at = datetime.now(UTC) + timedelta(minutes=ttl)

        # Invalidate old and save new token
        await resets_repo.create_token(user.id, token_hash, expires_at)

        # Send email
        await email_service.send_password_reset_email(user.email, token)

    async def reset_password(self, token: str, new_password: str, resets_repo: Any) -> None:
        if len(new_password) < 12:
            raise AuthenticationError("Password must be at least 12 characters.")

        import hashlib

        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

        # Find active token
        token_doc = await resets_repo.find_active_token_hash(token_hash)
        if not token_doc:
            raise AuthenticationError("Invalid or expired password reset token.")

        # Atomic consume
        success = await resets_repo.mark_token_used(token_hash)
        if not success:
            raise AuthenticationError("Invalid or expired password reset token.")

        user_id = token_doc["user_id"]
        # Update user password and revoke current active sessions
        updated = await self.users.update_password_and_revoke_tokens(
            user_id, hash_password(new_password)
        )
        if not updated:
            raise AuthenticationError("Failed to update user password.")

    async def _validated_user(self, payload: TokenPayload) -> User:
        user = await self.users.find_by_id(payload.subject)
        if not user or not user.is_active or user.token_version != payload.token_version:
            raise AuthenticationError
        return user

    def _issue_tokens(self, user: User) -> AuthResult:
        access_token, refresh_token = create_token_pair(user.id, user.token_version, self.settings)
        return AuthResult(user=user, access_token=access_token, refresh_token=refresh_token)
