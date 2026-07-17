import { Link, NavLink } from "react-router-dom";

import { Alert, Badge, Button, Card, LinearProgress } from "../ui";
import type {
  WorkoutAdaptationResponse,
  WorkoutDay,
  WorkoutPlanResponse,
  WorkoutSessionResponse,
} from "../../types/intelligentWorkout";
import type { WorkoutClientError } from "../../services/workoutErrorMapper";
import { label } from "./utils";

export function IntelligentWorkoutShell({
  children,
  title,
  description,
}: {
  children: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="iw-page">
      <header className="iw-topbar">
        <Link to="/app" className="workout-brand">
          <span>R</span> RAHFIT AI
        </Link>
        <nav aria-label="Intelligent workout navigation">
          <NavLink to="/intelligent-workouts" end>
            Overview
          </NavLink>
          <NavLink to="/intelligent-workouts/history/plans">Plans</NavLink>
          <NavLink to="/intelligent-workouts/history/sessions">Sessions</NavLink>
          <Link to="/app">Dashboard</Link>
        </nav>
      </header>
      <main className="iw-shell">
        <header className="iw-hero">
          <Badge>INTELLIGENT TRAINING</Badge>
          <h1>{title}</h1>
          <p>{description}</p>
        </header>
        {children}
      </main>
    </div>
  );
}

export function WorkoutErrorAlert({
  error,
  onRetry,
}: {
  error: WorkoutClientError;
  onRetry?: () => void;
}) {
  return (
    <Alert variant="danger" title={error.title}>
      <p>{error.message}</p>
      <div className="iw-alert-actions">
        {error.actionPath ? (
          <Link className="ds-button ds-button-outline ds-button-sm" to={error.actionPath}>
            {error.actionLabel}
          </Link>
        ) : null}
        {error.retryable && onRetry ? (
          <Button size="sm" variant="outline" onClick={onRetry}>
            Try again
          </Button>
        ) : null}
      </div>
    </Alert>
  );
}

export function PlanSummary({ plan }: { plan: WorkoutPlanResponse }) {
  return (
    <Card className="iw-plan-summary">
      <div>
        <span>Plan</span>
        <strong>{label(plan.plan_type)}</strong>
      </div>
      <div>
        <span>Schedule</span>
        <strong>{plan.training_days_per_week} days / week</strong>
      </div>
      <div>
        <span>Cycle</span>
        <strong>{plan.duration_weeks} weeks</strong>
      </div>
      <div>
        <span>Status</span>
        <Badge>{plan.status}</Badge>
      </div>
      <div>
        <span>Generation</span>
        <strong>{label(plan.generation_mode)}</strong>
      </div>
      <div>
        <span>Version</span>
        <strong>v{plan.version}</strong>
      </div>
    </Card>
  );
}

export function SafetyNotices({ plan }: { plan: WorkoutPlanResponse }) {
  if (!plan.warnings.length && !plan.safety_notes.length) return null;
  return (
    <section className="iw-safety" aria-labelledby="iw-safety-title">
      <h2 id="iw-safety-title">Safety guidance</h2>
      {plan.warnings.map((warning) => (
        <Alert
          key={warning.code}
          variant={warning.professional_guidance ? "warning" : "info"}
          title={warning.professional_guidance ? "Professional guidance" : "Plan notice"}
        >
          <p>{warning.message}</p>
        </Alert>
      ))}
      {plan.safety_notes.length ? (
        <Card>
          <ul>
            {plan.safety_notes.map((note) => (
              <li key={note}>{note}</li>
            ))}
          </ul>
        </Card>
      ) : null}
    </section>
  );
}

export function WorkoutDayCard({ planId, day }: { planId: string; day: WorkoutDay }) {
  const exerciseCount = day.sections.reduce(
    (count, section) => count + section.exercises.length,
    0,
  );
  return (
    <Card className="iw-day-card">
      <div>
        <div className="iw-inline">
          <Badge>DAY {day.day_number}</Badge>
          {day.high_intensity ? <Badge className="iw-badge-warning">High intensity</Badge> : null}
        </div>
        <h3>{day.title}</h3>
        <p>
          {day.focus} · {exerciseCount} exercises · {day.estimated_duration_minutes} minutes
        </p>
      </div>
      <Link
        className="ds-button ds-button-primary ds-button-md"
        to={`/intelligent-workouts/plans/${planId}/session/${day.day_number}`}
      >
        Start session
      </Link>
    </Card>
  );
}

export function SessionStatusCard({ session }: { session: WorkoutSessionResponse }) {
  return (
    <Card className="iw-session-status" aria-live="polite">
      <div>
        <strong>{label(session.status)}</strong>
        <span>{session.planned_duration_minutes} minute plan</span>
      </div>
      <LinearProgress
        value={session.completion_percentage}
        label="Server-calculated session progress"
      />
      <strong>{session.completion_percentage}%</strong>
    </Card>
  );
}

export function AdaptationResult({ result }: { result: WorkoutAdaptationResponse }) {
  const variant =
    result.severity === "info" ? "info" : result.severity === "caution" ? "warning" : "danger";
  return (
    <Alert variant={variant} title={`Recommendation: ${label(result.action)}`}>
      <p>This is guidance only. It has not changed your plan.</p>
      <ul>
        {result.evidence_summary.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      {result.affected_day_number ? <p>Affected day: {result.affected_day_number}</p> : null}
      {result.affected_exercise_id ? (
        <p>Affected exercise: {label(result.affected_exercise_id)}</p>
      ) : null}
    </Alert>
  );
}
