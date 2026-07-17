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
import { useLocale } from "../../contexts/LocaleContext";
import { workoutText } from "../../i18n/intelligentWorkout";

export default function WorkoutGenerationPage() {
  const { locale } = useLocale();
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
      setError(mapWorkoutError(cause, locale));
    } finally {
      setSubmitting(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title={workoutText(locale, "generationTitle")}
      description={workoutText(locale, "generationDescription")}
    >
      {healthSaved ? (
        <Alert variant="success" title={workoutText(locale, "healthSaved")}>
          <p>{workoutText(locale, "healthSavedDescription")}</p>
        </Alert>
      ) : null}
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void generate()} /> : null}
      {!plan ? (
        <Card className="iw-form-card">
          <h2>{workoutText(locale, "planPreferences")}</h2>
          <Select
            label={workoutText(locale, "trainingCycle")}
            value={duration}
            onChange={(event) => setDuration(Number(event.target.value))}
            options={[4, 6, 8, 10, 12].map((value) => ({
              value: String(value),
              label: workoutText(locale, "weeks", { count: value }),
            }))}
          />
          <Switch
            checked={aiAssistance}
            onChange={(event) => setAiAssistance(event.target.checked)}
            label={workoutText(locale, "aiExplanation")}
            description={workoutText(locale, "aiExplanationDescription")}
          />
          <Alert variant="info" title={workoutText(locale, "beforeGeneration")}>
            <p>{workoutText(locale, "beforeGenerationDescription")}</p>
          </Alert>
          <Button size="lg" loading={submitting} onClick={() => void generate()}>
            {workoutText(locale, "generateSafePlan")}
          </Button>
        </Card>
      ) : (
        <div className="iw-list" role="status">
          {plan.generation_mode === "deterministic_fallback" ? (
            <Alert variant="info" title={workoutText(locale, "safePlanCreated")}>
              <p>{workoutText(locale, "safePlanCreatedDescription")}</p>
            </Alert>
          ) : (
            <Alert variant="success" title={workoutText(locale, "planReady")}>
              <p>{workoutText(locale, "planReadyDescription")}</p>
            </Alert>
          )}
          <PlanSummary plan={plan} />
          <div className="iw-actions">
            <Link
              className="ds-button ds-button-primary ds-button-md"
              to={`/intelligent-workouts/plans/${plan.plan_id}`}
            >
              {workoutText(locale, "openPlan")}
            </Link>
            <Link className="ds-button ds-button-outline ds-button-md" to="/intelligent-workouts">
              {workoutText(locale, "workoutOverview")}
            </Link>
          </div>
        </div>
      )}
    </IntelligentWorkoutShell>
  );
}
