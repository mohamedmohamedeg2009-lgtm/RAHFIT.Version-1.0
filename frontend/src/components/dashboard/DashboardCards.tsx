import { Link } from "react-router-dom";

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
    <Card className={`dashboard-priority-card priority-${priority.severity}`}>
      <div className="dashboard-priority-icon" aria-hidden="true">
        {priority.severity === "danger" ? "!" : "↗"}
      </div>
      <div className="dashboard-priority-copy">
        <span className="dashboard-eyebrow">{copy.todayPriority}</span>
        <h2>{priority.title}</h2>
        <p>{priority.description}</p>
        <details>
          <summary>{copy.whyThis}</summary>
          <p>{priority.priorityReason}</p>
        </details>
      </div>
      <div className="dashboard-priority-action">
        {isRefresh ? (
          <Button size="lg" onClick={onRefresh}>
            {actionLabel(priority.actionType, locale)}
          </Button>
        ) : priority.destinationRoute ? (
          <Link className="ds-button ds-button-primary ds-button-lg" to={priority.destinationRoute}>
            {actionLabel(priority.actionType, locale)}
            <span aria-hidden="true">→</span>
          </Link>
        ) : null}
      </div>
    </Card>
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
    <Card
      className={`dashboard-safety-notice notice-${notice.severity}`}
      role={notice.status === "stop" ? "alert" : "status"}
      aria-live={notice.status === "stop" ? "assertive" : "polite"}
    >
      <span className="dashboard-safety-mark" aria-hidden="true">
        !
      </span>
      <div>
        <div className="dashboard-safety-heading">
          <h2>{notice.title}</h2>
          {notice.planGenerationBlocked ? <Badge>{copy.safetyBlocked}</Badge> : null}
        </div>
        <p>{notice.message}</p>
      </div>
    </Card>
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
    <Card className="dashboard-assessment-card">
      <div className="dashboard-section-heading">
        <div>
          <span className="dashboard-eyebrow">{copy.assessment}</span>
          <h2>{dashboardStatusLabel(assessment.status, locale)}</h2>
        </div>
        <Badge className={`dashboard-status status-${assessment.status}`}>
          {dashboardStatusLabel(assessment.status, locale)}
        </Badge>
      </div>
      <LinearProgress value={assessment.completionPercentage} label={copy.completion} />
      <div className="dashboard-metric-grid">
        <MetricCard>
          <span>{copy.readiness}</span>
          <strong>{assessment.readinessScore ?? copy.notCalculated}</strong>
          {assessment.readinessScore !== null ? <small>/ 100</small> : null}
        </MetricCard>
        <MetricCard>
          <span>{copy.risk}</span>
          <strong>
            {assessment.riskLevel ? riskLabel(assessment.riskLevel, locale) : copy.notCalculated}
          </strong>
        </MetricCard>
      </div>
      <div className="dashboard-missing-categories">
        <h3>{copy.missing}</h3>
        {assessment.missingCategories.length ? (
          <div>
            {assessment.missingCategories.map((category) => (
              <Badge key={category}>{categoryLabel(category, locale)}</Badge>
            ))}
          </div>
        ) : (
          <p>{copy.noMissing}</p>
        )}
      </div>
      {assessment.reassessmentRecommended ? (
        <p className="dashboard-reassessment" role="status">
          {copy.reassessment}
        </p>
      ) : null}
    </Card>
  );
}

export function FeatureStatusGrid({
  features,
  locale,
}: {
  features: DashboardFeature[];
  locale: Locale;
}) {
  const copy = dashboardCopy[locale];
  return (
    <section className="dashboard-modules" aria-labelledby="dashboard-modules-title">
      <div className="dashboard-section-heading">
        <div>
          <h2 id="dashboard-modules-title">{copy.modules}</h2>
          <p>{copy.modulesBody}</p>
        </div>
      </div>
      <div className="dashboard-feature-grid">
        {features.map((feature) => (
          <Card className={`dashboard-feature-card feature-${feature.status}`} key={feature.key}>
            <div className="dashboard-feature-heading">
              <span className="dashboard-feature-icon" aria-hidden="true">
                {feature.key === "assessment"
                  ? "◎"
                  : feature.key === "workout"
                    ? "↗"
                    : feature.key === "nutrition"
                      ? "◇"
                      : feature.key === "ai_coach"
                        ? "✦"
                        : feature.key === "progress"
                          ? "⌁"
                          : "▤"}
              </span>
              <Badge>{featureStatusLabel(feature.status, locale)}</Badge>
            </div>
            <h3>{feature.title}</h3>
            <p>{feature.reason}</p>
            {feature.destinationRoute ? (
              <Link to={feature.destinationRoute} aria-label={`${copy.open}: ${feature.title}`}>
                {copy.open} <span aria-hidden="true">→</span>
              </Link>
            ) : (
              <span className="dashboard-unavailable">{copy.notAvailable}</span>
            )}
          </Card>
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
    <Card className="dashboard-progress-card" id="profile-summary">
      <div className="dashboard-section-heading">
        <h2>{copy.progress}</h2>
        <span>
          {copy.defaultUnits}: {user.preferredUnits}
        </span>
      </div>
      <div className="dashboard-progress-list">
        <div>
          <LinearProgress value={progress.assessmentCompletion} label={copy.completion} />
        </div>
        <div>
          <LinearProgress value={progress.profileCompleteness} label={copy.profile} />
        </div>
        <div className="dashboard-last-activity">
          <span>{copy.lastActivity}</span>
          <strong>{formatDate(progress.lastActivityDate, locale, copy.noActivity)}</strong>
        </div>
      </div>
      {user.missingProfileFields.length ? (
        <div className="dashboard-profile-missing" role="status">
          <strong>{copy.profileMissing}</strong>
          <span>{user.missingProfileFields.join(", ")}</span>
        </div>
      ) : null}
    </Card>
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
    <section className="dashboard-quick-actions" aria-labelledby="dashboard-quick-title">
      <h2 id="dashboard-quick-title">{copy.quickActions}</h2>
      <div>
        {actions.map((action) =>
          action.actionType === "log_out" ? (
            <Button variant="ghost" key={action.actionType} onClick={onLogout}>
              {actionLabel(action.actionType, locale)}
            </Button>
          ) : action.destinationRoute ? (
            <Link
              className="ds-button ds-button-outline ds-button-md"
              key={`${action.actionType}-${action.destinationRoute}`}
              to={action.destinationRoute}
            >
              {actionLabel(action.actionType, locale)}
            </Link>
          ) : null,
        )}
      </div>
    </section>
  );
}
