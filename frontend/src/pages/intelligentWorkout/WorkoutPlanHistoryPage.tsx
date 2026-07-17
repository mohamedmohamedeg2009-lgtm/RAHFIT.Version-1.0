import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { useLocale } from "../../contexts/LocaleContext";
import { formatWorkoutDate, workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutPlanResponse } from "../../types/intelligentWorkout";
import { Badge, Button, Card, EmptyState, Skeleton } from "../../components/ui";

const pageSize = 10;
export default function WorkoutPlanHistoryPage() {
  const { locale } = useLocale();
  const [items, setItems] = useState<WorkoutPlanResponse[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(
    async (offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const page = await intelligentWorkoutService.listPlans(pageSize, offset);
        setItems((current) => (offset ? [...current, ...page.items] : page.items));
        setHasMore(page.has_more);
      } catch (cause) {
        setError(mapWorkoutError(cause, locale));
      } finally {
        setLoading(false);
      }
    },
    [locale],
  );
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  return (
    <IntelligentWorkoutShell
      title={workoutText(locale, "planHistoryTitle")}
      description={workoutText(locale, "planHistoryDescription")}
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load(items.length)} /> : null}
      {loading && !items.length ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{workoutText(locale, "loadingPlanHistory")}</span>
          <Skeleton height="10rem" />
        </Card>
      ) : items.length ? (
        <div className="iw-list">
          {items.map((plan) => (
            <Card className="iw-history-card" key={plan.plan_id}>
              <div>
                <div className="iw-inline">
                  <Badge>{workoutEnumLabel(plan.status, locale)}</Badge>
                  <Badge>{workoutEnumLabel(plan.generation_mode, locale)}</Badge>
                </div>
                <h2>{workoutEnumLabel(plan.plan_type, locale)}</h2>
                <p>
                  {workoutText(locale, "weeks", { count: plan.duration_weeks })} ·{" "}
                  {workoutText(locale, "daysPerWeek", {
                    count: plan.training_days_per_week,
                  })}{" "}
                  ·{" "}
                  {workoutText(locale, "generated", {
                    date: formatWorkoutDate(plan.generated_at, locale),
                  })}
                </p>
              </div>
              <Link to={`/intelligent-workouts/plans/${plan.plan_id}`}>
                {workoutText(locale, "viewPlan")}
              </Link>
            </Card>
          ))}
          {hasMore ? (
            <Button variant="outline" loading={loading} onClick={() => void load(items.length)}>
              {workoutText(locale, "loadMore")}
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
                {workoutText(locale, "generatePlan")}
              </Link>
            }
          />
        </Card>
      )}
    </IntelligentWorkoutShell>
  );
}
