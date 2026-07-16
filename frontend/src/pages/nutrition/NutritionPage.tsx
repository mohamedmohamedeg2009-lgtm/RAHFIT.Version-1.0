import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Alert, Badge, Button, Card, LinearProgress, Select, Skeleton } from "../../components/ui";
import { ApiError } from "../../services/apiClient";
import { nutritionService } from "../../services/nutritionService";
import type { NutritionState } from "../../types/nutrition";

export default function NutritionPage() {
  const [state, setState] = useState<NutritionState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [diet, setDiet] = useState("balanced");
  const load = useCallback(async () => {
    try {
      setState(await nutritionService.current());
    } catch (c) {
      if (!(c instanceof ApiError && c.status === 404))
        setError(c instanceof Error ? c.message : "Unable to load nutrition.");
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  const mutate = async (action: () => Promise<unknown>) => {
    try {
      await action();
      await load();
    } catch (c) {
      setError(c instanceof Error ? c.message : "Unable to update nutrition.");
    }
  };
  return (
    <div className="nutrition-page">
      <header className="nutrition-header">
        <Link to="/app">RAHFIT AI</Link>
        <nav>
          <Link to="/nutrition/history">History</Link> <Link to="/app">Dashboard</Link>
        </nav>
      </header>
      <main className="nutrition-shell">
        <Badge>NUTRITION ENGINE</Badge>
        <h1>Daily nutrition</h1>
        <p>Deterministic targets and meals calculated from your assessment and training.</p>
        {error ? (
          <Alert variant="danger" title="Nutrition unavailable">
            <p>{error}</p>
          </Alert>
        ) : null}
        {loading ? (
          <Card>
            <Skeleton height="12rem" />
          </Card>
        ) : !state ? (
          <Card className="nutrition-empty">
            <h2>Create your nutrition plan</h2>
            <Select
              label="Diet type"
              value={diet}
              onChange={(e) => setDiet(e.target.value)}
              options={[
                "balanced",
                "high_protein",
                "low_carb",
                "mediterranean",
                "vegetarian",
                "vegan",
              ].map((value) => ({ value, label: value.replaceAll("_", " ") }))}
            />
            <Button onClick={() => void mutate(() => nutritionService.generate(diet, 4))}>
              Generate plan
            </Button>
          </Card>
        ) : (
          <>
            <div className="nutrition-metrics">
              <Card>
                <span>Calories remaining</span>
                <strong>
                  {Math.max(0, state.plan.target.calories - state.progress.calories_consumed)}
                </strong>
                <LinearProgress
                  value={state.progress.calories_consumed}
                  max={state.plan.target.calories}
                />
              </Card>
              <Card>
                <span>Protein</span>
                <strong>
                  {state.progress.protein_consumed} / {state.plan.target.protein_grams} g
                </strong>
              </Card>
              <Card>
                <span>Water</span>
                <strong>
                  {state.progress.water_consumed_ml} / {state.plan.target.hydration.milliliters} mL
                </strong>
                <Button size="sm" onClick={() => void mutate(() => nutritionService.water(250))}>
                  + 250 mL
                </Button>
              </Card>
            </div>
            <section className="nutrition-meals">
              <h2>Today's meals</h2>
              {state.plan.meal_plan.meals.map((meal) => (
                <Card key={meal.id} className="nutrition-meal">
                  <div>
                    <Badge>{meal.meal_type}</Badge>
                    <h3>{meal.name}</h3>
                    <p>{meal.servings.map((s) => s.food_name).join(" · ")}</p>
                  </div>
                  <div>
                    <strong>{meal.calories} kcal</strong>
                    <span>{meal.protein}g protein</span>
                    <Button
                      size="sm"
                      disabled={state.progress.completed_meal_ids.includes(meal.id)}
                      onClick={() => void mutate(() => nutritionService.logMeal(meal.id))}
                    >
                      {state.progress.completed_meal_ids.includes(meal.id) ? "Logged" : "Log meal"}
                    </Button>
                  </div>
                </Card>
              ))}
            </section>
          </>
        )}
      </main>
    </div>
  );
}
