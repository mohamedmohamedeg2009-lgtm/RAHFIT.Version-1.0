import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";
import { DashboardAnalytics } from "../../components/dashboard/DashboardAnalytics";
import { DashboardHeader } from "../../components/dashboard/DashboardHeader";
import { DashboardHero } from "../../components/dashboard/DashboardHero";
import { DashboardErrorState, DashboardSkeleton } from "../../components/dashboard/DashboardStates";
import { DashboardTimeline } from "../../components/dashboard/DashboardTimeline";
import { Alert } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import { useAuth } from "../../hooks/useAuth";
import { ApiConnectionError, ApiError } from "../../services/apiClient";
import { dashboardService } from "../../services/dashboardService";
import type { DashboardSummaryData } from "../../types/dashboard";

export default function DashboardPage() {
  const { locale } = useLocale();
  const { user, logout } = useAuth();
  const copy = dashboardCopy[locale];
  const [dashboard, setDashboard] = useState<DashboardSummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const controllerRef = useRef<AbortController | null>(null);
  const load = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setLoading(true);
    setError(null);
    try {
      const next = await dashboardService.getSummary({ signal: controller.signal });
      if (controllerRef.current === controller) setDashboard(next);
    } catch (cause) {
      if (
        !(cause instanceof ApiConnectionError && cause.message === "The request was cancelled.") &&
        controllerRef.current === controller
      )
        setError(cause);
    } finally {
      if (controllerRef.current === controller) setLoading(false);
    }
  }, []);
  useEffect(() => {
    const task = window.setTimeout(() => void load(), 0);
    return () => {
      window.clearTimeout(task);
      controllerRef.current?.abort();
    };
  }, [load]);
  const leaveSession = () => void logout().catch(() => undefined);
  if (loading && !dashboard) return <DashboardSkeleton locale={locale} />;
  if (!dashboard)
    return (
      <DashboardErrorState
        locale={locale}
        sessionExpired={error instanceof ApiError && error.status === 401}
        onRetry={load}
        onSignIn={leaveSession}
      />
    );

  // The current chart needs all its displayed dimensions. Do not turn absent
  // measurements into zeroes just to draw a chart.
  const analytics = dashboard.history
    .filter(
      (p) =>
        p.caloriesConsumed !== null &&
        p.workoutsCompleted !== null &&
        p.activeMinutes !== null &&
        p.readinessScore !== null,
    )
    .map((p) => ({
      day: p.date,
      dayAr: p.date,
      calories: p.caloriesConsumed!,
      activeMinutes: p.activeMinutes!,
      workouts: p.workoutsCompleted!,
      healthScore: p.readinessScore!,
    }));
  const events = dashboard.recentActivities.map((item) => ({
    id: item.id,
    time: new Intl.DateTimeFormat(locale, { hour: "numeric", minute: "2-digit" }).format(
      new Date(item.occurredAt),
    ),
    timeAr: new Intl.DateTimeFormat("ar", { hour: "numeric", minute: "2-digit" }).format(
      new Date(item.occurredAt),
    ),
    title: item.title,
    titleAr: item.title,
    description: item.detail ?? undefined,
    descriptionAr: item.detail ?? undefined,
    type: item.kind === "workout" ? ("workout" as const) : ("recovery" as const),
    status: item.status === "completed" ? ("completed" as const) : ("upcoming" as const),
  }));
  return (
    <div className="dashboard-page">
      <DashboardHeader displayName={dashboard.user.displayName} email={user?.email} />
      <motion.main
        className="dashboard-shell"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        {dashboard.metadata.partialData && (
          <Alert variant="warning" title={copy.partialTitle}>
            <p>{copy.partialBody}</p>
          </Alert>
        )}
        {error !== null && (
          <Alert variant="danger" title={copy.errorTitle}>
            <p>{copy.errorBody}</p>
            <button className="ds-button ds-button-ghost ds-button-sm" onClick={() => void load()}>
              {copy.retry}
            </button>
          </Alert>
        )}
        <DashboardHero data={dashboard} locale={locale} />
        <div className="dashboard-grid-layout-p2">
          <DashboardAnalytics state={analytics.length ? "ready" : "empty"} data={analytics} />
          <div className="dashboard-timeline-full">
            <DashboardTimeline state={events.length ? "ready" : "empty"} events={events} />
          </div>
        </div>
        <footer className="dashboard-freshness">
          <span>{dashboard.metadata.dataFreshness}</span>
          <span>Dashboard v{dashboard.metadata.dashboardVersion}</span>
        </footer>
      </motion.main>
    </div>
  );
}
