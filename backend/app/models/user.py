from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class User(BaseModel):
    """Authentication domain user; password hashes are never returned by API schemas."""

    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    password_hash: str = Field(repr=False)
    is_active: bool = True
    token_version: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
