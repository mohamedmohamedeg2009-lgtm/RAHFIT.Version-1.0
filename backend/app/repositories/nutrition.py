from datetime import UTC, date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.nutrition import Meal, NutritionPlan, NutritionPlanStatus, NutritionProgress


class NutritionRepository:
    def __init__(self, database: AsyncIOMotorDatabase[dict[str, Any]]) -> None:
        self.plans = database["nutrition_plans"]
        self.logs = database["nutrition_daily_logs"]

    @staticmethod
    def _plan(document: dict[str, Any]) -> NutritionPlan:
        payload = dict(document)
        payload["id"] = str(payload.pop("_id"))
        return NutritionPlan.model_validate(payload)

    async def find_current_plan(self, user_id: str) -> NutritionPlan | None:
        document = await self.plans.find_one(
            {"user_id": user_id, "status": NutritionPlanStatus.ACTIVE.value},
            sort=[("generated_at", -1)],
        )
        return self._plan(document) if document else None

    async def create_plan(self, plan: NutritionPlan) -> NutritionPlan:
        await self.plans.update_many(
            {"user_id": plan.user_id, "status": NutritionPlanStatus.ACTIVE.value},
            {
                "$set": {
                    "status": NutritionPlanStatus.ARCHIVED.value,
                    "updated_at": datetime.now(UTC),
                }
            },
        )
        document = plan.model_dump(mode="python", exclude={"id"})
        document["_id"] = plan.id
        document["meal_plan"]["date"] = plan.meal_plan.date.isoformat()
        await self.plans.insert_one(document)
        return plan

    async def list_plans(self, user_id: str, limit: int = 20) -> list[NutritionPlan]:
        cursor = self.plans.find({"user_id": user_id}).sort("generated_at", -1).limit(limit)
        return [self._plan(item) for item in await cursor.to_list(length=limit)]

    async def get_progress(self, user_id: str, day: date) -> NutritionProgress:
        document = await self.logs.find_one({"user_id": user_id, "date": day.isoformat()})
        if not document:
            return NutritionProgress(
                date=day,
                calories_consumed=0,
                protein_consumed=0,
                carbohydrates_consumed=0,
                fat_consumed=0,
                water_consumed_ml=0,
                meals_completed=0,
            )
        return NutritionProgress.model_validate(document)

    async def log_meal(self, user_id: str, day: date, meal: Meal) -> NutritionProgress:
        await self.logs.update_one(
            {"user_id": user_id, "date": day.isoformat(), "completed_meal_ids": {"$ne": meal.id}},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "date": day.isoformat(),
                    "water_consumed_ml": 0,
                },
                "$addToSet": {"completed_meal_ids": meal.id},
                "$inc": {
                    "calories_consumed": meal.calories,
                    "protein_consumed": meal.protein,
                    "carbohydrates_consumed": meal.carbohydrates,
                    "fat_consumed": meal.fat,
                    "meals_completed": 1,
                },
            },
            upsert=True,
        )
        return await self.get_progress(user_id, day)

    async def add_water(self, user_id: str, day: date, milliliters: int) -> NutritionProgress:
        await self.logs.update_one(
            {"user_id": user_id, "date": day.isoformat()},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "date": day.isoformat(),
                    "calories_consumed": 0,
                    "protein_consumed": 0,
                    "carbohydrates_consumed": 0,
                    "fat_consumed": 0,
                    "meals_completed": 0,
                    "completed_meal_ids": [],
                },
                "$inc": {"water_consumed_ml": milliliters},
            },
            upsert=True,
        )
        return await self.get_progress(user_id, day)
