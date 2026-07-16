from datetime import UTC, datetime
from typing import Any, Protocol

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ReturnDocument

from app.workouts.exceptions import WorkoutPersistenceError
from app.workouts.models import WorkoutPlan, WorkoutSession, WorkoutStatus

# Isolated until legacy workout documents are migrated to the new strict contract.
PLAN_COLLECTION = "intelligent_workout_plans"
SESSION_COLLECTION = "intelligent_workout_sessions"


class WorkoutRepositoryProtocol(Protocol):
    async def create(self, plan: WorkoutPlan) -> WorkoutPlan: ...
    async def replace_active_plan(self, plan: WorkoutPlan) -> WorkoutPlan: ...
    async def get_active_plan(self, user_id: str) -> WorkoutPlan | None: ...
    async def get_by_id(self, user_id: str, plan_id: str) -> WorkoutPlan | None: ...
    async def list_user_plans(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutPlan, ...]: ...
    async def activate_plan(self, user_id: str, plan_id: str) -> WorkoutPlan | None: ...
    async def archive_plan(self, user_id: str, plan_id: str) -> bool: ...
    async def get_version_history(
        self, user_id: str, generation_key: str
    ) -> tuple[WorkoutPlan, ...]: ...
    async def save_session(self, session: WorkoutSession) -> WorkoutSession: ...
    async def update_session(self, session: WorkoutSession) -> WorkoutSession | None: ...
    async def get_session(self, user_id: str, session_id: str) -> WorkoutSession | None: ...
    async def list_sessions(
        self, user_id: str, plan_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutSession, ...]: ...


def _document(model: WorkoutPlan | WorkoutSession) -> dict[str, Any]:
    return model.model_dump(mode="python", exclude_computed_fields=True)


def _without_mongo_id(document: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in document.items() if key != "_id"}


