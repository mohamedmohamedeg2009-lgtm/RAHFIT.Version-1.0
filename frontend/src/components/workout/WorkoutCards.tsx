import { Link } from "react-router-dom";

import { Badge, Card, LinearProgress } from "../ui";
import type { Locale } from "../../contexts/LocaleContext";
import { workoutCopy } from "../../i18n/workout";
import type { WorkoutDay, WorkoutPlan, WorkoutSession } from "../../types/workout";
import { RahafitLogo } from "../common/RahafitLogo";

export function WorkoutShell({
  children,
  locale,
  title,
}: {
  children: React.ReactNode;
  locale: Locale;
  title?: string;
}) {
  const copy = workoutCopy[locale];
  return (
    <div className="workout-page">
      <header className="workout-topbar">
        <Link to="/app" className="workout-brand" aria-label={copy.dashboard}>
          <RahafitLogo size="sm" />
        </Link>
        <nav aria-label="Workout navigation">
          <Link to="/workouts">{copy.today}</Link>
          <Link to="/workouts/history">{copy.history}</Link>
          <Link to="/app">{copy.dashboard}</Link>
        </nav>
      </header>
      <main className="workout-shell">
        <div className="workout-hero">
          <Badge>RAHAFIT TRAINING</Badge>
          <h1>{title ?? copy.title}</h1>
          <p>{copy.subtitle}</p>
        </div>
        {children}
      </main>
    </div>
  );
}

export function PlanOverview({ plan }: { plan: WorkoutPlan }) {
  return (
    <Card className="workout-overview">
      <div>
        <span>Goal</span>
        <strong>{plan.goal.replaceAll("_", " ")}</strong>
      </div>
      <div>
        <span>Experience</span>
        <strong>{plan.experience}</strong>
      </div>
      <div>
        <span>Schedule</span>
        <strong>{plan.availableDays} days / week</strong>
      </div>
      <div>
        <span>Duration</span>
        <strong>{plan.sessionDurationMinutes} min</strong>
      </div>
    </Card>
  );
}

export function WorkoutDayCard({
  day,
  planId,
  featured = false,
}: {
  day: WorkoutDay;
  planId: string;
  featured?: boolean;
}) {
  return (
    <Card className={`workout-day-card ${featured ? "is-today" : ""}`}>
      <div>
        <Badge>{featured ? "TODAY" : `DAY ${day.dayNumber}`}</Badge>
        <h2>{day.title}</h2>
        <p>
          {day.exercises.length} exercises · {day.estimatedDurationMinutes} min
        </p>
      </div>
      <Link
        className="ds-button ds-button-primary ds-button-md"
        to={`/workouts/${planId}/session/${day.id}`}
      >
        Open session
      </Link>
    </Card>
  );
}

export function SessionProgress({ session }: { session: WorkoutSession }) {
  return (
    <Card className="workout-session-progress" aria-live="polite">
      <LinearProgress value={session.progress.completionPercentage} label="Workout progress" />
      <strong>
        {session.progress.completedSets} / {session.progress.totalSets} sets
      </strong>
    </Card>
  );
}
