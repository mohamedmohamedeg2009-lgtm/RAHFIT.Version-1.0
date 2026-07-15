from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

DocumentT = TypeVar("DocumentT", bound=dict[str, Any])


class BaseRepository(Generic[DocumentT]):
    """Shared persistence boundary for future feature repositories."""

    def __init__(self, collection: AsyncIOMotorCollection[DocumentT]) -> None:
        self.collection = collection

    async def find_by_id(self, document_id: str) -> DocumentT | None:
        if not ObjectId.is_valid(document_id):
            return None
        return await self.collection.find_one({"_id": ObjectId(document_id)})
