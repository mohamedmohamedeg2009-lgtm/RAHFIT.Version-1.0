import { useState } from "react";
import { Link, useLocation } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  PlanSummary,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { Alert, Button, Card, Select, Switch } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutPlanResponse } from "../../types/intelligentWorkout";

export default function WorkoutGenerationPage() {
  const location = useLocation();
  const healthSaved = Boolean((location.state as { healthSaved?: boolean } | null)?.healthSaved);
  const [duration, setDuration] = useState(8);
  const [aiAssistance, setAiAssistance] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [plan, setPlan] = useState<WorkoutPlanResponse | null>(null);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const generate = async () => {
    setSubmitting(true);
    setError(null);
    setPlan(null);
    try {
      setPlan(
        await intelligentWorkoutService.generatePlan({
          duration_weeks: duration,
          use_ai_assistance: aiAssistance,
        }),
      );
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title="Generate a training plan"
      description="Python validates readiness, safety, exercise selection, and the final plan before anything is returned."
    >
      {healthSaved ? (
        <Alert variant="success" title="Health declaration saved">
          <p>Your required setup is ready for server validation.</p>
        </Alert>
      ) : null}
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void generate()} /> : null}
      {!plan ? (
        <Card className="iw-form-card">
          <h2>Plan preferences</h2>
          <Select
            label="Training cycle"
            value={duration}
            onChange={(event) => setDuration(Number(event.target.value))}
            options={[4, 6, 8, 10, 12].map((value) => ({
              value: String(value),
              label: `${value} weeks`,
            }))}
          />
          <Switch
            checked={aiAssistance}
            onChange={(event) => setAiAssistance(event.target.checked)}
            label="AI-assisted explanation"
            description="AI may explain an already validated plan. Exercise selection remains deterministic and server-controlled."
          />
          <Alert variant="info" title="Before generation">
            <p>
              Your profile and explicit health declaration must be complete. RAHFIT AI does not
              replace professional medical advice.
            </p>
          </Alert>
          <Button size="lg" loading={submitting} onClick={() => void generate()}>
            Generate safe plan
          </Button>
        </Card>
      ) : (
        <div className="iw-list" role="status">
          {plan.generation_mode === "deterministic_fallback" ? (
            <Alert variant="info" title="Safe deterministic plan created">
              <p>
                AI assistance was unavailable, so the validated deterministic plan was returned
                successfully. No retry is needed.
              </p>
            </Alert>
          ) : (
            <Alert variant="success" title="Plan ready">
              <p>Your plan was generated and activated successfully.</p>
            </Alert>
          )}
          <PlanSummary plan={plan} />
          <div className="iw-actions">
            <Link
              className="ds-button ds-button-primary ds-button-md"
              to={`/intelligent-workouts/plans/${plan.plan_id}`}
            >
              Open plan
            </Link>
            <Link className="ds-button ds-button-outline ds-button-md" to="/intelligent-workouts">
              Workout overview
            </Link>
          </div>
        </div>
      )}
    </IntelligentWorkoutShell>
  );
}
