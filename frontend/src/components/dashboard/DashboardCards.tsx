import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Activity,
  Flame,
  ShieldAlert,
  Compass,
  TrendingUp,
  Sparkles,
  ArrowRight,
  Layers,
  HelpCircle,
  CheckCircle2,
  CircleAlert,
  LockKeyhole,
} from "lucide-react";

import { Badge, Button, Card, LinearProgress, MetricCard } from "../ui";
import type { Locale } from "../../contexts/LocaleContext";
import {
  actionLabel,
  dashboardCopy,
  dashboardStatusLabel,
  featureStatusLabel,
} from "../../i18n/dashboard";
import { categoryLabel, riskLabel } from "../../i18n/assessment";
import type {
  DashboardAction,
  DashboardAssessmentSummary,
  DashboardFeature,
  DashboardProgressSnapshot,
  DashboardSafetyNotice,
  DashboardUserSummary,
} from "../../types/dashboard";
import type { DashboardData } from "../../types/dashboard";

export function NutritionSnapshotCard({ nutrition }: { nutrition: DashboardData["nutrition"] }) {
  if (!nutrition) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <Card className="dashboard-progress-card" style={{ padding: "32px", borderRadius: "28px" }}>
        <div
          className="dashboard-section-heading"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "24px",
          }}
        >
          <h2 style={{ fontSize: "20px", fontWeight: 700, margin: 0 }}>Today's Nutrition & Fuel</h2>
          <Link
            to={nutrition.destinationRoute}
            style={{
              color: "var(--color-primary)",
              fontWeight: 700,
              fontSize: "14px",
              display: "flex",
              alignItems: "center",
              gap: "4px",
              textDecoration: "none",
            }}
          >
            Open Plan <ArrowRight size={16} />
          </Link>
        </div>
        <div style={{ display: "grid", gap: "20px" }}>
          <div>
            <LinearProgress
              value={nutrition.caloriesConsumed}
              max={nutrition.targetCalories}
              label="Calories Target"
            />
          </div>
          <div
            className="dashboard-metric-grid"
            style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}
          >
            <MetricCard
              style={{
                background: "var(--color-background)",
                border: "1px solid var(--color-border)",
              }}
            >
              <span
                style={{ fontSize: "12px", color: "var(--color-text-secondary)", fontWeight: 700 }}
              >
                Calories Remaining
              </span>
              <strong
                style={{ fontSize: "24px", color: "var(--color-text-primary)", fontWeight: 800 }}
              >
                {nutrition.caloriesRemaining}
              </strong>
              <small style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>kcal</small>
            </MetricCard>
            <MetricCard
              style={{
                background: "var(--color-background)",
                border: "1px solid var(--color-border)",
              }}
            >
              <span
                style={{ fontSize: "12px", color: "var(--color-text-secondary)", fontWeight: 700 }}
              >
                Meals Completed
              </span>
              <strong
                style={{ fontSize: "24px", color: "var(--color-text-primary)", fontWeight: 800 }}
              >
                {nutrition.mealsCompleted} / {nutrition.totalMeals}
              </strong>
            </MetricCard>
          </div>
          <div>
            <LinearProgress
              value={nutrition.waterConsumedMl}
              max={nutrition.waterTargetMl}
              label="Hydration Intake"
            />
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

