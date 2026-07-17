import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { useLocale } from "../../contexts/LocaleContext";
import { formatWorkoutDate, workoutEnumLabel, workoutText } from "../../i18n/intelligentWorkout";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutSessionResponse } from "../../types/intelligentWorkout";
import { Badge, Button, Card, EmptyState, Skeleton } from "../../components/ui";

const pageSize = 10;
export default function WorkoutSessionHistoryPage() {
  const { locale } = useLocale();
  const [items, setItems] = useState<WorkoutSessionResponse[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(
    async (offset = 0) => {
      setLoading(true);
      setError(null);
      try {
        const page = await intelligentWorkoutService.listSessions(pageSize, offset);
        setItems((current) => (offset ? [...current, ...page.items] : page.items));
        setHasMore(page.has_more);
      } catch (cause) {
        setError(mapWorkoutError(cause, locale));
      } finally {
        setLoading(false);
      }
    },
    [locale],
  );
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  return (
    <IntelligentWorkoutShell
      title={workoutText(locale, "sessionHistoryTitle")}
      description={workoutText(locale, "sessionHistoryDescription")}
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load(items.length)} /> : null}
      {loading && !items.length ? (
        <Card aria-live="polite" aria-busy="true">
          <span className="sr-only">{workoutText(locale, "loadingSessionHistory")}</span>
          <Skeleton height="10rem" />
        </Card>
      ) : items.length ? (
        <div className="iw-list">
          {items.map((session) => (
            <Card className="iw-history-card" key={session.session_id}>
              <div>
                <div className="iw-inline">
                  <Badge>{workoutEnumLabel(session.status, locale)}</Badge>
                  {session.adaptation_flags.length ? (
                    <Badge className="iw-badge-warning">
                      {workoutText(locale, "reviewFlagged")}
                    </Badge>
                  ) : null}
                </div>
                <h2>{workoutText(locale, "dayTitle", { count: session.day_number })}</h2>
                <p>
                  {workoutText(locale, "completePercent", {
                    count: session.completion_percentage,
                  })}{" "}
                  ·{" "}
                  {workoutText(locale, "started", {
                    date: formatWorkoutDate(session.started_at, locale),
                  })}
                </p>
              </div>
              <Link to={`/intelligent-workouts/sessions/${session.session_id}`}>
                {workoutText(locale, session.status === "in_progress" ? "resume" : "view")}
              </Link>
            </Card>
          ))}
          {hasMore ? (
            <Button variant="outline" loading={loading} onClick={() => void load(items.length)}>
              {workoutText(locale, "loadMore")}
            </Button>
          ) : null}
        </div>
      ) : (
        <Card>
          <EmptyState kind="workout" />
        </Card>
      )}
    </IntelligentWorkoutShell>
  );
}
