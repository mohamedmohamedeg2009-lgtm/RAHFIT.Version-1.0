import { LinearProgress, MetricCard } from "../ui";
import { useLocale } from "../../contexts/LocaleContext";
import { assessmentCopy, categoryLabel } from "../../i18n/assessment";
import type { AssessmentCategory, AssessmentProgress } from "../../types/assessment";

interface AssessmentProgressHeaderProps {
  progress: AssessmentProgress;
  category: AssessmentCategory;
  currentStep: number;
  totalSteps: number;
}

export function AssessmentProgressHeader({
  progress,
  category,
  currentStep,
  totalSteps,
}: AssessmentProgressHeaderProps) {
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];

  return (
    <section className="assessment-progress-panel" aria-label={copy.completion}>
      <div className="assessment-progress-heading">
        <div>
          <span className="assessment-category-pill">{categoryLabel(category, locale)}</span>
          <p>
            {copy.step} {currentStep} {copy.of} {Math.max(totalSteps, currentStep)}
          </p>
        </div>
        <strong>{progress.assessmentCompleteness}%</strong>
      </div>
      <LinearProgress value={progress.assessmentCompleteness} label={copy.completion} />
      <div className="assessment-metrics-row">
        <MetricCard>
          <span>{copy.readiness}</span>
          <strong>{progress.readinessScore}</strong>
          <small>/ 100</small>
        </MetricCard>
        <div className="assessment-progress-note" aria-live="polite">
          <span className="assessment-pulse" aria-hidden="true" />
          {progress.assessmentCompleteness < 100 ? copy.saved : copy.review}
        </div>
      </div>
    </section>
  );
}
