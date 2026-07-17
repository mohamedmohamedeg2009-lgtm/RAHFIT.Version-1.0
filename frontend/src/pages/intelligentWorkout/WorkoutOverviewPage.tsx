import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  PlanSummary,
  SafetyNotices,
  WorkoutDayCard,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { ApiError } from "../../services/apiClient";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import { Alert, Card, EmptyState, Skeleton } from "../../components/ui";
import type { WorkoutPlanResponse } from "../../types/intelligentWorkout";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutText } from "../../i18n/intelligentWorkout";

export default function WorkoutOverviewPage() {
  const { locale } = useLocale();
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPlan(await intelligentWorkoutService.getActivePlan());
    } catch (cause) {
      if (cause instanceof ApiError && cause.code === "workout_plan_not_found") setPlan(null);
      else setError(mapWorkoutError(cause, locale));
    } finally {
      setLoading(false);
    }
  }, [locale]);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  return (
    <IntelligentWorkoutShell
      title={workoutText(locale, "overviewTitle")}
      description={workoutText(locale, "overviewDescription")}
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load()} /> : null}
      {loading ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{workoutText(locale, "loadingActivePlan")}</span>
          <Skeleton height="12rem" />
        </Card>
      ) : plan ? (
        <>
          <PlanSummary plan={plan} />
          {plan.generation_mode === "deterministic_fallback" ? (
            <Alert variant="info" title={workoutText(locale, "safeDeterministicPlan")}>
              <p>{workoutText(locale, "safeDeterministicPlanDescription")}</p>
            </Alert>
          ) : null}
          <SafetyNotices plan={plan} />
          <div className="iw-actions">
            <Link
              className="ds-button ds-button-outline ds-button-md"
              to={`/intelligent-workouts/plans/${plan.plan_id}`}
            >
              {workoutText(locale, "viewCompletePlan")}
            </Link>
            <Link
              className="ds-button ds-button-ghost ds-button-md"
              to={`/intelligent-workouts/plans/${plan.plan_id}/adaptation`}
            >
              {workoutText(locale, "reviewAdaptation")}
            </Link>
          </div>
          <section className="iw-section" aria-labelledby="iw-schedule">
            <h2 id="iw-schedule">{workoutText(locale, "weeklySchedule")}</h2>
            <div className="iw-list">
              {plan.weekly_schedule.map((day) => (
                <WorkoutDayCard key={day.day_number} planId={plan.plan_id} day={day} />
              ))}
            </div>
          </section>
        </>
      ) : (
        <Card className="iw-empty-card">
          <EmptyState
            kind="workout"
            action={
              <div className="iw-actions">
                <Link
                  className="ds-button ds-button-primary ds-button-md"
                  to="/intelligent-workouts/setup/profile"
                >
                  {workoutText(locale, "startSetup")}
                </Link>
                <Link
                  className="ds-button ds-button-outline ds-button-md"
                  to="/intelligent-workouts/generate"
                >
                  {workoutText(locale, "generatePlan")}
                </Link>
              </div>
            }
          />
        </Card>
      )}
    </IntelligentWorkoutShell>
  );
}
