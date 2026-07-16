from pydantic import BaseModel, Field

from app.models.nutrition import (
    ActivityLevel,
    Allergy,
    DietaryPreference,
    DietType,
    NutritionPlan,
    NutritionProgress,
)


class GenerateNutritionRequest(BaseModel):
    diet_type: DietType = DietType.BALANCED
    allergies: tuple[Allergy, ...] = ()
    preferences: tuple[DietaryPreference, ...] = (
        DietaryPreference.HALAL,
        DietaryPreference.NO_PORK,
    )
    meal_count: int = Field(default=4, ge=3, le=6)
    activity_level: ActivityLevel | None = None


class CurrentNutritionResponse(BaseModel):
    plan: NutritionPlan
    progress: NutritionProgress


class LogMealRequest(BaseModel):
    meal_id: str = Field(min_length=1)


class WaterIntakeRequest(BaseModel):
    milliliters: int = Field(gt=0, le=2000)