class MongoWorkoutRepository:
    """Async Mongo adapter; every resource query includes the authenticated owner."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.plans = database[PLAN_COLLECTION]
        self.sessions = database[SESSION_COLLECTION]

    async def create(self, plan: WorkoutPlan) -> WorkoutPlan:
        await self.plans.insert_one(_document(plan))
        return plan

    async def replace_active_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        now = datetime.now(UTC)
        current = await self.get_active_plan(plan.user_id)
        version = (current.version + 1) if current else 1
        replacement = plan.model_copy(
            update={
                "version": version,
                "status": WorkoutStatus.ACTIVE,
                "activated_at": now,
                "archived_at": None,
                "updated_at": now,
            }
        )
        await self.plans.update_many(
            {"user_id": plan.user_id, "status": WorkoutStatus.ACTIVE.value},
            {
                "$set": {
                    "status": WorkoutStatus.ARCHIVED.value,
                    "archived_at": now,
                    "updated_at": now,
                }
            },
        )
        try:
            await self.plans.insert_one(_document(replacement))
        except Exception as exc:
            # An acknowledged insert is atomic, but a network error can make its result
            # ambiguous. Check the durable result before attempting compensation.
            try:
                inserted = await self.get_by_id(plan.user_id, replacement.plan_id)
            except Exception:
                inserted = None
            if inserted is not None:
                return inserted
            compensated = await self._restore_active(current)
            raise WorkoutPersistenceError(compensation_succeeded=compensated) from exc
        return replacement

    async def get_active_plan(self, user_id: str) -> WorkoutPlan | None:
        document = await self.plans.find_one(
            {"user_id": user_id, "status": WorkoutStatus.ACTIVE.value}
        )
        return WorkoutPlan.model_validate(_without_mongo_id(document)) if document else None

    async def get_by_id(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        document = await self.plans.find_one({"plan_id": plan_id, "user_id": user_id})
        return WorkoutPlan.model_validate(_without_mongo_id(document)) if document else None

    async def list_user_plans(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutPlan, ...]:
        cursor = self.plans.find({"user_id": user_id}).sort([("generated_at", -1), ("plan_id", -1)])
        cursor = cursor.skip(offset).limit(limit)
        return await self._plans(cursor)

    async def activate_plan(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        target = await self.get_by_id(user_id, plan_id)
        if target is None:
            return None
        if target.status == WorkoutStatus.ACTIVE:
            return target
        now = datetime.now(UTC)
        current = await self.get_active_plan(user_id)
        await self.plans.update_many(
            {"user_id": user_id, "status": WorkoutStatus.ACTIVE.value},
            {
                "$set": {
                    "status": WorkoutStatus.ARCHIVED.value,
                    "archived_at": now,
                    "updated_at": now,
                }
            },
        )
        try:
            document = await self.plans.find_one_and_update(
                {"plan_id": plan_id, "user_id": user_id},
                {
                    "$set": {
                        "status": WorkoutStatus.ACTIVE.value,
                        "activated_at": now,
                        "archived_at": None,
                        "updated_at": now,
                    }
                },
                return_document=ReturnDocument.AFTER,
            )
        except Exception as exc:
            try:
                activated = await self.get_by_id(user_id, plan_id)
            except Exception:
                activated = None
            if activated is not None and activated.status == WorkoutStatus.ACTIVE:
                return activated
            compensated = await self._restore_active(current)
            raise WorkoutPersistenceError(compensation_succeeded=compensated) from exc
        return WorkoutPlan.model_validate(_without_mongo_id(document)) if document else None

    async def archive_plan(self, user_id: str, plan_id: str) -> bool:
        now = datetime.now(UTC)
        result = await self.plans.update_one(
            {"plan_id": plan_id, "user_id": user_id, "status": WorkoutStatus.ACTIVE.value},
            {
                "$set": {
                    "status": WorkoutStatus.ARCHIVED.value,
                    "archived_at": now,
                    "updated_at": now,
                }
            },
        )
        return result.modified_count == 1

    async def get_version_history(
        self, user_id: str, generation_key: str
    ) -> tuple[WorkoutPlan, ...]:
        cursor = (
            self.plans.find(
                {
                    "user_id": user_id,
                    "generation_metadata.generation_key": generation_key,
                }
            )
            .sort("version", -1)
            .limit(100)
        )
        return await self._plans(cursor)

    async def save_session(self, session: WorkoutSession) -> WorkoutSession:
        await self.sessions.insert_one(_document(session))
        return session

    async def update_session(self, session: WorkoutSession) -> WorkoutSession | None:
        document = await self.sessions.find_one_and_update(
            {"session_id": session.session_id, "user_id": session.user_id},
            {"$set": _document(session)},
            return_document=ReturnDocument.AFTER,
        )
        return WorkoutSession.model_validate(_without_mongo_id(document)) if document else None

    async def get_session(self, user_id: str, session_id: str) -> WorkoutSession | None:
        document = await self.sessions.find_one({"session_id": session_id, "user_id": user_id})
        return WorkoutSession.model_validate(_without_mongo_id(document)) if document else None

    async def list_sessions(
        self, user_id: str, plan_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutSession, ...]:
        query: dict[str, Any] = {"user_id": user_id}
        if plan_id is not None:
            query["plan_id"] = plan_id
        cursor = self.sessions.find(query).sort([("started_at", -1), ("session_id", -1)])
        cursor = cursor.skip(offset).limit(limit)
        result: list[WorkoutSession] = []
        async for item in cursor:
            result.append(WorkoutSession.model_validate(_without_mongo_id(item)))
        return tuple(result)

    @staticmethod
    async def _plans(cursor: Any) -> tuple[WorkoutPlan, ...]:
        result: list[WorkoutPlan] = []
        async for item in cursor:
            result.append(WorkoutPlan.model_validate(_without_mongo_id(item)))
        return tuple(result)

    async def _restore_active(
        self,
        target: WorkoutPlan | None,
        fallback: WorkoutPlan | None = None,
    ) -> bool:
        previous = target or fallback
        if previous is None:
            return True
        try:
            result = await self.plans.update_one(
                {"plan_id": previous.plan_id, "user_id": previous.user_id},
                {
                    "$set": {
                        "status": WorkoutStatus.ACTIVE.value,
                        "activated_at": previous.activated_at,
                        "archived_at": None,
                        "updated_at": previous.updated_at,
                    }
                },
            )
        except Exception:
            return False
        return result.matched_count == 1

    # Compatibility aliases for the initial internal draft.
    save_replacement = replace_active_plan
    get_active = get_active_plan
    get_plan = get_by_id
    archive = archive_plan
    list_history = list_user_plans
