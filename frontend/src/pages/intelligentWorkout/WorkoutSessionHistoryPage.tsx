import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  IntelligentWorkoutShell,
  WorkoutErrorAlert,
} from "../../components/intelligentWorkout/WorkoutExperience";
import { formatDate, label } from "../../components/intelligentWorkout/utils";
import { Badge, Button, Card, EmptyState, Skeleton } from "../../components/ui";
import { intelligentWorkoutService } from "../../services/intelligentWorkoutService";
import { mapWorkoutError, type WorkoutClientError } from "../../services/workoutErrorMapper";
import type { WorkoutSessionResponse } from "../../types/intelligentWorkout";

const pageSize = 10;
export default function WorkoutSessionHistoryPage() {
  const [items, setItems] = useState<WorkoutSessionResponse[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<WorkoutClientError | null>(null);
  const load = useCallback(async (offset = 0) => {
    setLoading(true);
    setError(null);
    try {
      const page = await intelligentWorkoutService.listSessions(pageSize, offset);
      setItems((current) => (offset ? [...current, ...page.items] : page.items));
      setHasMore(page.has_more);
    } catch (cause) {
      setError(mapWorkoutError(cause));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    // Initial route loading synchronizes the protected screen with its server resource.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);
  return (
    <IntelligentWorkoutShell
      title="Session history"
      description="Resume open sessions and review backend-calculated workout outcomes."
    >
      {error ? <WorkoutErrorAlert error={error} onRetry={() => void load(items.length)} /> : null}
      {loading && !items.length ? (
        <Card>
          <Skeleton height="10rem" />
        </Card>
      ) : items.length ? (
        <div className="iw-list">
          {items.map((session) => (
            <Card className="iw-history-card" key={session.session_id}>
              <div>
                <div className="iw-inline">
                  <Badge>{label(session.status)}</Badge>
                  {session.adaptation_flags.length ? (
                    <Badge className="iw-badge-warning">Review flagged</Badge>
                  ) : null}
                </div>
                <h2>Day {session.day_number}</h2>
                <p>
                  {session.completion_percentage}% complete · Started{" "}
                  {formatDate(session.started_at)}
                </p>
              </div>
              <Link to={`/intelligent-workouts/sessions/${session.session_id}`}>
                {session.status === "in_progress" ? "Resume" : "View"}
              </Link>
            </Card>
          ))}
          {hasMore ? (
            <Button variant="outline" loading={loading} onClick={() => void load(items.length)}>
              Load more
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
