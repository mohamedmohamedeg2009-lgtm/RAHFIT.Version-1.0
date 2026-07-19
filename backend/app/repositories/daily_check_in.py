from datetime import date
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.daily_check_in import DailyCheckIn

DAILY_CHECK_IN_COLLECTION = "daily_check_ins"


class MongoDailyCheckInRepository:
    """MongoDB persistence adapter for owner-scoped DailyCheckIn records."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database[DAILY_CHECK_IN_COLLECTION]

    async def upsert(self, check_in: DailyCheckIn) -> DailyCheckIn:
        payload = check_in.model_dump(mode="json")
        # Format date as ISO string (YYYY-MM-DD) for clean MongoDB indexing
        date_str = check_in.date.isoformat()
        payload["date"] = date_str

        filter_doc = {"user_id": check_in.user_id, "date": date_str}
        await self.collection.replace_one(filter_doc, payload, upsert=True)
        return check_in

    async def get_by_date(self, user_id: str, check_in_date: date) -> DailyCheckIn | None:
        date_str = check_in_date.isoformat()
        doc = await self.collection.find_one({"user_id": user_id, "date": date_str})
        if not doc:
            return None
        doc.pop("_id", None)
        return DailyCheckIn.model_validate(doc)

    async def list_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[DailyCheckIn], int]:
        query = {"user_id": user_id}
        total = await self.collection.count_documents(query)

        cursor = self.collection.find(query).sort("date", -1).skip(offset).limit(limit)
        items: list[DailyCheckIn] = []
        async for doc in cursor:
            doc.pop("_id", None)
            items.append(DailyCheckIn.model_validate(doc))

        return items, total
