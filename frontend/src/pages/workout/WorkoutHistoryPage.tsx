import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { WorkoutShell } from "../../components/workout/WorkoutCards";
import { Card, CircularProgress, Skeleton } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutService } from "../../services/workoutService";
import type { WorkoutHistory } from "../../types/workout";

export default function WorkoutHistoryPage() {
  const { locale } = useLocale();
  const [history, setHistory] = useState<WorkoutHistory | null>(null);
  useEffect(() => {
    void workoutService.history().then(setHistory);
  }, []);
  return (
    <WorkoutShell locale={locale} title="Workout history">
      {!history ? (
        <Card>
          <Skeleton height="10rem" />
        </Card>
      ) : (
        <>
          <Card className="workout-history-summary">
            <CircularProgress value={history.weeklyAdherencePercentage} label="Weekly adherence" />
            <div>
              <span>Completed this week</span>
              <strong>{history.completedSessions}</strong>
              <p>sessions</p>
            </div>
          </Card>
          <div className="workout-history-list">
            {history.plans.map((plan) => (
              <Card key={plan.id}>
                <div>
                  <h2>{plan.goal.replaceAll("_", " ")}</h2>
                  <p>
                    {plan.availableDays} days · {plan.experience}
                  </p>
                </div>
                <Link to={`/workouts/${plan.id}`}>View plan</Link>
              </Card>
            ))}
          </div>
        </>
      )}
    </WorkoutShell>
  );
}
