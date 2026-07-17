from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorCollection


class PasswordResetRepository:
    """Handles storage, retrieval, and deactivation of secure password reset tokens."""

    def __init__(self, collection: AsyncIOMotorCollection[dict[str, Any]]) -> None:
        self.collection = collection

    async def create_token(self, user_id: str, token_hash: str, expires_at: datetime) -> None:
        """Invalidate any existing token and store the new token hash."""
        now = datetime.now(UTC)
        await self.collection.update_many(
            {"user_id": user_id, "used_at": None},
            {"$set": {"used_at": now}},
        )
        await self.collection.insert_one(
            {
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at,
                "used_at": None,
                "created_at": now,
            }
        )

    async def find_active_token_hash(self, token_hash: str) -> dict[str, Any] | None:
        """Find an unused token hash that has not expired."""
        now = datetime.now(UTC)
        return await self.collection.find_one(
            {
                "token_hash": token_hash,
                "used_at": None,
                "expires_at": {"$gt": now},
            }
        )

    async def mark_token_used(self, token_hash: str) -> bool:
        """Atomically mark a token as used, checking that it was not already used."""
        now = datetime.now(UTC)
        result = await self.collection.update_one(
            {"token_hash": token_hash, "used_at": None},
            {"$set": {"used_at": now}},
        )
        return result.modified_count == 1
