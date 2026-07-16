import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { PlanOverview, WorkoutDayCard, WorkoutShell } from "../../components/workout/WorkoutCards";
import { Alert, Button, Card, Select, Skeleton } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutCopy } from "../../i18n/workout";
import { ApiError } from "../../services/apiClient";
import { workoutService } from "../../services/workoutService";
import type { CurrentWorkout } from "../../types/workout";

export default function WorkoutPage() {
  const { locale } = useLocale();
  const copy = workoutCopy[locale];
  const [current, setCurrent] = useState<CurrentWorkout | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [days, setDays] = useState(3);
  const [duration, setDuration] = useState(60);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      setCurrent(await workoutService.current());
    } catch (cause) {
      if (!(cause instanceof ApiError && cause.status === 404))
        setError(cause instanceof Error ? cause.message : "Unable to load workout.");
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with the workout aggregate.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const generate = async () => {
    setGenerating(true);
    setError(null);
    try {
      await workoutService.generate(days, duration);
      await load();
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to generate workout.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <WorkoutShell locale={locale}>
      {error ? (
        <Alert variant="danger" title="Workout unavailable">
          <p>{error}</p>
        </Alert>
      ) : null}
      {loading ? (
        <Card className="workout-loading">
          <Skeleton height="12rem" />
        </Card>
      ) : current ? (
        <>
          <PlanOverview plan={current.plan} />
          <section className="workout-today" aria-labelledby="today-workout-title">
            <div className="workout-section-heading">
              <div>
                <span>{copy.today}</span>
                <h2 id="today-workout-title">{current.today.title}</h2>
              </div>
              <Link to={`/workouts/${current.plan.id}`}>View full plan</Link>
            </div>
            <WorkoutDayCard day={current.today} planId={current.plan.id} featured />
          </section>
        </>
      ) : (
        <Card className="workout-empty-state">
          <span className="workout-empty-icon" aria-hidden="true">
            ↗
          </span>
          <div>
            <h2>{copy.noPlan}</h2>
            <p>
              Choose a weekly schedule. Safety, exercise selection, and progression remain
              assessment-driven.
            </p>
          </div>
          <div className="workout-generation-fields">
            <Select
              label="Training days"
              value={days}
              onChange={(event) => setDays(Number(event.target.value))}
              options={[2, 3, 4, 5, 6].map((value) => ({
                label: `${value} days`,
                value: String(value),
              }))}
            />
            <Select
              label="Session duration"
              value={duration}
              onChange={(event) => setDuration(Number(event.target.value))}
              options={[30, 45, 60, 75, 90].map((value) => ({
                label: `${value} minutes`,
                value: String(value),
              }))}
            />
          </div>
          <Button size="lg" loading={generating} onClick={() => void generate()}>
            {copy.generate}
          </Button>
        </Card>
      )}
    </WorkoutShell>
  );
}
