import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { PlanOverview, WorkoutDayCard, WorkoutShell } from "../../components/workout/WorkoutCards";
import { Alert, Card, Skeleton } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutService } from "../../services/workoutService";
import type { WorkoutPlan } from "../../types/workout";

export default function WorkoutPlanPage() {
  const { locale } = useLocale();
  const { planId = "" } = useParams();
  const [plan, setPlan] = useState<WorkoutPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    void workoutService
      .details(planId)
      .then(setPlan)
      .catch((cause: unknown) =>
        setError(cause instanceof Error ? cause.message : "Plan unavailable."),
      );
  }, [planId]);
  return (
    <WorkoutShell locale={locale} title="Workout plan">
      {error ? (
        <Alert variant="danger" title="Plan unavailable">
          <p>{error}</p>
        </Alert>
      ) : !plan ? (
        <Card>
          <Skeleton height="12rem" />
        </Card>
      ) : (
        <>
          <PlanOverview plan={plan} />
          <div className="workout-days-grid">
            {plan.days.map((day) => (
              <WorkoutDayCard key={day.id} day={day} planId={plan.id} />
            ))}
          </div>
        </>
      )}
    </WorkoutShell>
  );
}
