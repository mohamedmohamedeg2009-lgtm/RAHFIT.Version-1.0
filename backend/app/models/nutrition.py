from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.workout import TrainingGoal


class DietType(StrEnum):
    BALANCED = "balanced"
    HIGH_PROTEIN = "high_protein"
    LOW_CARB = "low_carb"
    MEDITERRANEAN = "mediterranean"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"


class Allergy(StrEnum):
    MILK = "milk"
    EGG = "egg"
    PEANUT = "peanut"
    TREE_NUT = "tree_nut"
    SOY = "soy"
    FISH = "fish"
    SHELLFISH = "shellfish"
    GLUTEN = "gluten"


class DietaryPreference(StrEnum):
    HALAL = "halal"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    NO_PORK = "no_pork"
    NO_SEAFOOD = "no_seafood"


class ActivityLevel(StrEnum):
    SEDENTARY = "sedentary"
    LIGHT = "light"
    MODERATE = "moderate"
    VERY_ACTIVE = "very_active"
    EXTRA_ACTIVE = "extra_active"


class MealType(StrEnum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class GlycemicCategory(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class NutritionPlanStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class Food(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    category: str
    calories: float = Field(gt=0)
    protein: float = Field(ge=0)
    carbohydrates: float = Field(ge=0)
    fat: float = Field(ge=0)
    fiber: float = Field(ge=0)
    serving_size: float = Field(gt=0)
    serving_unit: str
    diet_tags: tuple[str, ...] = ()
    halal: bool
    vegetarian: bool
    vegan: bool
    contains_allergens: tuple[Allergy, ...] = ()
    glycemic_category: GlycemicCategory
    meal_suitability: tuple[MealType, ...]
    active: bool = True
    version: int = Field(default=1, ge=1)


class FoodServing(BaseModel):
    model_config = ConfigDict(frozen=True)

    food_id: str
    food_name: str
    servings: float = Field(gt=0, le=10)
    serving_size: float
    serving_unit: str
    calories: int = Field(ge=0)
    protein: float = Field(ge=0)
    carbohydrates: float = Field(ge=0)
    fat: float = Field(ge=0)
    fiber: float = Field(ge=0)


class Meal(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    meal_type: MealType
    servings: tuple[FoodServing, ...]
    calories: int = Field(ge=0)
    protein: float = Field(ge=0)
    carbohydrates: float = Field(ge=0)
    fat: float = Field(ge=0)
    fiber: float = Field(ge=0)


class MealPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    date: date
    meals: tuple[Meal, ...]


class HydrationTarget(BaseModel):
    model_config = ConfigDict(frozen=True)

    milliliters: int = Field(ge=1000, le=10000)
    rationale: str


class NutritionTarget(BaseModel):
    model_config = ConfigDict(frozen=True)

    bmr: int = Field(gt=0)
    tdee: int = Field(gt=0)
    calories: int = Field(gt=0)
    protein_grams: int = Field(gt=0)
    carbohydrate_grams: int = Field(gt=0)
    fat_grams: int = Field(gt=0)
    fiber_grams: int = Field(gt=0)
    hydration: HydrationTarget


class NutritionPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    assessment_result_id: str
    workout_plan_id: str | None = None
    goal: TrainingGoal
    diet_type: DietType
    allergies: tuple[Allergy, ...] = ()
    preferences: tuple[DietaryPreference, ...] = ()
    activity_level: ActivityLevel
    meal_count: int = Field(ge=3, le=6)
    target: NutritionTarget
    meal_plan: MealPlan
    generation_key: str
    status: NutritionPlanStatus = NutritionPlanStatus.ACTIVE
    version: int = 1
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class NutritionProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    date: date
    calories_consumed: int = Field(ge=0)
    protein_consumed: float = Field(ge=0)
    carbohydrates_consumed: float = Field(ge=0)
    fat_consumed: float = Field(ge=0)
    water_consumed_ml: int = Field(ge=0)
    completed_meal_ids: tuple[str, ...] = ()
    meals_completed: int = Field(ge=0)


class NutritionDashboardState(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: str
    target_calories: int
    calories_consumed: int
    calories_remaining: int
    water_target_ml: int
    water_consumed_ml: int
    meals_completed: int
    total_meals: int
    destination_route: str = "/nutrition"
