import { Link, NavLink } from "react-router-dom";

import { useLocale } from "../../contexts/LocaleContext";
import { workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";
import type { WorkoutClientError } from "../../services/workoutErrorMapper";
import type {
  WorkoutAdaptationResponse,
  WorkoutDay,
  WorkoutPlanResponse,
  WorkoutSessionResponse,
} from "../../types/intelligentWorkout";
import { Alert, Badge, Button, Card, LinearProgress } from "../ui";
import { RahafitLogo } from "../common/RahafitLogo";

export function IntelligentWorkoutShell({
  children,
  title,
  description,
}: {
  children: React.ReactNode;
  title: string;
  description: string;
}) {
  const { locale, toggleLocale } = useLocale();
  const t = (key: Parameters<typeof workoutText>[1]) => workoutText(locale, key);
  return (
    <div className="iw-page">
      <header className="iw-topbar">
        <Link to="/app" className="workout-brand">
          <RahafitLogo size="sm" />
        </Link>
        <nav aria-label={t("navigation")}>
          <NavLink to="/intelligent-workouts" end>
            {t("overview")}
          </NavLink>
          <NavLink to="/intelligent-workouts/history/plans">{t("plans")}</NavLink>
          <NavLink to="/intelligent-workouts/history/sessions">{t("sessions")}</NavLink>
          <Link to="/app">{t("dashboard")}</Link>
          <button
            className="iw-language-toggle"
            type="button"
            aria-label={t("languageLabel")}
            onClick={toggleLocale}
          >
            {t("language")}
          </button>
        </nav>
      </header>
      <main className="iw-shell">
        <header className="iw-hero">
          <Badge>{t("featureBadge")}</Badge>
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
  const { locale } = useLocale();
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
            {workoutText(locale, "retry")}
          </Button>
        ) : null}
      </div>
    </Alert>
  );
}

export function PlanSummary({ plan }: { plan: WorkoutPlanResponse }) {
  const { locale } = useLocale();
  return (
    <Card className="iw-plan-summary">
      <div>
        <span>{workoutText(locale, "plan")}</span>
        <strong>{workoutEnumLabel(plan.plan_type, locale)}</strong>
      </div>
      <div>
        <span>{workoutText(locale, "schedule")}</span>
        <strong>
          {workoutText(locale, "daysPerWeek", { count: plan.training_days_per_week })}
        </strong>
      </div>
      <div>
        <span>{workoutText(locale, "cycle")}</span>
        <strong>{workoutText(locale, "weeks", { count: plan.duration_weeks })}</strong>
      </div>
      <div>
        <span>{workoutText(locale, "status")}</span>
        <Badge>{workoutEnumLabel(plan.status, locale)}</Badge>
      </div>
      <div>
        <span>{workoutText(locale, "generation")}</span>
        <strong>{workoutEnumLabel(plan.generation_mode, locale)}</strong>
      </div>
      <div>
        <span>{workoutText(locale, "version")}</span>
        <strong>v{plan.version}</strong>
      </div>
    </Card>
  );
}

export function SafetyNotices({ plan }: { plan: WorkoutPlanResponse }) {
  const { locale } = useLocale();
  if (!plan.warnings.length && !plan.safety_notes.length) return null;
  return (
    <section className="iw-safety" aria-labelledby="iw-safety-title">
      <h2 id="iw-safety-title">{workoutText(locale, "safetyGuidance")}</h2>
      {plan.warnings.map((warning) => (
        <Alert
          key={warning.code}
          variant={warning.professional_guidance ? "warning" : "info"}
          title={workoutText(
            locale,
            warning.professional_guidance ? "professionalGuidance" : "planNotice",
          )}
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
  const { locale } = useLocale();
  const exerciseCount = day.sections.reduce(
    (count, section) => count + section.exercises.length,
    0,
  );
  return (
    <Card className="iw-day-card">
      <div>
        <div className="iw-inline">
          <Badge>{workoutText(locale, "day", { count: day.day_number })}</Badge>
          {day.high_intensity ? (
            <Badge className="iw-badge-warning">{workoutText(locale, "highIntensity")}</Badge>
          ) : null}
        </div>
        <h3>{day.title}</h3>
        <p>
          {day.focus} · {workoutText(locale, "exerciseCount", { count: exerciseCount })} ·{" "}
          {workoutText(locale, "minutes", { count: day.estimated_duration_minutes })}
        </p>
      </div>
      <Link
        className="ds-button ds-button-primary ds-button-md"
        to={`/intelligent-workouts/plans/${planId}/session/${day.day_number}`}
      >
        {workoutText(locale, "startSession")}
      </Link>
    </Card>
  );
}

export function SessionStatusCard({ session }: { session: WorkoutSessionResponse }) {
  const { locale } = useLocale();
  return (
    <Card className="iw-session-status" aria-live="polite">
      <div>
        <strong>{workoutEnumLabel(session.status, locale)}</strong>
        <span>
          {workoutText(locale, "minutePlan", { count: session.planned_duration_minutes })}
        </span>
      </div>
      <LinearProgress
        value={session.completion_percentage}
        label={workoutText(locale, "sessionProgress")}
      />
      <strong>{session.completion_percentage}%</strong>
    </Card>
  );
}

export function AdaptationResult({ result }: { result: WorkoutAdaptationResponse }) {
  const { locale } = useLocale();
  const variant =
    result.severity === "info" ? "info" : result.severity === "caution" ? "warning" : "danger";
  return (
    <Alert
      variant={variant}
      title={workoutText(locale, "recommendation", {
        action: workoutEnumLabel(result.action, locale),
      })}
    >
      <p>{workoutText(locale, "advisoryOnly")}</p>
      <ul>
        {result.evidence_summary.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      {result.affected_day_number ? (
        <p>{workoutText(locale, "affectedDay", { count: result.affected_day_number })}</p>
      ) : null}
      {result.affected_exercise_id ? (
        <p>{workoutText(locale, "affectedExercise", { id: result.affected_exercise_id })}</p>
      ) : null}
    </Alert>
  );
}
