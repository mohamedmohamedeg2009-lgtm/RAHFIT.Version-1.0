from app.models.nutrition import ActivityLevel, Allergy, DietaryPreference, DietType
from app.models.workout import TrainingGoal
from app.services.nutrition_engine import NutritionEngine


def test_mifflin_st_jeor_targets_are_deterministic() -> None:
    engine = NutritionEngine()
    target = engine.targets(80, 180, 30, "male", ActivityLevel.MODERATE, TrainingGoal.FAT_LOSS, 4)
    assert target.bmr == 1780
    assert target.tdee == 2759
    assert target.calories == 2345
    assert target.protein_grams == 144
    assert target.hydration.milliliters == 3100


def test_safe_foods_exclude_allergies_and_respect_vegan_preference() -> None:
    foods = NutritionEngine().safe_foods(
        DietType.VEGAN,
        (Allergy.SOY, Allergy.TREE_NUT, Allergy.GLUTEN),
        (DietaryPreference.VEGAN, DietaryPreference.HALAL),
    )
    assert foods
    assert all(food.vegan and food.halal for food in foods)
    assert all(
        not set(food.contains_allergens).intersection(
            {Allergy.SOY, Allergy.TREE_NUT, Allergy.GLUTEN}
        )
        for food in foods
    )


def test_generated_meals_approximate_calories_without_allergens() -> None:
    engine = NutritionEngine()
    target = engine.targets(
        70, 170, 25, "female", ActivityLevel.MODERATE, TrainingGoal.GENERAL_FITNESS, 3
    )
    plan = engine.generate(
        user_id="u1",
        assessment_result_id="a1",
        workout_plan_id=None,
        goal=TrainingGoal.GENERAL_FITNESS,
        diet=DietType.MEDITERRANEAN,
        allergies=(Allergy.MILK, Allergy.EGG),
        preferences=(DietaryPreference.HALAL,),
        activity=ActivityLevel.MODERATE,
        meal_count=4,
        target=target,
        today=None,
    )
    calories = sum(meal.calories for meal in plan.meal_plan.meals)
    assert abs(calories - target.calories) <= target.calories * 0.05
    assert len(plan.meal_plan.meals) == 4
