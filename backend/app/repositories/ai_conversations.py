from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.models.ai_conversation import AIConversation, AIConversationStatus, AIMessage


class AIMessageAlreadyExistsError(Exception):
    """Raised when a trusted retry attempts to persist the same message ID."""


class AIConversationRepository:
    """MongoDB persistence for owner-scoped AI Coach conversations."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database["ai_conversations"]

    @staticmethod
    def _to_domain(document: dict[str, Any]) -> AIConversation:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return AIConversation.model_validate(payload)

    async def create(self, conversation: AIConversation) -> AIConversation:
        document = conversation.model_dump(mode="python", exclude={"id"})
        document["_id"] = conversation.id
        await self.collection.insert_one(document)
        return conversation

    async def find_by_id_and_owner(
        self, conversation_id: str, user_id: str
    ) -> AIConversation | None:
        document = await self.collection.find_one(
            {
                "_id": conversation_id,
                "user_id": user_id,
                "status": {"$ne": AIConversationStatus.DELETED.value},
            }
        )
        return self._to_domain(document) if document else None

    async def list_by_owner(
        self, user_id: str, limit: int, offset: int
    ) -> tuple[list[AIConversation], bool]:
        cursor = (
            self.collection.find(
                {"user_id": user_id, "status": {"$ne": AIConversationStatus.DELETED.value}}
            )
            .sort([("last_activity_at", -1), ("_id", -1)])
            .skip(offset)
            .limit(limit + 1)
        )
        documents = await cursor.to_list(length=limit + 1)
        has_more = len(documents) > limit
        return [self._to_domain(document) for document in documents[:limit]], has_more

    async def close(self, conversation_id: str, user_id: str) -> AIConversation | None:
        now = datetime.now(UTC)
        document = await self.collection.find_one_and_update(
            {
                "_id": conversation_id,
                "user_id": user_id,
                "status": AIConversationStatus.ACTIVE.value,
            },
            {
                "$set": {
                    "status": AIConversationStatus.CLOSED.value,
                    "closed_at": now,
                    "updated_at": now,
                    "last_activity_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        if document:
            return self._to_domain(document)
        return await self.find_by_id_and_owner(conversation_id, user_id)

    async def soft_delete(self, conversation_id: str, user_id: str) -> AIConversation | None:
        now = datetime.now(UTC)
        document = await self.collection.find_one_and_update(
            {
                "_id": conversation_id,
                "user_id": user_id,
                "status": {"$ne": AIConversationStatus.DELETED.value},
            },
            {
                "$set": {
                    "status": AIConversationStatus.DELETED.value,
                    "deleted_at": now,
                    "updated_at": now,
                    "last_activity_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return self._to_domain(document) if document else None

    async def record_message(
        self,
        conversation_id: str,
        user_id: str,
        created_at: datetime,
        allowed_statuses: tuple[AIConversationStatus, ...],
    ) -> AIConversation | None:
        document = await self.collection.find_one_and_update(
            {
                "_id": conversation_id,
                "user_id": user_id,
                "status": {"$in": [status.value for status in allowed_statuses]},
            },
            {
                "$set": {
                    "last_message_at": created_at,
                    "last_activity_at": created_at,
                    "updated_at": created_at,
                },
                "$inc": {"message_count": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return self._to_domain(document) if document else None


class AIMessageRepository:
    """MongoDB persistence for owner- and conversation-scoped messages."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database["ai_messages"]

    @staticmethod
    def _to_domain(document: dict[str, Any]) -> AIMessage:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return AIMessage.model_validate(payload)

    async def create(self, message: AIMessage) -> AIMessage:
        document = message.model_dump(mode="python", exclude={"id"})
        document["_id"] = message.id
        try:
            await self.collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise AIMessageAlreadyExistsError from exc
        return message

    async def list_by_conversation_and_owner(
        self, conversation_id: str, user_id: str, limit: int
    ) -> list[AIMessage]:
        cursor = (
            self.collection.find(
                {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "deleted_at": None,
                }
            )
            .sort([("created_at", -1), ("_id", -1)])
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        messages = [self._to_domain(document) for document in documents]
        messages.reverse()
        return messages

    async def soft_delete_by_conversation(self, conversation_id: str, user_id: str) -> None:
        now = datetime.now(UTC)
        await self.collection.update_many(
            {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "deleted_at": None,
            },
            {"$set": {"deleted_at": now}},
        )

    async def soft_delete_message(self, message_id: str, user_id: str) -> None:
        await self.collection.update_one(
            {"_id": message_id, "user_id": user_id, "deleted_at": None},
            {"$set": {"deleted_at": datetime.now(UTC)}},
        )
