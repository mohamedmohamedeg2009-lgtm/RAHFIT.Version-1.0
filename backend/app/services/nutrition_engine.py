from hashlib import sha256
from uuid import uuid4

from app.models.nutrition import (
    ActivityLevel,
    Allergy,
    DietaryPreference,
    DietType,
    Food,
    FoodServing,
    HydrationTarget,
    Meal,
    MealPlan,
    MealType,
    NutritionPlan,
    NutritionTarget,
)
from app.models.workout import TrainingGoal
from app.services.food_catalog import FoodCatalog


class NutritionGenerationError(Exception):
    """Raised when safe deterministic meals cannot be assembled."""


class NutritionEngine:
    ACTIVITY = {
        ActivityLevel.SEDENTARY: 1.2,
        ActivityLevel.LIGHT: 1.375,
        ActivityLevel.MODERATE: 1.55,
        ActivityLevel.VERY_ACTIVE: 1.725,
        ActivityLevel.EXTRA_ACTIVE: 1.9,
    }

    def __init__(self, catalog: FoodCatalog | None = None) -> None:
        self.catalog = catalog or FoodCatalog()

    def targets(
        self,
        weight: float,
        height: float,
        age: int,
        sex: str,
        activity: ActivityLevel,
        goal: TrainingGoal,
        workout_days: int,
    ) -> NutritionTarget:
        sex_adjustment = 5 if sex == "male" else -161 if sex == "female" else -78
        bmr = round(10 * weight + 6.25 * height - 5 * age + sex_adjustment)
        tdee = round(bmr * self.ACTIVITY[activity])
        calorie_factor = {
            TrainingGoal.FAT_LOSS: 0.85,
            TrainingGoal.MUSCLE_GAIN: 1.10,
            TrainingGoal.STRENGTH: 1.05,
            TrainingGoal.GENERAL_FITNESS: 1.0,
            TrainingGoal.ENDURANCE: 1.08,
            TrainingGoal.FOOTBALL_PERFORMANCE: 1.08,
            TrainingGoal.GOALKEEPER_PERFORMANCE: 1.05,
        }[goal]
        calories = max(1200, round(tdee * calorie_factor))
        protein_factor = {
            TrainingGoal.FAT_LOSS: 1.8,
            TrainingGoal.MUSCLE_GAIN: 2.0,
            TrainingGoal.STRENGTH: 1.8,
            TrainingGoal.GENERAL_FITNESS: 1.6,
            TrainingGoal.ENDURANCE: 1.6,
            TrainingGoal.FOOTBALL_PERFORMANCE: 1.8,
            TrainingGoal.GOALKEEPER_PERFORMANCE: 1.8,
        }[goal]
        protein = round(weight * protein_factor)
        fat = round(weight * 0.8)
        carbohydrates = max(50, round((calories - protein * 4 - fat * 9) / 4))
        fiber = round(calories / 1000 * 14)
        water = round((weight * 35 + workout_days / 7 * 500) / 50) * 50
        return NutritionTarget(
            bmr=bmr,
            tdee=tdee,
            calories=calories,
            protein_grams=protein,
            carbohydrate_grams=carbohydrates,
            fat_grams=fat,
            fiber_grams=fiber,
            hydration=HydrationTarget(
                milliliters=max(1000, water),
                rationale="35 mL/kg baseline plus an averaged training-day allowance.",
            ),
        )

    def safe_foods(
        self,
        diet: DietType,
        allergies: tuple[Allergy, ...],
        preferences: tuple[DietaryPreference, ...],
    ) -> tuple[Food, ...]:
        excluded = set(allergies)
        vegan = diet == DietType.VEGAN or DietaryPreference.VEGAN in preferences
        vegetarian = diet == DietType.VEGETARIAN or DietaryPreference.VEGETARIAN in preferences
        no_seafood = DietaryPreference.NO_SEAFOOD in preferences
        return tuple(
            food
            for food in self.catalog.list_active()
            if not excluded.intersection(food.contains_allergens)
            and (not vegan or food.vegan)
            and (not vegetarian or food.vegetarian)
            and (not no_seafood or food.category != "seafood")
            and (DietaryPreference.HALAL not in preferences or food.halal)
        )

    def generate(
        self,
        *,
        user_id: str,
        assessment_result_id: str,
        workout_plan_id: str | None,
        goal: TrainingGoal,
        diet: DietType,
        allergies: tuple[Allergy, ...],
        preferences: tuple[DietaryPreference, ...],
        activity: ActivityLevel,
        meal_count: int,
        target: NutritionTarget,
        today: object,
    ) -> NutritionPlan:
        safe = self.safe_foods(diet, allergies, preferences)
        meal_types = self._meal_types(meal_count)
        weights = self._distribution(meal_count)
        meals = tuple(
            self._meal(index, meal_type, round(target.calories * weights[index]), safe, diet)
            for index, meal_type in enumerate(meal_types)
        )
        from datetime import date

        plan_date = today if isinstance(today, date) else date.today()
        key_payload = "|".join(
            (
                assessment_result_id,
                str(workout_plan_id),
                goal.value,
                diet.value,
                str(allergies),
                str(preferences),
                activity.value,
                str(meal_count),
                target.model_dump_json(),
            )
        )
        return NutritionPlan(
            id=uuid4().hex,
            user_id=user_id,
            assessment_result_id=assessment_result_id,
            workout_plan_id=workout_plan_id,
            goal=goal,
            diet_type=diet,
            allergies=allergies,
            preferences=preferences,
            activity_level=activity,
            meal_count=meal_count,
            target=target,
            meal_plan=MealPlan(date=plan_date, meals=meals),
            generation_key=sha256(key_payload.encode()).hexdigest(),
        )

    @staticmethod
    def _meal_types(count: int) -> tuple[MealType, ...]:
        return (MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER) + tuple(
            MealType.SNACK for _ in range(count - 3)
        )

    @staticmethod
    def _distribution(count: int) -> tuple[float, ...]:
        snack_share = 0.1
        snack_total = (count - 3) * snack_share
        main = (1 - snack_total) / 3
        return (main, main, main) + tuple(snack_share for _ in range(count - 3))

    def _meal(
        self,
        index: int,
        meal_type: MealType,
        calorie_target: int,
        foods: tuple[Food, ...],
        diet: DietType,
    ) -> Meal:
        candidates = [food for food in foods if meal_type in food.meal_suitability]
        candidates.sort(
            key=lambda food: (
                0 if diet.value in food.diet_tags else 1,
                -(food.protein / food.calories),
                food.id,
            )
        )
        if len(candidates) < 2:
            raise NutritionGenerationError(f"Not enough safe foods for {meal_type.value}.")
        selected = candidates[: min(3, len(candidates))]
        each_calories = calorie_target / len(selected)
        servings = tuple(self._serving(food, each_calories / food.calories) for food in selected)
        return Meal(
            id=f"meal-{index + 1}",
            name=f"{meal_type.value.replace('_', ' ').title()} {index + 1}",
            meal_type=meal_type,
            servings=servings,
            calories=sum(item.calories for item in servings),
            protein=round(sum(item.protein for item in servings), 1),
            carbohydrates=round(sum(item.carbohydrates for item in servings), 1),
            fat=round(sum(item.fat for item in servings), 1),
            fiber=round(sum(item.fiber for item in servings), 1),
        )

    @staticmethod
    def _serving(food: Food, servings: float) -> FoodServing:
        amount = round(max(0.25, min(10, servings)), 2)
        return FoodServing(
            food_id=food.id,
            food_name=food.name,
            servings=amount,
            serving_size=food.serving_size,
            serving_unit=food.serving_unit,
            calories=round(food.calories * amount),
            protein=round(food.protein * amount, 1),
            carbohydrates=round(food.carbohydrates * amount, 1),
            fat=round(food.fat * amount, 1),
            fiber=round(food.fiber * amount, 1),
        )
