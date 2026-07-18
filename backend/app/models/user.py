from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Authentication domain user; password hashes are never returned by API schemas."""

    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    password_hash: str = Field(repr=False)
    display_name: str | None = None
    preferred_units: str | None = None
    is_active: bool = True
    role: Literal["user", "admin"] = "user"
    token_version: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    provider: str | None = None
    provider_subject: str | None = None
    verified_email: str | None = None
