import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { formatDate, label } from "../../components/intelligentWorkout/utils";
import { Badge, Button, Card, EmptyState, Skeleton } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutPlanResponse } from "../../types/intelligentWorkout";

const pageSize = 10;
export default function WorkoutPlanHistoryPage() {
  const [items, setItems] = useState<WorkoutPlanResponse[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(async (offset = 0) => {
    setLoading(true);
    setError(null);
    try {
      const page = await intelligentWorkoutService.listPlans(pageSize, offset);
      setItems((current) => (offset ? [...current, ...page.items] : page.items));
      setHasMore(page.has_more);
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  return (
    <IntelligentWorkoutShell
      title="Plan history"
      description="Review your owner-scoped active and archived training plans."
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load(items.length)} /> : null}
      {loading && !items.length ? (
        <Card>
          <Skeleton height="10rem" />
        </Card>
      ) : items.length ? (
        <div className="iw-list">
          {items.map((plan) => (
            <Card className="iw-history-card" key={plan.plan_id}>
              <div>
                <div className="iw-inline">
                  <Badge>{plan.status}</Badge>
                  <Badge>{label(plan.generation_mode)}</Badge>
                </div>
                <h2>{label(plan.plan_type)}</h2>
                <p>
                  {plan.duration_weeks} weeks · {plan.training_days_per_week} days / week ·
                  Generated {formatDate(plan.generated_at)}
                </p>
              </div>
              <Link to={`/intelligent-workouts/plans/${plan.plan_id}`}>View plan</Link>
            </Card>
          ))}
          {hasMore ? (
            <Button variant="outline" loading={loading} onClick={() => void load(items.length)}>
              Load more
            </Button>
          ) : null}
        </div>
      ) : (
        <Card>
          <EmptyState
            kind="workout"
            action={
              <Link
                className="ds-button ds-button-primary ds-button-md"
                to="/intelligent-workouts/generate"
              >
                Generate a plan
              </Link>
            }
          />
        </Card>
      )}
    </IntelligentWorkoutShell>
  );
}