export function DailyPriorityCard({
  priority,
  locale,
  onRefresh,
}: {
  priority: DashboardAction;
  locale: Locale;
  onRefresh: () => void;
}) {
  const copy = dashboardCopy[locale];
  const isRefresh = priority.actionType === "continue_available_feature";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <Card
        className={`dashboard-priority-card priority-${priority.severity}`}
        style={{
          borderLeft: `5px solid var(--color-${priority.severity === "danger" ? "danger" : "primary"})`,
          padding: "32px",
          borderRadius: "28px",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            display: "flex",
            gap: "24px",
            alignItems: "flex-start",
            position: "relative",
            zIndex: 1,
          }}
        >
          <div
            className="dashboard-priority-icon"
            style={{
              width: "56px",
              height: "56px",
              borderRadius: "16px",
              display: "grid",
              placeItems: "center",
              background: `rgba(${priority.severity === "danger" ? "239, 68, 68" : "15, 118, 110"}, 0.1)`,
              color: `var(--color-${priority.severity === "danger" ? "danger" : "primary"})`,
              flexShrink: 0,
            }}
          >
            {priority.severity === "danger" ? <ShieldAlert size={28} /> : <Compass size={28} />}
          </div>
          <div className="dashboard-priority-copy" style={{ flexGrow: 1 }}>
            <span
              className="dashboard-eyebrow"
              style={{
                fontSize: "12px",
                color: "var(--color-primary)",
                fontWeight: 800,
                textTransform: "uppercase",
                letterSpacing: "0.1em",
              }}
            >
              {copy.todayPriority}
            </span>
            <h2 style={{ fontSize: "24px", fontWeight: 800, margin: "8px 0" }}>{priority.title}</h2>
            <p
              style={{ fontSize: "16px", color: "var(--color-text-secondary)", margin: "0 0 16px" }}
            >
              {priority.description}
            </p>
            <details
              style={{ background: "rgba(0,0,0,0.02)", padding: "12px 16px", borderRadius: "12px" }}
            >
              <summary
                style={{
                  cursor: "pointer",
                  fontWeight: 700,
                  fontSize: "14px",
                  color: "var(--color-primary)",
                }}
              >
                {copy.whyThis}
              </summary>
              <p
                style={{
                  marginTop: "8px",
                  fontSize: "14px",
                  color: "var(--color-text-secondary)",
                  lineHeight: 1.5,
                }}
              >
                {priority.priorityReason}
              </p>
            </details>
          </div>
          <div className="dashboard-priority-action" style={{ alignSelf: "center", flexShrink: 0 }}>
            {isRefresh ? (
              <Button
                size="lg"
                onClick={onRefresh}
                style={{ height: "52px", borderRadius: "18px" }}
              >
                {actionLabel(priority.actionType, locale)}
              </Button>
            ) : priority.destinationRoute ? (
              <Link
                className="ds-button ds-button-primary ds-button-lg"
                to={priority.destinationRoute}
                style={{
                  height: "52px",
                  borderRadius: "18px",
                  display: "inline-flex",
                  alignItems: "center",
                  gap: "8px",
                }}
              >
                {actionLabel(priority.actionType, locale)}
                <ArrowRight size={18} />
              </Link>
            ) : null}
          </div>
        </div>
      </Card>
    </motion.div>
  );
}

export function SafetyNoticeCard({
  notice,
  locale,
}: {
  notice: DashboardSafetyNotice;
  locale: Locale;
}) {
  const copy = dashboardCopy[locale];
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
    >
      <Card
        className={`dashboard-safety-notice notice-${notice.severity}`}
        role={notice.status === "stop" ? "alert" : "status"}
        aria-live={notice.status === "stop" ? "assertive" : "polite"}
        style={{
          borderLeft: "5px solid var(--color-danger)",
          borderRadius: "28px",
          padding: "32px",
          display: "flex",
          gap: "20px",
          alignItems: "flex-start",
          background: "rgba(239, 68, 68, 0.04)",
        }}
      >
        <div
          className="dashboard-safety-mark"
          style={{
            width: "48px",
            height: "48px",
            borderRadius: "12px",
            background: "rgba(239, 68, 68, 0.1)",
            color: "var(--color-danger)",
            display: "grid",
            placeItems: "center",
            flexShrink: 0,
          }}
        >
          <ShieldAlert size={24} />
        </div>
        <div>
          <div
            className="dashboard-safety-heading"
            style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "8px" }}
          >
            <h2
              style={{ fontSize: "20px", fontWeight: 700, margin: 0, color: "var(--color-danger)" }}
            >
              {notice.title}
            </h2>
            {notice.planGenerationBlocked ? (
              <Badge
                style={{
                  background: "rgba(239, 68, 68, 0.1)",
                  color: "var(--color-danger)",
                  border: "none",
                }}
              >
                {copy.safetyBlocked}
              </Badge>
            ) : null}
          </div>
          <p
            style={{
              fontSize: "16px",
              color: "var(--color-text-secondary)",
              margin: 0,
              lineHeight: 1.6,
            }}
          >
            {notice.message}
          </p>
        </div>
      </Card>
    </motion.div>
  );
}

