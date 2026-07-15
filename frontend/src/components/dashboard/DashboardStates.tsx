import { Button, Card, ErrorState, Skeleton } from "../ui";
import type { Locale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";

export function DashboardSkeleton({ locale }: { locale: Locale }) {
  const copy = dashboardCopy[locale];
  return (
    <main className="dashboard-shell" aria-busy="true" aria-label={copy.loading}>
      <div className="dashboard-skeleton-header">
        <Skeleton width="9rem" height="2rem" />
        <Skeleton width="14rem" height="1rem" />
      </div>
      <Card className="dashboard-skeleton-priority">
        <Skeleton width="8rem" />
        <Skeleton width="70%" height="2.25rem" />
        <Skeleton width="88%" />
        <Skeleton width="10rem" height="2.75rem" />
      </Card>
      <div className="dashboard-skeleton-grid">
        <Card>
          <Skeleton height="15rem" />
        </Card>
        <Card>
          <Skeleton height="15rem" />
        </Card>
      </div>
      <span className="sr-only" role="status">
        {copy.loading}
      </span>
    </main>
  );
}

export function DashboardErrorState({
  locale,
  sessionExpired,
  onRetry,
  onSignIn,
}: {
  locale: Locale;
  sessionExpired: boolean;
  onRetry: () => void;
  onSignIn: () => void;
}) {
  const copy = dashboardCopy[locale];
  return (
    <main className="dashboard-shell dashboard-error-shell">
      <ErrorState
        action={
          <Button onClick={sessionExpired ? onSignIn : onRetry}>
            {sessionExpired ? copy.signOut : copy.retry}
          </Button>
        }
      />
      <p role="alert">{sessionExpired ? copy.sessionExpired : copy.errorBody}</p>
    </main>
  );
}
