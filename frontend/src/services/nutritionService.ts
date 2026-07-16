import { apiRequest } from "./apiClient";
import type { NutritionState } from "../types/nutrition";
export const nutritionService = {
  current: () => apiRequest<NutritionState>("/nutrition/current"),
  generate: (diet_type: string, meal_count: number) =>
    apiRequest("/nutrition/generate", {
      method: "POST",
      body: { diet_type, meal_count, preferences: ["halal", "no_pork"] },
    }),
  logMeal: (meal_id: string) =>
    apiRequest("/nutrition/meals/log", { method: "POST", body: { meal_id } }),
  water: (milliliters: number) =>
    apiRequest("/nutrition/water", { method: "POST", body: { milliliters } }),
  history: () => apiRequest<Array<unknown>>("/nutrition/history"),
};