export function AssessmentSummaryCard({
  assessment,
  locale,
}: {
  assessment: DashboardAssessmentSummary;
  locale: Locale;
}) {
  const copy = dashboardCopy[locale];
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      style={{ height: "100%" }}
    >
      <Card
        className="dashboard-assessment-card"
        style={{
          padding: "32px",
          borderRadius: "28px",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <div>
          <div
            className="dashboard-section-heading"
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "flex-start",
              marginBottom: "20px",
            }}
          >
            <div>
              <span
                className="dashboard-eyebrow"
                style={{
                  fontSize: "12px",
                  color: "var(--color-primary)",
                  fontWeight: 800,
                  textTransform: "uppercase",
                  letterSpacing: "0.08em",
                }}
              >
                {copy.assessment}
              </span>
              <h2 style={{ fontSize: "24px", fontWeight: 800, margin: "4px 0" }}>
                {dashboardStatusLabel(assessment.status, locale)}
              </h2>
            </div>
            <Badge
              className={`dashboard-status status-${assessment.status}`}
              style={{
                background: `rgba(${assessment.status === "completed" ? "34, 197, 94" : "245, 158, 11"}, 0.1)`,
                color: `var(--color-${assessment.status === "completed" ? "success" : "warning"})`,
                border: "none",
                padding: "6px 12px",
                fontWeight: 700,
              }}
            >
              {dashboardStatusLabel(assessment.status, locale)}
            </Badge>
          </div>

          <div style={{ marginBottom: "24px" }}>
            <LinearProgress value={assessment.completionPercentage} label={copy.completion} />
          </div>

          <div
            className="dashboard-metric-grid"
            style={{
              display: "grid",
              gridTemplateColumns: "1fr 1fr",
              gap: "16px",
              marginBottom: "24px",
            }}
          >
            <MetricCard
              style={{
                background: "var(--color-background)",
                border: "1px solid var(--color-border)",
                padding: "20px",
              }}
            >
              <span
                style={{ fontSize: "12px", color: "var(--color-text-secondary)", fontWeight: 700 }}
              >
                {copy.readiness}
              </span>
              <strong
                style={{ fontSize: "28px", color: "var(--color-text-primary)", fontWeight: 800 }}
              >
                {assessment.readinessScore ?? copy.notCalculated}
              </strong>
              {assessment.readinessScore !== null ? (
                <small style={{ fontSize: "12px", color: "var(--color-text-muted)" }}>/ 100</small>
              ) : null}
            </MetricCard>
            <MetricCard
              style={{
                background: "var(--color-background)",
                border: "1px solid var(--color-border)",
                padding: "20px",
              }}
            >
              <span
                style={{ fontSize: "12px", color: "var(--color-text-secondary)", fontWeight: 700 }}
              >
                {copy.risk}
              </span>
              <strong
                style={{ fontSize: "20px", color: "var(--color-text-primary)", fontWeight: 800 }}
              >
                {assessment.riskLevel
                  ? riskLabel(assessment.riskLevel, locale)
                  : copy.notCalculated}
              </strong>
            </MetricCard>
          </div>

          <div
            className="dashboard-missing-categories"
            style={{
              borderTop: "1px solid var(--color-border)",
              paddingTop: "20px",
              marginBottom: "20px",
            }}
          >
            <h3 style={{ fontSize: "14px", fontWeight: 700, margin: "0 0 12px" }}>
              {copy.missing}
            </h3>
            {assessment.missingCategories.length ? (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "8px" }}>
                {assessment.missingCategories.map((category) => (
                  <Badge
                    key={category}
                    style={{ background: "rgba(0,0,0,0.04)", color: "var(--color-text-secondary)" }}
                  >
                    {categoryLabel(category, locale)}
                  </Badge>
                ))}
              </div>
            ) : (
              <p style={{ fontSize: "14px", color: "var(--color-text-secondary)", margin: 0 }}>
                {copy.noMissing}
              </p>
            )}
          </div>
        </div>

        {assessment.reassessmentRecommended ? (
          <div
            className="dashboard-reassessment"
            role="status"
            style={{
              background: "rgba(245, 158, 11, 0.05)",
              border: "1px solid rgba(245, 158, 11, 0.2)",
              color: "var(--color-warning)",
              padding: "12px 16px",
              borderRadius: "16px",
              fontSize: "14px",
              lineHeight: 1.5,
            }}
          >
            {copy.reassessment}
          </div>
        ) : null}
      </Card>
    </motion.div>
  );
}

