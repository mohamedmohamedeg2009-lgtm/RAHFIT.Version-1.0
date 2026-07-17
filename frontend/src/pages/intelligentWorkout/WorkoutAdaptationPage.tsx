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

export default function WorkoutAdaptationPage() {
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
      setError(mapWorkoutError(cause));
    } finally {
      setLoading(false);
    }
  };
  return (
    <IntelligentWorkoutShell
      title="Adaptation review"
      description="Analyze recorded sessions for deterministic guidance without mutating the plan."
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void analyze()} /> : null}
      <Card className="iw-form-card">
        <h2>Review current evidence</h2>
        <p>
          The server reviews completed and in-progress session evidence. Recommendations remain
          advisory and are never applied automatically.
        </p>
        <Alert variant="info">
          <p>RAHFIT AI does not diagnose injury or replace professional guidance.</p>
        </Alert>
        <Button loading={loading} onClick={() => void analyze()}>
          Analyze adaptation
        </Button>
      </Card>
      {result ? <AdaptationResult result={result} /> : null}
    </IntelligentWorkoutShell>
  );
}
