from datetime import datetime, timedelta
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase


class DashboardSummaryRepository:
    """Read-only, owner-scoped MongoDB queries used by the dashboard summary."""

    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.nutrition_logs = database["nutrition_daily_logs"]
        self.nutrition_plans = database["nutrition_plans"]
        self.workout_sessions = database["workout_sessions"]
        self.intelligent_workout_sessions = database["intelligent_workout_sessions"]
        self.daily_check_ins = database["daily_check_ins"]

    async def latest_check_in(self, user_id: str) -> dict[str, Any] | None:
        return await self.daily_check_ins.find_one({"user_id": user_id}, sort=[("date", -1)])

    async def today_nutrition(self, user_id: str, day: str) -> dict[str, Any] | None:
        return await self.nutrition_logs.find_one({"user_id": user_id, "date": day})

    async def active_nutrition_plan(self, user_id: str) -> dict[str, Any] | None:
        return await self.nutrition_plans.find_one(
            {"user_id": user_id, "status": "active"}, sort=[("generated_at", -1)]
        )

    async def latest_workout(self, user_id: str) -> dict[str, Any] | None:
        legacy, intelligent = await __import__("asyncio").gather(
            self.workout_sessions.find_one({"user_id": user_id}, sort=[("updated_at", -1)]),
            self.intelligent_workout_sessions.find_one(
                {"user_id": user_id}, sort=[("updated_at", -1)]
            ),
        )
        records = [record for record in (legacy, intelligent) if record]
        return max(records, key=lambda record: record["updated_at"]) if records else None

    async def recent_records(
        self, user_id: str, now: datetime
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
        since = now - timedelta(days=7)
        legacy, intelligent = await __import__("asyncio").gather(
            self.workout_sessions.find({"user_id": user_id, "started_at": {"$gte": since}})
            .sort("started_at", -1)
            .to_list(length=20),
            self.intelligent_workout_sessions.find(
                {"user_id": user_id, "started_at": {"$gte": since}}
            )
            .sort("started_at", -1)
            .to_list(length=20),
        )
        workouts = sorted(
            [*legacy, *intelligent], key=lambda record: record["started_at"], reverse=True
        )[:20]
        nutrition = (
            await self.nutrition_logs.find(
                {"user_id": user_id, "date": {"$gte": since.date().isoformat()}}
            )
            .sort("date", -1)
            .to_list(length=14)
        )
        check_ins = (
            await self.daily_check_ins.find(
                {"user_id": user_id, "date": {"$gte": since.date().isoformat()}}
            )
            .sort("date", -1)
            .to_list(length=14)
        )
        return workouts, nutrition, check_ins
