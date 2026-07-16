import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Card, Skeleton } from "../../components/ui";
import { nutritionService } from "../../services/nutritionService";

type HistoricalPlan = {
  id: string;
  diet_type: string;
  generated_at: string;
  target: { calories: number };
  meal_count: number;
};
export default function NutritionHistoryPage() {
  const [plans, setPlans] = useState<HistoricalPlan[] | null>(null);
  useEffect(() => {
    void nutritionService.history().then((value) => setPlans(value as HistoricalPlan[]));
  }, []);
  return (
    <main className="nutrition-shell">
      <Link to="/nutrition">← Daily nutrition</Link>
      <h1>Nutrition history</h1>
      {!plans ? (
        <Card>
          <Skeleton height="10rem" />
        </Card>
      ) : plans.length === 0 ? (
        <Card className="nutrition-empty">
          <h2>No previous plans</h2>
        </Card>
      ) : (
        <div className="nutrition-meals">
          {plans.map((plan) => (
            <Card className="nutrition-meal" key={plan.id}>
              <div>
                <h2>{plan.diet_type.replaceAll("_", " ")}</h2>
                <p>{new Date(plan.generated_at).toLocaleDateString()}</p>
              </div>
              <div>
                <strong>{plan.target.calories} kcal</strong>
                <span>{plan.meal_count} meals</span>
              </div>
            </Card>
          ))}
        </div>
      )}
    </main>
  );
}
