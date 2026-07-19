import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { Badge, Button, Card, FullPageLoader, MetricCard } from "../../components/ui";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useLocale } from "../../contexts/LocaleContext";
import {
  assessmentCopy,
  categoryLabel,
  localizeSummaryText,
  riskLabel,
} from "../../i18n/assessment";

export default function AssessmentCompletedPage() {
  const navigate = useNavigate();
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { result, loadLatest, isLoading, error } = useAssessment();

  useEffect(() => {
    if (result) return;
    void loadLatest().catch(() => undefined);
  }, [loadLatest, result]);

  if (isLoading && !result) return <FullPageLoader label={copy.loading} />;
  if (!result) {
    return (
      <main className="assessment-main assessment-centered-page">
        <Card className="assessment-message-card" role="alert">
          <h1>{error?.message ?? copy.loadError}</h1>
          <Button onClick={() => void loadLatest()}>{copy.retry}</Button>
        </Card>
      </main>
    );
  }

  const sections = [
    [copy.goals, result.summary.goals],
    [copy.lifestyle, result.summary.lifestyle],
    [copy.medical, result.summary.medicalConsiderations],
    [copy.equipment, result.summary.equipment],
  ] as const;

  return (
    <main className="assessment-main assessment-completed-main">
      <section className="assessment-success-hero" aria-labelledby="assessment-complete-title">
        <div className="assessment-success-mark" aria-hidden="true">
          <span>✓</span>
        </div>
        <span className="assessment-eyebrow">{copy.completedEyebrow}</span>
        <h1 id="assessment-complete-title">{copy.completedTitle}</h1>
        <p>{copy.completedBody}</p>
        <div className="assessment-success-metrics">
          <MetricCard>
            <span>{copy.completion}</span>
            <strong>{result.assessmentCompleteness}%</strong>
          </MetricCard>
          <MetricCard>
            <span>{copy.readiness}</span>
            <strong>{result.readinessScore}</strong>
            <small>/ 100</small>
          </MetricCard>
          <MetricCard>
            <span>{copy.risk}</span>
            <strong>{riskLabel(result.riskLevel, locale)}</strong>
          </MetricCard>
        </div>
      </section>

      <Card className="assessment-result-summary">
        <div className="assessment-section-heading">
          <div>
            <h2>{copy.summary}</h2>
          </div>
          <Badge>{localizeSummaryText(result.summary.trainingReadiness, locale)}</Badge>
        </div>
        <div className="assessment-summary-grid">
          {sections.map(([title, items]) => (
            <section key={title}>
              <h3>{title}</h3>
              {items.length ? (
                <ul>
                  {items.map((item) => (
                    <li key={item}>{localizeSummaryText(item, locale)}</li>
                  ))}
                </ul>
              ) : (
                <p>{copy.notAnswered}</p>
              )}
            </section>
          ))}
          <section>
            <h3>{copy.experience}</h3>
            <p>
              {result.summary.experience
                ? localizeSummaryText(result.summary.experience, locale)
                : copy.notAnswered}
            </p>
          </section>
          <section>
            <h3>{copy.missingCategories}</h3>
            <div className="assessment-category-list">
              {result.missingCategories.length
                ? result.missingCategories.map((category) => (
                    <Badge key={category}>{categoryLabel(category, locale)}</Badge>
                  ))
                : copy.noMissingCategories}
            </div>
          </section>
        </div>
      </Card>

      <Button size="lg" onClick={() => navigate("/app")}>
        {copy.continueDashboard}
        <span aria-hidden="true">→</span>
      </Button>
    </main>
  );
}
