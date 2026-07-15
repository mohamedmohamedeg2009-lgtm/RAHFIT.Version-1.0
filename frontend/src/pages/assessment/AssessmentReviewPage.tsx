import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { SafetyStatusCard } from "../../components/assessment/SafetyStatusCard";
import {
  Badge,
  Button,
  Card,
  FullPageLoader,
  LinearProgress,
  MetricCard,
} from "../../components/ui";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useLocale } from "../../contexts/LocaleContext";
import {
  answerLabel,
  assessmentCopy,
  categoryLabel,
  localizeQuestion,
  riskLabel,
} from "../../i18n/assessment";

export default function AssessmentReviewPage() {
  const { sessionId = "" } = useParams();
  const navigate = useNavigate();
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { session, questions, loadSession, finish, isLoading, isSaving, error } = useAssessment();

  useEffect(() => {
    if (!sessionId || session?.id === sessionId) return;
    void loadSession(sessionId).catch(() => undefined);
  }, [loadSession, session?.id, sessionId]);

  const complete = async () => {
    if (!session || session.progress.safety.status === "stop") return;
    try {
      await finish(session.id);
      navigate(`/assessment/completed/${session.id}`);
    } catch {
      // The context surfaces completion and safety failures.
    }
  };

  if (isLoading && !session) return <FullPageLoader label={copy.loading} />;
  if (!session) {
    return (
      <main className="assessment-main assessment-centered-page">
        <Card className="assessment-message-card" role="alert">
          <h1>{error?.message ?? copy.loadError}</h1>
          <Button onClick={() => void loadSession(sessionId)}>{copy.retry}</Button>
        </Card>
      </main>
    );
  }

  const lastAnsweredQuestionId = session.answers.at(-1)?.questionId;

  return (
    <main className="assessment-main assessment-review-main">
      <header className="assessment-page-heading">
        <span className="assessment-eyebrow">{copy.summary}</span>
        <h1>{copy.review}</h1>
        <p>{copy.reviewBody}</p>
      </header>

      <section className="assessment-review-overview" aria-label={copy.summary}>
        <Card className="assessment-completion-card">
          <LinearProgress value={session.progress.assessmentCompleteness} label={copy.completion} />
          <div className="assessment-review-metrics">
            <MetricCard>
              <span>{copy.readiness}</span>
              <strong>{session.progress.readinessScore}</strong>
              <small>/ 100</small>
            </MetricCard>
            <MetricCard>
              <span>{copy.risk}</span>
              <strong className={`risk-${session.progress.safety.riskLevel}`}>
                {riskLabel(session.progress.safety.riskLevel, locale)}
              </strong>
            </MetricCard>
          </div>
        </Card>
        <SafetyStatusCard safety={session.progress.safety} />
      </section>

      <section className="assessment-review-grid">
        <Card className="assessment-answers-card">
          <div className="assessment-section-heading">
            <div>
              <span>{session.answers.length}</span>
              <h2>{copy.answers}</h2>
            </div>
          </div>
          <dl className="assessment-answer-list">
            {session.answers.map((answer) => {
              const question = questions.find((item) => item.id === answer.questionId);
              if (!question) return null;
              const localized = localizeQuestion(question, locale);
              return (
                <div key={answer.questionId} className="assessment-answer-row">
                  <div>
                    <dt>{localized.title}</dt>
                    <dd>{answerLabel(localized, answer.value, locale)}</dd>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() =>
                      navigate(`/assessment/session/${session.id}/question/${answer.questionId}`)
                    }
                    aria-label={`${copy.edit}: ${localized.title}`}
                  >
                    {copy.edit}
                  </Button>
                </div>
              );
            })}
          </dl>
        </Card>

        <Card className="assessment-missing-card">
          <h2>{copy.missingCategories}</h2>
          {session.progress.missingCategories.length ? (
            <div className="assessment-category-list">
              {session.progress.missingCategories.map((category) => (
                <Badge key={category}>{categoryLabel(category, locale)}</Badge>
              ))}
            </div>
          ) : (
            <p>{copy.noMissingCategories}</p>
          )}
        </Card>
      </section>

      {error ? (
        <p className="assessment-inline-error" role="alert">
          {error.message}
        </p>
      ) : null}
      <footer className="assessment-review-actions">
        <Button
          variant="ghost"
          disabled={!lastAnsweredQuestionId}
          onClick={() =>
            lastAnsweredQuestionId &&
            navigate(`/assessment/session/${session.id}/question/${lastAnsweredQuestionId}`)
          }
        >
          <span aria-hidden="true">←</span>
          {copy.previous}
        </Button>
        <div>
          {session.progress.safety.status === "stop" ? <p>{copy.stopComplete}</p> : null}
          <Button
            size="lg"
            loading={isSaving}
            disabled={session.progress.safety.status === "stop" || Boolean(session.nextQuestion)}
            onClick={() => void complete()}
          >
            {copy.complete}
            <span aria-hidden="true">✓</span>
          </Button>
        </div>
      </footer>
    </main>
  );
}
