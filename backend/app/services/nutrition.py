from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Protocol

from app.models.assessment import AssessmentResult, SafetyStatus
from app.models.nutrition import (
    ActivityLevel,
    Allergy,
    DietaryPreference,
    DietType,
    Meal,
    NutritionDashboardState,
    NutritionPlan,
    NutritionProgress,
)
from app.models.workout import TrainingGoal, WorkoutPlan
from app.services.nutrition_engine import NutritionEngine


class NutritionAssessmentReader(Protocol):
    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None: ...


class NutritionWorkoutReader(Protocol):
    async def find_current_plan(self, user_id: str) -> WorkoutPlan | None: ...


class NutritionStore(Protocol):
    async def find_current_plan(self, user_id: str) -> NutritionPlan | None: ...
    async def create_plan(self, plan: NutritionPlan) -> NutritionPlan: ...
    async def list_plans(self, user_id: str, limit: int = 20) -> list[NutritionPlan]: ...
    async def get_progress(self, user_id: str, day: date) -> NutritionProgress: ...
    async def log_meal(self, user_id: str, day: date, meal: Meal) -> NutritionProgress: ...
    async def add_water(self, user_id: str, day: date, milliliters: int) -> NutritionProgress: ...


class NutritionNotFoundError(Exception):
    pass


class NutritionAssessmentRequiredError(Exception):
    pass


class NutritionSafetyRestrictedError(Exception):
    pass


@dataclass(frozen=True)
class NutritionCurrentState:
    plan: NutritionPlan
    progress: NutritionProgress


class NutritionService:
    def __init__(
        self,
        store: NutritionStore,
        assessment: NutritionAssessmentReader,
        workout: NutritionWorkoutReader,
        engine: NutritionEngine | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.store = store
        self.assessment = assessment
        self.workout = workout
        self.engine = engine or NutritionEngine()
        self.clock = clock or (lambda: datetime.now(UTC))

    async def generate(
        self,
        user_id: str,
        diet: DietType,
        allergies: tuple[Allergy, ...],
        preferences: tuple[DietaryPreference, ...],
        meal_count: int,
        activity: ActivityLevel | None,
    ) -> NutritionPlan:
        result = await self.assessment.get_latest_assessment_optional(user_id)
        if not result:
            raise NutritionAssessmentRequiredError
        if result.user_id != user_id:
            raise NutritionNotFoundError
        if result.safety_status == SafetyStatus.STOP:
            raise NutritionSafetyRestrictedError
        values = self._values(result)
        workout = await self.workout.find_current_plan(user_id)
        goal = self._goal(values, workout)
        workout_days = workout.available_days if workout else 0
        selected_activity = activity or self._activity(workout_days)
        try:
            weight = float(str(values["current_weight"]))
            height = float(str(values["height"]))
            age = int(str(values["age"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise NutritionAssessmentRequiredError from exc
        target = self.engine.targets(
            weight,
            height,
            age,
            str(values.get("user_gender", "unspecified")),
            selected_activity,
            goal,
            workout_days,
        )
        plan = self.engine.generate(
            user_id=user_id,
            assessment_result_id=result.id,
            workout_plan_id=workout.id if workout else None,
            goal=goal,
            diet=diet,
            allergies=allergies,
            preferences=preferences,
            activity=selected_activity,
            meal_count=meal_count,
            target=target,
            today=self.clock().date(),
        )
        current = await self.store.find_current_plan(user_id)
        if current and current.generation_key == plan.generation_key:
            return current
        return await self.store.create_plan(plan)

    async def current(self, user_id: str) -> NutritionCurrentState:
        plan = await self.store.find_current_plan(user_id)
        if not plan:
            raise NutritionNotFoundError
        return NutritionCurrentState(
            plan, await self.store.get_progress(user_id, self.clock().date())
        )

    async def history(self, user_id: str) -> tuple[NutritionPlan, ...]:
        return tuple(await self.store.list_plans(user_id))

    async def log_meal(self, user_id: str, meal_id: str) -> NutritionProgress:
        state = await self.current(user_id)
        meal = next((item for item in state.plan.meal_plan.meals if item.id == meal_id), None)
        if not meal:
            raise NutritionNotFoundError
        if meal.id in state.progress.completed_meal_ids:
            return state.progress
        return await self.store.log_meal(user_id, self.clock().date(), meal)

    async def add_water(self, user_id: str, milliliters: int) -> NutritionProgress:
        await self.current(user_id)
        return await self.store.add_water(user_id, self.clock().date(), milliliters)

    async def dashboard(self, user_id: str) -> NutritionDashboardState | None:
        try:
            state = await self.current(user_id)
        except NutritionNotFoundError:
            return None
        return NutritionDashboardState(
            plan_id=state.plan.id,
            target_calories=state.plan.target.calories,
            calories_consumed=state.progress.calories_consumed,
            calories_remaining=max(
                0, state.plan.target.calories - state.progress.calories_consumed
            ),
            water_target_ml=state.plan.target.hydration.milliliters,
            water_consumed_ml=state.progress.water_consumed_ml,
            meals_completed=state.progress.meals_completed,
            total_meals=len(state.plan.meal_plan.meals),
        )

    @staticmethod
    def _values(result: AssessmentResult) -> dict[str, object]:
        return {
            key: value for category in result.profile.values() for key, value in category.items()
        }

    @staticmethod
    def _goal(values: Mapping[str, object], workout: WorkoutPlan | None) -> TrainingGoal:
        if workout:
            return workout.goal
        return {
            "fat_loss": TrainingGoal.FAT_LOSS,
            "muscle_gain": TrainingGoal.MUSCLE_GAIN,
            "general_fitness": TrainingGoal.GENERAL_FITNESS,
        }.get(str(values.get("primary_goal")), TrainingGoal.GENERAL_FITNESS)

    @staticmethod
    def _activity(days: int) -> ActivityLevel:
        if days >= 6:
            return ActivityLevel.VERY_ACTIVE
        if days >= 3:
            return ActivityLevel.MODERATE
        if days:
            return ActivityLevel.LIGHT
        return ActivityLevel.SEDENTARY
