import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS, AIConversationLimits
from app.models.ai_conversation import (
    AIConversation,
    AIConversationStatus,
    AIMessage,
    AIMessageRole,
    AIMessageSource,
)

_HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][^>]*>")


class AIConversationNotFoundError(Exception):
    """Safe error for absent, deleted, or differently owned conversations."""


class AIConversationStateError(Exception):
    """Raised when a lifecycle state does not allow an operation."""


class AIConversationValidationError(Exception):
    """Raised when trusted service input violates domain validation."""


class AIConversationLimitError(Exception):
    """Raised when a bounded conversation storage limit is reached."""


class ConversationStore(Protocol):
    async def create(self, conversation: AIConversation) -> AIConversation: ...

    async def find_by_id_and_owner(
        self, conversation_id: str, user_id: str
    ) -> AIConversation | None: ...

    async def list_by_owner(
        self, user_id: str, limit: int, offset: int
    ) -> tuple[list[AIConversation], bool]: ...

    async def close(self, conversation_id: str, user_id: str) -> AIConversation | None: ...

    async def soft_delete(self, conversation_id: str, user_id: str) -> AIConversation | None: ...

    async def record_message(
        self,
        conversation_id: str,
        user_id: str,
        created_at: datetime,
        allowed_statuses: tuple[AIConversationStatus, ...],
    ) -> AIConversation | None: ...


class MessageStore(Protocol):
    async def create(self, message: AIMessage) -> AIMessage: ...

    async def list_by_conversation_and_owner(
        self, conversation_id: str, user_id: str, limit: int
    ) -> list[AIMessage]: ...

    async def soft_delete_by_conversation(self, conversation_id: str, user_id: str) -> None: ...

    async def soft_delete_message(self, message_id: str, user_id: str) -> None: ...


@dataclass(frozen=True)
class AIConversationList:
    items: tuple[AIConversation, ...]
    limit: int
    offset: int
    has_more: bool


@dataclass(frozen=True)
class AIConversationDetail:
    conversation: AIConversation
    messages: tuple[AIMessage, ...]
    message_history_limit: int
    messages_truncated: bool


