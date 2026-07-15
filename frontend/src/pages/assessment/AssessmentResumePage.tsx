import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Button, Card, FullPageLoader, LinearProgress } from "../../components/ui";
import { SafetyStatusCard } from "../../components/assessment/SafetyStatusCard";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useLocale } from "../../contexts/LocaleContext";
import { assessmentCopy } from "../../i18n/assessment";

export default function AssessmentResumePage() {
  const { sessionId = "" } = useParams();
  const navigate = useNavigate();
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { session, resume, isLoading, error } = useAssessment();

  useEffect(() => {
    if (!sessionId || session?.id === sessionId) return;
    void resume(sessionId).catch(() => undefined);
  }, [resume, session?.id, sessionId]);

  if (isLoading && !session) return <FullPageLoader label={copy.loading} />;
  if (error || !session) {
    return (
      <main className="assessment-main assessment-centered-page">
        <Card className="assessment-message-card" role="alert">
          <h1>{copy.loadError}</h1>
          <Button onClick={() => void resume(sessionId)}>{copy.retry}</Button>
        </Card>
      </main>
    );
  }

  return (
    <main className="assessment-main assessment-centered-page">
      <Card className="assessment-resume-card">
        <span className="assessment-resume-mark" aria-hidden="true">
          ↻
        </span>
        <span className="assessment-eyebrow">{copy.startOverNotice}</span>
        <h1>{copy.resumeTitle}</h1>
        <p>{copy.resumeBody}</p>
        <LinearProgress value={session.progress.assessmentCompleteness} label={copy.completion} />
        <div className="assessment-resume-stats">
          <span>
            {copy.completion}
            <strong>{session.progress.assessmentCompleteness}%</strong>
          </span>
          <span>
            {copy.readiness}
            <strong>{session.progress.readinessScore}/100</strong>
          </span>
        </div>
        <SafetyStatusCard safety={session.progress.safety} />
        <Button size="lg" onClick={() => navigate(`/assessment/session/${session.id}`)}>
          {copy.continueAssessment}
          <span aria-hidden="true">→</span>
        </Button>
      </Card>
    </main>
  );
}
