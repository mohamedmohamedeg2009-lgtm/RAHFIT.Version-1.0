import { useState } from "react";
import { useParams } from "react-router-dom";

import {
  AdaptationResult,
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { Alert, Button, Card } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutAdaptationResponse } from "../../types/intelligentWorkout";
import { useLocale } from "../../contexts/LocaleContext";
import { workoutText } from "../../i18n/intelligentWorkout";

export default function WorkoutAdaptationPage() {
  const { locale } = useLocale();
  const { planId = "" } = useParams();
  const [result, setResult] = useState<WorkoutAdaptationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const analyze = async () => {
    setLoading(true);
    setError(null);
    try {
      setResult(await intelligentWorkoutService.analyzeAdaptation(planId));
    } catch (cause) {
      setError(mapWorkoutError(cause, locale));
    } finally {
      setLoading(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title={workoutText(locale, "adaptationTitle")}
      description={workoutText(locale, "adaptationDescription")}
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void analyze()} /> : null}
      <Card className="iw-form-card">
        <h2>{workoutText(locale, "reviewEvidence")}</h2>
        <p>{workoutText(locale, "reviewEvidenceDescription")}</p>
        <Alert variant="info">
          <p>{workoutText(locale, "noDiagnosis")}</p>
        </Alert>
        <Button loading={loading} onClick={() => void analyze()}>
          {workoutText(locale, "analyzeAdaptation")}
        </Button>
      </Card>
      {result ? <AdaptationResult result={result} /> : null}
    </IntelligentWorkoutShell>
  );
}
