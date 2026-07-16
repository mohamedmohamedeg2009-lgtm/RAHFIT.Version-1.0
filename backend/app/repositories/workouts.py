from datetime import UTC, date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.models.workout import (
    ExerciseProgress,
    WorkoutPlan,
    WorkoutPlanStatus,
    WorkoutProgress,
    WorkoutSession,
    WorkoutSessionStatus,
)


class WorkoutRepository:
    """MongoDB persistence boundary for owner-scoped workout plans and sessions."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.plans = database["workout_plans"]
        self.sessions = database["workout_sessions"]

    @staticmethod
    def _to_plan(document: dict[str, Any]) -> WorkoutPlan:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return WorkoutPlan.model_validate(payload)

    @staticmethod
    def _to_session(document: dict[str, Any]) -> WorkoutSession:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return WorkoutSession.model_validate(payload)

    async def find_current_plan(self, user_id: str) -> WorkoutPlan | None:
        document = await self.plans.find_one(
            {"user_id": user_id, "status": WorkoutPlanStatus.ACTIVE.value},
            sort=[("generated_at", -1)],
        )
        return self._to_plan(document) if document else None

    async def create_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        now = datetime.now(UTC)
        await self.plans.update_many(
            {"user_id": plan.user_id, "status": WorkoutPlanStatus.ACTIVE.value},
            {"$set": {"status": WorkoutPlanStatus.ARCHIVED.value, "updated_at": now}},
        )
        document = plan.model_dump(mode="python", exclude={"id"})
        document["_id"] = plan.id
        await self.plans.insert_one(document)
        return plan

    async def list_plans(self, user_id: str, limit: int = 20) -> list[WorkoutPlan]:
        cursor = self.plans.find({"user_id": user_id}).sort("generated_at", -1).limit(limit)
        return [self._to_plan(document) for document in await cursor.to_list(length=limit)]

    async def find_plan(self, plan_id: str, user_id: str) -> WorkoutPlan | None:
        document = await self.plans.find_one({"_id": plan_id, "user_id": user_id})
        return self._to_plan(document) if document else None

    async def find_session(self, session_id: str, user_id: str) -> WorkoutSession | None:
        document = await self.sessions.find_one({"_id": session_id, "user_id": user_id})
        return self._to_session(document) if document else None

    async def find_active_session(
        self, user_id: str, plan_id: str, day_id: str
    ) -> WorkoutSession | None:
        document = await self.sessions.find_one(
            {
                "user_id": user_id,
                "plan_id": plan_id,
                "workout_day_id": day_id,
                "status": WorkoutSessionStatus.IN_PROGRESS.value,
            }
        )
        return self._to_session(document) if document else None

    async def find_session_for_date(
        self, user_id: str, plan_id: str, day_id: str, scheduled_date: date
    ) -> WorkoutSession | None:
        document = await self.sessions.find_one(
            {
                "user_id": user_id,
                "plan_id": plan_id,
                "workout_day_id": day_id,
                "scheduled_date": scheduled_date.isoformat(),
            },
            sort=[("started_at", -1)],
        )
        return self._to_session(document) if document else None

    async def create_session(self, session: WorkoutSession) -> WorkoutSession:
        document = session.model_dump(mode="python", exclude={"id"})
        document["_id"] = session.id
        document["scheduled_date"] = session.scheduled_date.isoformat()
        await self.sessions.insert_one(document)
        return session

    async def update_exercise_progress(
        self,
        session: WorkoutSession,
        exercise_progress: tuple[ExerciseProgress, ...],
        progress: WorkoutProgress,
    ) -> WorkoutSession | None:
        now = datetime.now(UTC)
        document = await self.sessions.find_one_and_update(
            {
                "_id": session.id,
                "user_id": session.user_id,
                "status": WorkoutSessionStatus.IN_PROGRESS.value,
                "revision": session.revision,
            },
            {
                "$set": {
                    "exercise_progress": [item.model_dump() for item in exercise_progress],
                    "progress": progress.model_dump(),
                    "updated_at": now,
                },
                "$inc": {"revision": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return self._to_session(document) if document else None

    async def complete_session(
        self, session: WorkoutSession, progress: WorkoutProgress
    ) -> WorkoutSession | None:
        now = datetime.now(UTC)
        document = await self.sessions.find_one_and_update(
            {
                "_id": session.id,
                "user_id": session.user_id,
                "status": WorkoutSessionStatus.IN_PROGRESS.value,
                "revision": session.revision,
            },
            {
                "$set": {
                    "status": WorkoutSessionStatus.COMPLETED.value,
                    "progress": progress.model_dump(),
                    "completed_at": now,
                    "updated_at": now,
                },
                "$inc": {"revision": 1},
            },
            return_document=ReturnDocument.AFTER,
        )
        return self._to_session(document) if document else None

    async def list_sessions_since(self, user_id: str, since: datetime) -> list[WorkoutSession]:
        cursor = self.sessions.find({"user_id": user_id, "started_at": {"$gte": since}}).sort(
            "started_at", -1
        )
        return [self._to_session(document) for document in await cursor.to_list(length=100)]
