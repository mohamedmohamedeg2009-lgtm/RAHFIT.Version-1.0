from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.health.models import HEALTH_PROFILE_SCHEMA_VERSION, HealthProfile, HealthProfileData


class HealthProfileRepository:
    """Owner-scoped persistence boundary for sensitive health declarations."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database["health_profiles"]

    @staticmethod
    def _profile(document: dict[str, Any]) -> HealthProfile:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return HealthProfile.model_validate(payload)

    async def get_by_user_id(self, user_id: str) -> HealthProfile | None:
        document = await self.collection.find_one({"user_id": user_id})
        return self._profile(document) if document else None

    async def save(self, user_id: str, profile: HealthProfileData) -> HealthProfile:
        now = datetime.now(UTC)
        values = profile.model_dump(
            mode="python",
            exclude={"active_injury_areas", "requires_medical_clearance"},
        )
        for surgery in values["surgery_history"]:
            surgery["surgery_date"] = surgery["surgery_date"].isoformat()
        document = await self.collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$set": {
                    **values,
                    "schema_version": HEALTH_PROFILE_SCHEMA_VERSION,
                    "updated_at": now,
                },
                "$setOnInsert": {"user_id": user_id, "created_at": now},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if document is None:
            raise RuntimeError("Health profile upsert did not return a document.")
        return self._profile(document)
