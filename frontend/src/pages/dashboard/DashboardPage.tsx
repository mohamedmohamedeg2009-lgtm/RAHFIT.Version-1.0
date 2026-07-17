import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";

import {
  AssessmentSummaryCard,
  DailyPriorityCard,
  FeatureStatusGrid,
  ProgressSnapshotCard,
  NutritionSnapshotCard,
  QuickActions,
  SafetyNoticeCard,
} from "../../components/dashboard/DashboardCards";
import { DashboardHeader } from "../../components/dashboard/DashboardHeader";
import { DashboardHero } from "../../components/dashboard/DashboardHero";
import { DashboardErrorState, DashboardSkeleton } from "../../components/dashboard/DashboardStates";
import { Alert } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { useAuth } from "../../hooks/useAuth";
import { dashboardCopy } from "../../i18n/dashboard";
import { ApiError } from "../../services/apiClient";
import { dashboardService } from "../../services/dashboardService";
import type { DashboardData } from "../../types/dashboard";

export default function DashboardPage() {
  const { locale } = useLocale();
  const { user, logout } = useAuth();
  const copy = dashboardCopy[locale];
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setDashboard(await dashboardService.getDashboard());
    } catch (cause) {
      setError(cause);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // Initial dashboard loading synchronizes this route with the authenticated API aggregate.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void load();
  }, [load]);

  const leaveSession = () => void logout().catch(() => undefined);

  if (loading && !dashboard) return <DashboardSkeleton locale={locale} />;
  if (!dashboard) {
    return (
      <DashboardErrorState
        locale={locale}
        sessionExpired={error instanceof ApiError && error.status === 401}
        onRetry={() => void load()}
        onSignIn={leaveSession}
      />
    );
  }

  return (
    <div className="dashboard-page">
      <DashboardHeader displayName={dashboard.user.displayName} email={user?.email} />
      <motion.main
        className="dashboard-shell"
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        style={{ marginTop: "24px" }}
      >
        {dashboard.metadata.partialData ? (
          <Alert variant="warning" title={copy.partialTitle}>
            <p>{copy.partialBody}</p>
          </Alert>
        ) : null}

        {/* Premium Health Overview Hero Header */}
        <DashboardHero data={dashboard} locale={locale} />

        <DailyPriorityCard priority={dashboard.dailyPriority} locale={locale} onRefresh={load} />

        {dashboard.safetyNotice ? (
          <SafetyNoticeCard notice={dashboard.safetyNotice} locale={locale} />
        ) : null}

        <div className="dashboard-primary-grid">
          <AssessmentSummaryCard assessment={dashboard.assessment} locale={locale} />
          <ProgressSnapshotCard
            progress={dashboard.progress}
            user={dashboard.user}
            locale={locale}
          />
        </div>

        {dashboard.nutrition ? (
          <NutritionSnapshotCard nutrition={dashboard.nutrition} />
        ) : null}

        <FeatureStatusGrid features={dashboard.features} locale={locale} />

        <QuickActions actions={dashboard.quickActions} locale={locale} onLogout={leaveSession} />

        <footer className="dashboard-freshness">
          <span>{dashboard.metadata.dataFreshness}</span>
          <span>Dashboard v{dashboard.metadata.dashboardVersion}</span>
        </footer>
      </motion.main>
    </div>
  );
}

