import { useCallback, useEffect, useRef, useState } from "react";
import { motion } from "framer-motion";

import {
  AssessmentSummaryCard,
  DailyPriorityCard,
  FeatureStatusGrid,
  NutritionSnapshotCard,
  ProgressSnapshotCard,
  QuickActions,
  SafetyNoticeCard,
} from "../../components/dashboard/DashboardCards";
import { DashboardAnalytics } from "../../components/dashboard/DashboardAnalytics";
import { DashboardGoals } from "../../components/dashboard/DashboardGoals";
import { DashboardHeader } from "../../components/dashboard/DashboardHeader";
import { DashboardHero } from "../../components/dashboard/DashboardHero";
import { DashboardMetricRingCard } from "../../components/dashboard/DashboardMetricRingCard";
import { DashboardErrorState, DashboardSkeleton } from "../../components/dashboard/DashboardStates";
import { DashboardTimeline } from "../../components/dashboard/DashboardTimeline";
import { Alert } from "../../components/ui";
import { useLocale } from "../../contexts/LocaleContext";
import { dashboardCopy } from "../../i18n/dashboard";
import { useAuth } from "../../hooks/useAuth";
import { ApiConnectionError, ApiError } from "../../services/apiClient";
import { dashboardService } from "../../services/dashboardService";
import type { DashboardData } from "../../types/dashboard";

export default function DashboardPage() {
  const { locale } = useLocale();
  const { user, logout } = useAuth();
  const copy = dashboardCopy[locale];
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
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
      const next = await dashboardService.getDashboard({ signal: controller.signal });
      if (controllerRef.current === controller) setDashboard(next);
    } catch (cause) {
      if (cause instanceof ApiConnectionError && cause.message === "The request was cancelled.")
        return;
      if (controllerRef.current === controller) setError(cause);
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
  if (!dashboard) {
    return (
      <DashboardErrorState
        locale={locale}
        sessionExpired={error instanceof ApiError && error.status === 401}
        onRetry={load}
        onSignIn={leaveSession}
      />
    );
  }

  const nutritionGoals = dashboard.nutrition
    ? [
        {
          id: "water",
          title: "Water Intake",
          titleAr: "ترطيب الجسم",
          current: dashboard.nutrition.waterConsumedMl,
          target: dashboard.nutrition.waterTargetMl,
          unit: "ml",
          unitAr: "مل",
          iconType: "water" as const,
        },
        {
          id: "meals",
          title: "Meals completed",
          titleAr: "الوجبات المكتملة",
          current: dashboard.nutrition.mealsCompleted,
          target: dashboard.nutrition.totalMeals,
          unit: "",
          unitAr: "",
          iconType: "workout" as const,
        },
      ]
    : [];

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
        <DailyPriorityCard priority={dashboard.dailyPriority} locale={locale} onRefresh={load} />
        {dashboard.safetyNotice && (
          <SafetyNoticeCard notice={dashboard.safetyNotice} locale={locale} />
        )}

        {dashboard.nutrition && (
          <div className="dashboard-row-p3-metrics">
            <DashboardMetricRingCard
              type="hydration"
              current={dashboard.nutrition.waterConsumedMl}
              target={dashboard.nutrition.waterTargetMl}
            />
            <DashboardMetricRingCard
              type="calories"
              current={dashboard.nutrition.caloriesConsumed}
              target={dashboard.nutrition.targetCalories}
            />
          </div>
        )}
        <div className="dashboard-grid-layout-p2">
          <DashboardAnalytics state="empty" data={[]} />
          <DashboardGoals goals={nutritionGoals} />
          <div className="dashboard-timeline-full">
            <DashboardTimeline events={[]} />
          </div>
        </div>
        <div className="dashboard-primary-grid">
          <AssessmentSummaryCard assessment={dashboard.assessment} locale={locale} />
          <ProgressSnapshotCard
            progress={dashboard.progress}
            user={dashboard.user}
            locale={locale}
          />
        </div>
        {dashboard.nutrition && <NutritionSnapshotCard nutrition={dashboard.nutrition} />}
        <FeatureStatusGrid features={dashboard.features} locale={locale} dashboard={dashboard} />
        <QuickActions actions={dashboard.quickActions} locale={locale} onLogout={leaveSession} />
        <footer className="dashboard-freshness">
          <span>{dashboard.metadata.dataFreshness}</span>
          <span>Dashboard v{dashboard.metadata.dashboardVersion}</span>
        </footer>
      </motion.main>
    </div>
  );
}
