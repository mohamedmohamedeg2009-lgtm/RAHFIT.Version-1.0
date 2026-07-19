from dataclasses import dataclass
from typing import Protocol

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

    async def _validated_user(self, payload: TokenPayload) -> User:
        user = await self.users.find_by_id(payload.subject)
        if not user or not user.is_active or user.token_version != payload.token_version:
            raise AuthenticationError
        return user

    def _issue_tokens(self, user: User) -> AuthResult:
        access_token, refresh_token = create_token_pair(user.id, user.token_version, self.settings)
        return AuthResult(user=user, access_token=access_token, refresh_token=refresh_token)
