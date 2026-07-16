import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, expect, it, vi } from "vitest";
import NutritionPage from "../pages/nutrition/NutritionPage";

const state = {
  plan: {
    id: "p1",
    diet_type: "balanced",
    target: {
      calories: 2000,
      protein_grams: 140,
      carbohydrate_grams: 230,
      fat_grams: 60,
      fiber_grams: 28,
      hydration: { milliliters: 2800 },
    },
    meal_plan: {
      meals: [
        {
          id: "meal-1",
          name: "Breakfast 1",
          meal_type: "breakfast",
          calories: 500,
          protein: 35,
          carbohydrates: 55,
          fat: 15,
          servings: [
            { food_name: "Rolled Oats", servings: 1, serving_size: 40, serving_unit: "g" },
          ],
        },
      ],
    },
  },
  progress: {
    calories_consumed: 0,
    protein_consumed: 0,
    carbohydrates_consumed: 0,
    fat_consumed: 0,
    water_consumed_ml: 0,
    completed_meal_ids: [],
    meals_completed: 0,
  },
};
const response = (payload: unknown) =>
  Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
afterEach(() => vi.restoreAllMocks());

it("renders deterministic nutrition and logs water", async () => {
  const fetchMock = vi
    .spyOn(globalThis, "fetch")
    .mockImplementation((_request, init) =>
      response(init?.method === "POST" ? { ...state.progress, water_consumed_ml: 250 } : state),
    );
  render(
    <MemoryRouter>
      <NutritionPage />
    </MemoryRouter>,
  );
  expect(await screen.findByRole("heading", { name: "Breakfast 1" })).toBeTruthy();
  await userEvent.click(screen.getByRole("button", { name: "+ 250 mL" }));
  await waitFor(() =>
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/nutrition/water"),
      expect.objectContaining({ method: "POST" }),
    ),
  );
});
