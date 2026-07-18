from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from uuid import uuid4

import jwt

from app.config import Settings


@dataclass(frozen=True)
class TokenPayload:
    subject: str
    token_type: Literal["access", "refresh"]
    token_version: int


class TokenValidationError(Exception):
    """Raised when a JWT cannot be trusted for an authentication action."""


def _create_token(
    subject: str,
    token_type: Literal["access", "refresh"],
    token_version: int,
    expires_at: datetime,
    settings: Settings,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": datetime.now(UTC),
        "exp": expires_at,
        "typ": token_type,
        "ver": token_version,
        "jti": str(uuid4()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(
        payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm
    )


def create_access_token(
    subject: str,
    settings: Settings,
    token_version: int = 0,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    return _create_token(
        subject,
        "access",
        token_version,
        datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes),
        settings,
        extra_claims,
    )


def create_refresh_token(subject: str, token_version: int, settings: Settings) -> str:
    return _create_token(
        subject,
        "refresh",
        token_version,
        datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days),
        settings,
    )


def create_token_pair(subject: str, token_version: int, settings: Settings) -> tuple[str, str]:
    return (
        create_access_token(subject, settings, token_version=token_version),
        create_refresh_token(subject, token_version, settings),
    )


def decode_token(token: str, settings: Settings) -> TokenPayload:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "iat", "exp", "typ", "ver"]},
        )
        subject = payload["sub"]
        token_type = payload["typ"]
        token_version = payload["ver"]
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise TokenValidationError from exc
    if not isinstance(subject, str) or token_type not in {"access", "refresh"}:
        raise TokenValidationError
    if not isinstance(token_version, int) or token_version < 0:
        raise TokenValidationError
    return TokenPayload(subject=subject, token_type=token_type, token_version=token_version)
