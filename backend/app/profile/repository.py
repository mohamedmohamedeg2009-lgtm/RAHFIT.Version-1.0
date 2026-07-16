from datetime import UTC, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.profile.models import PROFILE_SCHEMA_VERSION, UserProfile, UserProfileData


class UserProfileRepository:
    """Owner-scoped persistence boundary for the canonical user profile."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.collection = database["user_profiles"]

    @staticmethod
    def _profile(document: dict[str, Any]) -> UserProfile:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return UserProfile.model_validate(payload)

    async def get_by_user_id(self, user_id: str) -> UserProfile | None:
        document = await self.collection.find_one({"user_id": user_id})
        return self._profile(document) if document else None

    async def save(self, user_id: str, profile: UserProfileData) -> UserProfile:
        now = datetime.now(UTC)
        values = profile.model_dump(mode="python", exclude={"bmi", "bmr_kcal", "age_group"})
        target_date = values["goals"].get("target_date")
        if target_date is not None:
            values["goals"]["target_date"] = target_date.isoformat()
        document = await self.collection.find_one_and_update(
            {"user_id": user_id},
            {
                "$set": {
                    **values,
                    "schema_version": PROFILE_SCHEMA_VERSION,
                    "updated_at": now,
                },
                "$setOnInsert": {"user_id": user_id, "created_at": now},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        if document is None:
            raise RuntimeError("User profile upsert did not return a document.")
        return self._profile(document)