export function FeatureStatusGrid({
  features,
  locale,
  dashboard,
}: {
  features: DashboardFeature[];
  locale: Locale;
  dashboard: DashboardData;
}) {
  const copy = dashboardCopy[locale];

  const getFeatureIcon = (key: string) => {
    switch (key) {
      case "assessment":
        return <Compass size={22} />;
      case "workout":
        return <Activity size={22} />;
      case "nutrition":
        return <Flame size={22} />;
      case "ai_coach":
        return <Sparkles size={22} />;
      case "progress":
        return <TrendingUp size={22} />;
      default:
        return <Layers size={22} />;
    }
  };

  const getFeatureMetrics = (feature: DashboardFeature): string[] => {
    switch (feature.key) {
      case "assessment":
        return [
          dashboardStatusLabel(dashboard.assessment.status, locale),
          `${dashboard.assessment.completionPercentage}% ${copy.completion.toLowerCase()}`,
        ];
      case "workout":
        return dashboard.workout
          ? [
              dashboard.workout.title,
              dashboard.workout.focus,
              `${dashboard.workout.completionPercentage}% complete`,
            ]
          : [];
      case "nutrition":
        return dashboard.nutrition
          ? [
              `${dashboard.nutrition.caloriesRemaining} kcal remaining`,
              `${dashboard.nutrition.mealsCompleted}/${dashboard.nutrition.totalMeals} meals completed`,
              `${dashboard.nutrition.waterConsumedMl}/${dashboard.nutrition.waterTargetMl} ml water`,
            ]
          : [];
      case "progress":
        return [
          `${dashboard.progress.assessmentCompletion}% ${copy.completion.toLowerCase()}`,
          `${dashboard.progress.profileCompleteness}% ${copy.profile.toLowerCase()}`,
        ];
      default:
        return [];
    }
  };

  const getStatusIcon = (status: DashboardFeature["status"]) => {
    if (status === "available") return <CheckCircle2 size={15} aria-hidden="true" />;
    if (status === "locked") return <LockKeyhole size={15} aria-hidden="true" />;
    return <CircleAlert size={15} aria-hidden="true" />;
  };

  return (
    <section
      className="dashboard-modules"
      aria-labelledby="dashboard-modules-title"
      style={{ marginTop: "32px" }}
    >
      <div className="dashboard-section-heading" style={{ marginBottom: "24px" }}>
        <div>
          <h2 id="dashboard-modules-title" style={{ fontSize: "24px", fontWeight: 800, margin: 0 }}>
            {copy.modules}
          </h2>
          <p style={{ fontSize: "16px", color: "var(--color-text-secondary)", marginTop: "8px" }}>
            {copy.modulesBody}
          </p>
        </div>
      </div>
      <div className="dashboard-feature-grid">
        {features.map((feature, idx) => (
          <motion.div
            key={feature.key}
            className={feature.key === "assessment" ? "dashboard-feature-primary" : undefined}
            initial={{ opacity: 0, y: 15 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: idx * 0.08 }}
            whileHover={{ y: -4 }}
          >
            <Card
              className={`dashboard-feature-card feature-${feature.status} ${feature.key === "assessment" ? "is-primary" : ""}`}
            >
              <div>
                <div className="dashboard-feature-heading">
                  <div className="dashboard-feature-icon">{getFeatureIcon(feature.key)}</div>
                  <Badge
                    className={`dashboard-feature-status status-${feature.status}`}
                    aria-label={`Status: ${featureStatusLabel(feature.status, locale)}`}
                  >
                    {getStatusIcon(feature.status)}
                    {featureStatusLabel(feature.status, locale)}
                  </Badge>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.reason}</p>
                {getFeatureMetrics(feature).length ? (
                  <ul className="dashboard-feature-metrics" aria-label={`${feature.title} details`}>
                    {getFeatureMetrics(feature).map((metric) => (
                      <li key={metric}>{metric}</li>
                    ))}
                  </ul>
                ) : null}
              </div>
              {feature.destinationRoute ? (
                <Link
                  to={feature.destinationRoute}
                  aria-label={`${copy.open}: ${feature.title}`}
                  className="dashboard-feature-action"
                >
                  {copy.open} <ArrowRight size={16} />
                </Link>
              ) : (
                <span className="dashboard-unavailable" role="status">
                  {copy.notAvailable}
                </span>
              )}
            </Card>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

function formatDate(value: string | null, locale: Locale, fallback: string): string {
  if (!value) return fallback;
  return new Intl.DateTimeFormat(locale === "ar" ? "ar" : "en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function ProgressSnapshotCard({
  progress,
  user,
  locale,
}: {
  progress: DashboardProgressSnapshot;
  user: DashboardUserSummary;
  locale: Locale;
}) {
  const copy = dashboardCopy[locale];
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      <Card
        className="dashboard-progress-card"
        id="profile-summary"
        style={{ padding: "32px", borderRadius: "28px" }}
      >
        <div
          className="dashboard-section-heading"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: "20px",
          }}
        >
          <h2 style={{ fontSize: "20px", fontWeight: 700, margin: 0 }}>{copy.progress}</h2>
          <span style={{ fontSize: "12px", color: "var(--color-text-secondary)" }}>
            {copy.defaultUnits}:{" "}
            <strong style={{ textTransform: "uppercase" }}>{user.preferredUnits}</strong>
          </span>
        </div>
        <div className="dashboard-progress-list" style={{ display: "grid", gap: "20px" }}>
          <div>
            <LinearProgress value={progress.assessmentCompletion} label={copy.completion} />
          </div>
          <div>
            <LinearProgress value={progress.profileCompleteness} label={copy.profile} />
          </div>
          <div
            className="dashboard-last-activity"
            style={{
              display: "flex",
              justifyContent: "space-between",
              borderTop: "1px solid var(--color-border)",
              paddingTop: "16px",
              fontSize: "14px",
            }}
          >
            <span style={{ color: "var(--color-text-secondary)" }}>{copy.lastActivity}</span>
            <strong style={{ color: "var(--color-text-primary)", fontWeight: 700 }}>
              {formatDate(progress.lastActivityDate, locale, copy.noActivity)}
            </strong>
          </div>
        </div>
        {user.missingProfileFields.length ? (
          <div
            className="dashboard-profile-missing"
            role="status"
            style={{
              marginTop: "20px",
              padding: "16px",
              borderRadius: "16px",
              background: "rgba(245, 158, 11, 0.05)",
              border: "1px solid rgba(245, 158, 11, 0.15)",
              fontSize: "14px",
              color: "var(--color-warning)",
            }}
          >
            <strong style={{ display: "block", marginBottom: "4px" }}>{copy.profileMissing}</strong>
            <span style={{ color: "var(--color-text-secondary)" }}>
              {user.missingProfileFields.join(", ")}
            </span>
          </div>
        ) : null}
      </Card>
    </motion.div>
  );
}

export function QuickActions({
  actions,
  locale,
  onLogout,
}: {
  actions: DashboardAction[];
  locale: Locale;
  onLogout: () => void;
}) {
  const copy = dashboardCopy[locale];
  return (
    <section
      className="dashboard-quick-actions"
      aria-labelledby="dashboard-quick-title"
      style={{ marginTop: "32px", borderTop: "1px solid var(--color-border)", paddingTop: "24px" }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "20px",
        }}
      >
        <h2 id="dashboard-quick-title" style={{ fontSize: "20px", fontWeight: 800, margin: 0 }}>
          {copy.quickActions}
        </h2>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "12px" }}>
          {actions.map((action) =>
            action.actionType === "log_out" ? (
              <Button
                variant="ghost"
                key={action.actionType}
                onClick={onLogout}
                style={{
                  borderRadius: "18px",
                  minHeight: "48px",
                  display: "flex",
                  alignItems: "center",
                  gap: "6px",
                }}
              >
                <HelpCircle size={18} />
                <span>{actionLabel(action.actionType, locale)}</span>
              </Button>
            ) : action.destinationRoute ? (
              <Link
                className="ds-button ds-button-outline ds-button-md"
                key={`${action.actionType}-${action.destinationRoute}`}
                to={action.destinationRoute}
                style={{ borderRadius: "18px", height: "48px", minHeight: "48px", fontWeight: 700 }}
              >
                {actionLabel(action.actionType, locale)}
              </Link>
            ) : null,
          )}
        </div>
      </div>
    </section>
  );
}
