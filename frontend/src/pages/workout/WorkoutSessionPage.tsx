import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { SessionProgress, WorkoutShell } from "../../components/workout/WorkoutCards";
import { Alert, Badge, Button, Card, Skeleton } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutCopy } from "../../i18n/workout";
import { workoutService } from "../../services/workoutService";
import type { WorkoutDay, WorkoutPlan, WorkoutSession } from "../../types/workout";

export default function WorkoutSessionPage() {
  const { locale } = useLocale();
  const copy = workoutCopy[locale];
  const { planId = "", dayId = "" } = useParams();
  const [plan, setPlan] = useState<WorkoutPlan | null>(null);
  const [session, setSession] = useState<WorkoutSession | null>(null);
  const [saving, setSaving] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const day: WorkoutDay | null = useMemo(
    () => plan?.days.find((item) => item.id === dayId) ?? null,
    [dayId, plan],
  );

  useEffect(() => {
    void Promise.all([workoutService.details(planId), workoutService.start(planId, dayId)])
      .then(([loadedPlan, loadedSession]) => {
        setPlan(loadedPlan);
        setSession(loadedSession);
      })
      .catch((cause: unknown) =>
        setError(cause instanceof Error ? cause.message : "Session unavailable."),
      );
  }, [dayId, planId]);

  const update = async (exerciseId: string, sets: number, skipped: boolean) => {
    if (!session) return;
    setSaving(exerciseId);
    setError(null);
    try {
      setSession(await workoutService.update(session.id, exerciseId, sets, skipped));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to save progress.");
    } finally {
      setSaving(null);
    }
  };
  const complete = async () => {
    if (!session) return;
    setSaving("complete");
    try {
      setSession(await workoutService.complete(session.id));
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Complete or skip every exercise first.");
    } finally {
      setSaving(null);
    }
  };

  return (
    <WorkoutShell locale={locale} title={day?.title ?? "Workout session"}>
      {error ? (
        <Alert variant="danger" title="Check your workout">
          <p>{error}</p>
        </Alert>
      ) : null}
      {!session || !day ? (
        <Card className="workout-loading">
          <Skeleton height="12rem" />
        </Card>
      ) : (
        <>
          <SessionProgress session={session} />
          {session.status === "completed" ? (
            <Card className="workout-complete-state" role="status">
              <span aria-hidden="true">✓</span>
              <h2>{copy.completed}</h2>
              <p>Your progress has been saved.</p>
              <Link to="/workouts" className="ds-button ds-button-primary ds-button-md">
                Return to plan
              </Link>
            </Card>
          ) : (
            <div className="workout-exercise-list">
              {day.exercises.map((exercise, index) => {
                const tracked = session.exerciseProgress.find(
                  (item) => item.exerciseId === exercise.exerciseId,
                );
                const completedSets = tracked?.completedSets ?? 0;
                return (
                  <Card className="workout-exercise-card" key={exercise.exerciseId}>
                    <div className="workout-exercise-index">{index + 1}</div>
                    <div className="workout-exercise-copy">
                      <div>
                        <h2>{exercise.name}</h2>
                        <Badge>{exercise.muscleGroups.join(" · ")}</Badge>
                      </div>
                      <p>{exercise.description}</p>
                      <dl>
                        <div>
                          <dt>{copy.sets}</dt>
                          <dd>
                            {exercise.sets} × {exercise.reps}
                          </dd>
                        </div>
                        <div>
                          <dt>{copy.rest}</dt>
                          <dd>{exercise.restSeconds}s</dd>
                        </div>
                        <div>
                          <dt>Tempo</dt>
                          <dd>{exercise.tempo}</dd>
                        </div>
                      </dl>
                      <small>{exercise.notes}</small>
                    </div>
                    <div className="workout-set-controls">
                      <strong>
                        {completedSets} / {exercise.sets}
                      </strong>
                      <Button
                        size="sm"
                        disabled={completedSets >= exercise.sets || tracked?.skipped}
                        loading={saving === exercise.exerciseId}
                        onClick={() => void update(exercise.exerciseId, completedSets + 1, false)}
                      >
                        Complete set
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        disabled={completedSets > 0}
                        onClick={() => void update(exercise.exerciseId, 0, !tracked?.skipped)}
                      >
                        {tracked?.skipped ? "Undo skip" : copy.skip}
                      </Button>
                    </div>
                  </Card>
                );
              })}
              <Button size="lg" loading={saving === "complete"} onClick={() => void complete()}>
                {copy.complete}
              </Button>
            </div>
          )}
        </>
      )}
    </WorkoutShell>
  );
}
