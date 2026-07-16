export interface NutritionMeal {
  id: string;
  name: string;
  meal_type: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
  servings: Array<{
    food_name: string;
    servings: number;
    serving_size: number;
    serving_unit: string;
  }>;
}
export interface NutritionState {
  plan: {
    id: string;
    diet_type: string;
    target: {
      calories: number;
      protein_grams: number;
      carbohydrate_grams: number;
      fat_grams: number;
      fiber_grams: number;
      hydration: { milliliters: number };
    };
    meal_plan: { meals: NutritionMeal[] };
  };
  progress: {
    calories_consumed: number;
    protein_consumed: number;
    carbohydrates_consumed: number;
    fat_consumed: number;
    water_consumed_ml: number;
    completed_meal_ids: string[];
    meals_completed: number;
  };
}
