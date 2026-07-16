from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS
from app.models.ai_conversation import (
    AIConversationStatus,
    AIMessageRole,
    AIMessageSource,
)


class CreateAIConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, max_length=AI_CONVERSATION_LIMITS.maximum_title_length)


class AIMessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: AIMessageRole
    content: str
    source: AIMessageSource
    created_at: datetime
    schema_version: int


class AIConversationSummaryResponse(BaseModel):
    id: str
    title: str
    status: AIConversationStatus
    created_at: datetime
    updated_at: datetime
    last_activity_at: datetime
    closed_at: datetime | None
    last_message_at: datetime | None
    message_count: int
    schema_version: int


class AIConversationDetailResponse(AIConversationSummaryResponse):
    messages: tuple[AIMessageResponse, ...]
    message_history_limit: int = Field(ge=1)
    messages_truncated: bool


class AIConversationListResponse(BaseModel):
    items: tuple[AIConversationSummaryResponse, ...]
    limit: int = Field(ge=1, le=AI_CONVERSATION_LIMITS.maximum_page_size)
    offset: int = Field(ge=0)
    has_more: bool
