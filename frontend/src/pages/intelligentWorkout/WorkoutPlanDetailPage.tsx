import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  PlanSummary,
  SafetyNotices,
  WorkoutDayCard,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { label } from "../../components/intelligentWorkout/utils";
import { Alert, Button, Card, Skeleton } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutPlanResponse } from "../../types/intelligentWorkout";

export default function WorkoutPlanDetailPage() {
  const { planId = "" } = useParams();
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setPlan(await intelligentWorkoutService.getPlan(planId));
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setLoading(false);
    }
  }, [planId]);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  const changeStatus = async () => {
    if (!plan) return;
    setSaving(true);
    setError(null);
    try {
      if (plan.status === "active") {
        await intelligentWorkoutService.archivePlan(plan.plan_id);
        await load();
      } else setPlan(await intelligentWorkoutService.activatePlan(plan.plan_id));
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setSaving(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title="Training plan"
      description="Review every server-approved day, prescription, safety note, and progression boundary."
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load()} /> : null}
      {loading ? (
        <Card>
          <Skeleton height="14rem" />
        </Card>
      ) : plan ? (
        <>
          <PlanSummary plan={plan} />
          <div className="iw-actions">
            <Button
              variant={plan.status === "active" ? "danger" : "primary"}
              loading={saving}
              onClick={() => void changeStatus()}
            >
              {plan.status === "active" ? "Archive plan" : "Activate plan"}
            </Button>
            <Link
              className="ds-button ds-button-outline ds-button-md"
              to={`/intelligent-workouts/plans/${plan.plan_id}/adaptation`}
            >
              Analyze adaptation
            </Link>
          </div>
          {plan.generation_mode === "deterministic_fallback" ? (
            <Alert variant="info" title="Deterministic fallback">
              <p>
                This is a successful, fully validated plan. AI was not used for its explanation.
              </p>
            </Alert>
          ) : null}
          <Card className="iw-explanation">
            <h2>Why this plan</h2>
            <p>{plan.explanation.summary}</p>
            <ul>
              {plan.explanation.rationale.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
            <strong>{plan.explanation.motivation}</strong>
            <p>{plan.explanation.recovery_reminder}</p>
          </Card>
          <SafetyNotices plan={plan} />
          <section className="iw-section">
            <h2>Weekly schedule</h2>
            <div className="iw-list">
              {plan.weekly_schedule.map((day) => (
                <div key={day.day_number} className="iw-list">
                  <WorkoutDayCard planId={plan.plan_id} day={day} />
                  {day.sections.map((section) => (
                    <Card className="iw-section-card" key={section.section_type}>
                      <h3>{label(section.section_type)}</h3>
                      {section.exercises.map((exercise) => (
                        <article className="iw-exercise" key={exercise.exercise_id}>
                          <div>
                            <h4>{exercise.exercise_name}</h4>
                            <p>
                              {exercise.primary_muscles.map(label).join(" · ")} ·{" "}
                              {exercise.equipment.map(label).join(", ")}
                            </p>
                          </div>
                          <dl>
                            <div>
                              <dt>Sets</dt>
                              <dd>{exercise.prescription.sets}</dd>
                            </div>
                            <div>
                              <dt>Reps</dt>
                              <dd>
                                {exercise.prescription.min_reps}–{exercise.prescription.max_reps}
                              </dd>
                            </div>
                            <div>
                              <dt>Rest</dt>
                              <dd>{exercise.prescription.rest_seconds}s</dd>
                            </div>
                            <div>
                              <dt>RPE</dt>
                              <dd>
                                {exercise.prescription.rpe_min}–{exercise.prescription.rpe_max}
                              </dd>
                            </div>
                          </dl>
                          <p>{exercise.prescription.intensity_guidance}</p>
                          <ol>
                            {exercise.instructions.map((item) => (
                              <li key={item}>{item}</li>
                            ))}
                          </ol>
                          {exercise.safety_notes.length ? (
                            <Alert variant="warning">
                              <ul>
                                {exercise.safety_notes.map((item) => (
                                  <li key={item}>{item}</li>
                                ))}
                              </ul>
                            </Alert>
                          ) : null}
                        </article>
                      ))}
                    </Card>
                  ))}
                </div>
              ))}
            </div>
          </section>
          <Card>
            <h2>Progression guidance</h2>
            <ul>
              {plan.progression_guidance.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </Card>
        </>
      ) : null}
    </IntelligentWorkoutShell>
  );
}
