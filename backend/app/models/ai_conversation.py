from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS

CONVERSATION_ID_PATTERN = r"^[0-9a-f]{32}$"


class AIConversationStatus(StrEnum):
    ACTIVE = "active"
    CLOSED = "closed"
    DELETED = "deleted"


class AIMessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM_NOTICE = "system_notice"


class AIMessageSource(StrEnum):
    USER = "user"
    APPLICATION = "application"
    LIFECYCLE = "lifecycle"


class AIConversation(BaseModel):
    """User-owned AI Coach conversation aggregate root."""

    model_config = ConfigDict(frozen=True)

    id: Annotated[str, Field(pattern=CONVERSATION_ID_PATTERN)]
    user_id: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=AI_CONVERSATION_LIMITS.maximum_title_length)
    status: AIConversationStatus = AIConversationStatus.ACTIVE
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_activity_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    closed_at: datetime | None = None
    deleted_at: datetime | None = None
    last_message_at: datetime | None = None
    message_count: int = Field(default=0, ge=0)
    schema_version: int = Field(default=1, ge=1)


class AIMessage(BaseModel):
    """Plain-text persisted message created only through trusted services."""

    model_config = ConfigDict(frozen=True)

    id: Annotated[str, Field(pattern=CONVERSATION_ID_PATTERN)]
    conversation_id: Annotated[str, Field(pattern=CONVERSATION_ID_PATTERN)]
    user_id: str = Field(min_length=1)
    role: AIMessageRole
    content: str = Field(min_length=1, max_length=AI_CONVERSATION_LIMITS.maximum_message_length)
    source: AIMessageSource
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deleted_at: datetime | None = None
    schema_version: int = Field(default=1, ge=1)
