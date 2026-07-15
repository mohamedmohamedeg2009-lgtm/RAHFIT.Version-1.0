from datetime import UTC, datetime
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.models.user import User


class UserRepository:
    """Persistence boundary for authentication users."""

    def __init__(self, collection: AsyncIOMotorCollection[dict[str, Any]]) -> None:
        self.collection = collection

    @staticmethod
    def _to_user(document: dict[str, Any]) -> User:
        return User(
            id=str(document["_id"]),
            email=str(document["email"]),
            password_hash=str(document["password_hash"]),
            is_active=bool(document["is_active"]),
            token_version=int(document.get("token_version", 0)),
            created_at=document["created_at"],
            updated_at=document["updated_at"],
        )

    async def create(self, email: str, password_hash: str) -> User:
        now = datetime.now(UTC)
        document: dict[str, Any] = {
            "email": email,
            "password_hash": password_hash,
            "is_active": True,
            "token_version": 0,
            "created_at": now,
            "updated_at": now,
        }
        try:
            result = await self.collection.insert_one(document)
        except DuplicateKeyError as exc:
            raise UserAlreadyExistsError from exc
        document["_id"] = result.inserted_id
        return self._to_user(document)

    async def find_by_email(self, email: str) -> User | None:
        document = await self.collection.find_one({"email": email})
        return self._to_user(document) if document else None

    async def find_by_id(self, user_id: str) -> User | None:
        if not ObjectId.is_valid(user_id):
            return None
        document = await self.collection.find_one({"_id": ObjectId(user_id)})
        return self._to_user(document) if document else None

    async def increment_token_version(self, user_id: str, expected_version: int) -> User | None:
        if not ObjectId.is_valid(user_id):
            return None
        document = await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id), "token_version": expected_version},
            {"$inc": {"token_version": 1}, "$set": {"updated_at": datetime.now(UTC)}},
            return_document=ReturnDocument.AFTER,
        )
        return self._to_user(document) if document else None


class UserAlreadyExistsError(Exception):
    """Raised when a unique user identity already exists."""
