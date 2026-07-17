from datetime import date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.ai_decision import DailyDecision


class AIDecisionRepository:
    """MongoDB persistence boundary for owner-scoped daily AI Decisions."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database["ai_decisions"]

    @staticmethod
    def _to_decision(document: dict[str, Any]) -> DailyDecision:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return DailyDecision.model_validate(payload)

    async def save(self, decision: DailyDecision) -> DailyDecision:
        """
        Saves a decision. Overwrites if existing on same _id, or inserts.
        """
        document = decision.model_dump(mode="python", exclude={"id"})
        document["_id"] = decision.id
        # Convert date to isoformat string or store as datetime if needed.
        # Standard MongoDB handles datetime easily, for date we can store as string or ISO date.
        # Let's save effective_date as a string 'YYYY-MM-DD' or keep it as date (Pydantic mode='python' converts date to date or datetime.date).
        if isinstance(document.get("effective_date"), date):
            document["effective_date"] = document["effective_date"].isoformat()

        # Also convert date inside metadata
        if "metadata" in document and isinstance(document["metadata"].get("effective_date"), date):
            document["metadata"]["effective_date"] = document["metadata"][
                "effective_date"
            ].isoformat()

        await self.collection.replace_one({"_id": decision.id}, document, upsert=True)
        return decision

    async def find_active_by_date(self, user_id: str, effective_date: date) -> DailyDecision | None:
        """
        Finds the active (non-superseded) decision for a user on a given date.
        """
        document = await self.collection.find_one(
            {"user_id": user_id, "effective_date": effective_date.isoformat(), "is_active": True}
        )
        return self._to_decision(document) if document else None

    async def find_latest(self, user_id: str) -> DailyDecision | None:
        """
        Finds the latest created active decision for a user.
        """
        document = await self.collection.find_one(
            {"user_id": user_id, "is_active": True}, sort=[("metadata.created_at", -1)]
        )
        return self._to_decision(document) if document else None

    async def list_history(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> list[DailyDecision]:
        """
        Lists decision history for a user, sorted from newest to oldest.
        """
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("metadata.created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)
        return [self._to_decision(doc) for doc in documents]

    async def supersede_previous_decisions(
        self, user_id: str, effective_date: date, new_decision_id: str
    ) -> None:
        """
        Deactivates any previous decisions for the same user and date.
        """
        await self.collection.update_many(
            {
                "user_id": user_id,
                "effective_date": effective_date.isoformat(),
                "is_active": True,
                "_id": {"$ne": new_decision_id},
            },
            {
                "$set": {
                    "is_active": False,
                    "superseded_by": new_decision_id,
                    "updated_at": datetime.utcnow(),
                }
            },
        )
