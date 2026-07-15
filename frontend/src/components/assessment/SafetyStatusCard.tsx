import { useLocale } from "../../contexts/LocaleContext";
import {
  assessmentCopy,
  localizeSafetyExplanation,
  riskLabel,
  safetyTitle,
} from "../../i18n/assessment";
import type { SafetyEvaluation } from "../../types/assessment";

export function SafetyStatusCard({ safety }: { safety: SafetyEvaluation }) {
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];

  return (
    <aside
      className={`assessment-safety-card is-${safety.status}`}
      role={safety.status === "stop" ? "alert" : "status"}
      aria-live="polite"
    >
      <span className="assessment-safety-icon" aria-hidden="true">
        {safety.status === "safe" ? "✓" : safety.status === "caution" ? "!" : "×"}
      </span>
      <div>
        <div className="assessment-safety-heading">
          <strong>{safetyTitle(safety.status, locale)}</strong>
          <span>
            {copy.risk}: {riskLabel(safety.riskLevel, locale)}
          </span>
        </div>
        <ul>
          {safety.explanations.map((explanation) => (
            <li key={explanation}>{localizeSafetyExplanation(explanation, locale)}</li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