class AIConversationService:
    """Owner isolation, lifecycle rules, and trusted message persistence."""

    def __init__(
        self,
        conversations: ConversationStore,
        messages: MessageStore,
        limits: AIConversationLimits = AI_CONVERSATION_LIMITS,
    ) -> None:
        self.conversations = conversations
        self.messages = messages
        self.limits = limits

    async def create_conversation(self, user_id: str, title: str | None = None) -> AIConversation:
        normalized_title = self._normalize_title(title)
        now = datetime.now(UTC)
        conversation = AIConversation(
            id=uuid4().hex,
            user_id=user_id,
            title=normalized_title,
            created_at=now,
            updated_at=now,
            last_activity_at=now,
        )
        return await self.conversations.create(conversation)

    async def list_conversations(
        self, user_id: str, limit: int | None = None, offset: int = 0
    ) -> AIConversationList:
        selected_limit = limit or self.limits.default_page_size
        if selected_limit < 1 or selected_limit > self.limits.maximum_page_size or offset < 0:
            raise AIConversationValidationError("Conversation pagination is outside safe bounds.")
        items, has_more = await self.conversations.list_by_owner(user_id, selected_limit, offset)
        return AIConversationList(tuple(items), selected_limit, offset, has_more)

    async def get_conversation(self, user_id: str, conversation_id: str) -> AIConversationDetail:
        conversation = await self._get_owned(user_id, conversation_id)
        messages = await self.messages.list_by_conversation_and_owner(
            conversation_id, user_id, self.limits.maximum_history_response
        )
        return AIConversationDetail(
            conversation=conversation,
            messages=tuple(messages),
            message_history_limit=self.limits.maximum_history_response,
            messages_truncated=conversation.message_count > len(messages),
        )

    async def close_conversation(self, user_id: str, conversation_id: str) -> AIConversation:
        conversation = await self._get_owned(user_id, conversation_id)
        if conversation.status == AIConversationStatus.CLOSED:
            return conversation
        closed = await self.conversations.close(conversation_id, user_id)
        if not closed:
            raise AIConversationNotFoundError
        if closed.status != AIConversationStatus.CLOSED:
            raise AIConversationStateError("The conversation could not be closed safely.")
        return closed

    async def delete_conversation(self, user_id: str, conversation_id: str) -> None:
        deleted = await self.conversations.soft_delete(conversation_id, user_id)
        if not deleted:
            return
        await self.messages.soft_delete_by_conversation(conversation_id, user_id)

    async def append_user_message(
        self, user_id: str, conversation_id: str, content: str
    ) -> AIMessage:
        return await self._append_message(
            user_id,
            conversation_id,
            AIMessageRole.USER,
            AIMessageSource.USER,
            content,
            (AIConversationStatus.ACTIVE,),
        )

    async def append_assistant_message(
        self, user_id: str, conversation_id: str, content: str
    ) -> AIMessage:
        return await self._append_message(
            user_id,
            conversation_id,
            AIMessageRole.ASSISTANT,
            AIMessageSource.APPLICATION,
            content,
            (AIConversationStatus.ACTIVE,),
        )

    async def append_system_notice(
        self, user_id: str, conversation_id: str, content: str
    ) -> AIMessage:
        return await self._append_message(
            user_id,
            conversation_id,
            AIMessageRole.SYSTEM_NOTICE,
            AIMessageSource.LIFECYCLE,
            content,
            (AIConversationStatus.ACTIVE, AIConversationStatus.CLOSED),
        )

    async def _append_message(
        self,
        user_id: str,
        conversation_id: str,
        role: AIMessageRole,
        source: AIMessageSource,
        content: str,
        allowed_statuses: tuple[AIConversationStatus, ...],
    ) -> AIMessage:
        conversation = await self._get_owned(user_id, conversation_id)
        if conversation.status not in allowed_statuses:
            raise AIConversationStateError("The conversation does not accept this message type.")
        if conversation.message_count >= self.limits.maximum_retained_messages:
            raise AIConversationLimitError("The retained message limit has been reached.")
        normalized_content = self._normalize_content(content)
        message = AIMessage(
            id=uuid4().hex,
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=normalized_content,
            source=source,
        )
        stored = await self.messages.create(message)
        updated = await self.conversations.record_message(
            conversation_id, user_id, stored.created_at, allowed_statuses
        )
        if not updated:
            await self.messages.soft_delete_message(stored.id, user_id)
            raise AIConversationStateError("The conversation changed while adding the message.")
        return stored

    async def _get_owned(self, user_id: str, conversation_id: str) -> AIConversation:
        conversation = await self.conversations.find_by_id_and_owner(conversation_id, user_id)
        if not conversation:
            raise AIConversationNotFoundError
        return conversation

    def _normalize_title(self, title: str | None) -> str:
        normalized = re.sub(r"\s+", " ", title or "").strip()
        if not normalized:
            return "New conversation"
        if len(normalized) > self.limits.maximum_title_length:
            raise AIConversationValidationError("Conversation title is too long.")
        if _HTML_TAG_PATTERN.search(normalized):
            raise AIConversationValidationError("Conversation title must be plain text.")
        return normalized

    def _normalize_content(self, content: str) -> str:
        normalized = content.strip()
        if not normalized:
            raise AIConversationValidationError("Message content cannot be blank.")
        if len(normalized) > self.limits.maximum_message_length:
            raise AIConversationValidationError("Message content is too long.")
        if any(ord(character) < 32 and character not in "\n\r\t" for character in normalized):
            raise AIConversationValidationError("Message content contains unsupported characters.")
        if _HTML_TAG_PATTERN.search(normalized):
            raise AIConversationValidationError("Message content must be plain text.")
        return normalized
