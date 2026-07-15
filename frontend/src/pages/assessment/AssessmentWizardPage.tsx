import { useEffect, useMemo, useRef, useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";

import { AssessmentProgressHeader } from "../../components/assessment/AssessmentProgressHeader";
import { AssessmentQuestionField } from "../../components/assessment/AssessmentQuestionField";
import { initialAnswer, isAnswerReady } from "../../components/assessment/questionUtils";
import { SafetyStatusCard } from "../../components/assessment/SafetyStatusCard";
import { Button, Card, FullPageLoader } from "../../components/ui";
import { useAssessment } from "../../contexts/AssessmentContext";
import { useLocale } from "../../contexts/LocaleContext";
import { assessmentCopy, localizeQuestion } from "../../i18n/assessment";
import type { AnswerValue, AssessmentQuestion } from "../../types/assessment";

interface QuestionStepProps {
  question: AssessmentQuestion;
  initialValue: AnswerValue | undefined;
  sessionId: string;
  previousQuestionId?: string;
  step: number;
  total: number;
}

function valueForSave(
  question: AssessmentQuestion,
  value: AnswerValue | undefined,
): AnswerValue | undefined {
  if (value !== undefined) return value;
  if (["text", "textarea", "date", "time"].includes(question.type)) return "";
  if (question.type === "multiple_choice") return [];
  return undefined;
}

function QuestionStep({
  question,
  initialValue,
  sessionId,
  previousQuestionId,
  step,
  total,
}: QuestionStepProps) {
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { session, saveAnswer, isSaving, error, clearError } = useAssessment();
  const navigate = useNavigate();
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [value, setValue] = useState<AnswerValue | undefined>(
    initialValue ?? initialAnswer(question),
  );
  const [localError, setLocalError] = useState<string | undefined>();

  useEffect(() => {
    headingRef.current?.focus();
  }, [question.id]);

  const ready = isAnswerReady(question, value) && valueForSave(question, value) !== undefined;
  const submit = async () => {
    if (!ready) {
      setLocalError(copy.answerRequired);
      return;
    }
    setLocalError(undefined);
    clearError();
    try {
      const updated = await saveAnswer(sessionId, question.id, valueForSave(question, value)!);
      if (updated.nextQuestion) {
        navigate(`/assessment/session/${sessionId}`, { replace: true });
      } else {
        navigate(`/assessment/session/${sessionId}/review`);
      }
    } catch {
      // The field renders the normalized backend error from context.
    }
  };

  const fieldError =
    error?.field === question.id || error?.code === "assessment_answer_invalid"
      ? error.message
      : localError;

  return (
    <main className="assessment-main assessment-wizard-main">
      {session ? (
        <AssessmentProgressHeader
          progress={session.progress}
          category={question.category}
          currentStep={step}
          totalSteps={total}
        />
      ) : null}
      <div className="assessment-wizard-grid">
        <Card className="assessment-question-card">
          <div className="assessment-question-meta">
            <span>{copy.category}</span>
            <span className={question.required ? "is-required" : ""}>
              {question.required ? copy.required : copy.optional}
            </span>
          </div>
          <h1 ref={headingRef} tabIndex={-1} className="assessment-question-heading">
            {question.title}
          </h1>
          <AssessmentQuestionField
            question={question}
            value={value}
            onChange={(next) => {
              setValue(next);
              setLocalError(undefined);
              clearError();
            }}
            error={fieldError}
            disabled={isSaving}
          />
          {error && !fieldError ? (
            <p className="assessment-inline-error" role="alert">
              {error.message}
            </p>
          ) : null}
          <div className="assessment-question-actions">
            <Button
              variant="ghost"
              type="button"
              disabled={!previousQuestionId || isSaving}
              onClick={() =>
                previousQuestionId &&
                navigate(`/assessment/session/${sessionId}/question/${previousQuestionId}`)
              }
            >
              <span aria-hidden="true">←</span>
              {copy.previous}
            </Button>
            <span className="assessment-save-status" role="status" aria-live="polite">
              {isSaving ? copy.saving : copy.saved}
            </span>
            <Button
              type="button"
              loading={isSaving}
              disabled={!ready}
              onClick={() => void submit()}
            >
              {question.required || value !== undefined ? copy.next : copy.skip}
              <span aria-hidden="true">→</span>
            </Button>
          </div>
        </Card>
        {session ? <SafetyStatusCard safety={session.progress.safety} /> : null}
      </div>
    </main>
  );
}

export default function AssessmentWizardPage() {
  const { sessionId = "", questionId } = useParams();
  const { locale } = useLocale();
  const copy = assessmentCopy[locale];
  const { session, questions, loadSession, isLoading, error } = useAssessment();

  useEffect(() => {
    if (!sessionId || session?.id === sessionId) return;
    void loadSession(sessionId).catch(() => undefined);
  }, [loadSession, session?.id, sessionId]);

  const activeQuestion = useMemo(() => {
    if (!session) return null;
    if (questionId) {
      const editable = session.answers.some((answer) => answer.questionId === questionId);
      return editable ? (questions.find((question) => question.id === questionId) ?? null) : null;
    }
    return session.nextQuestion;
  }, [questionId, questions, session]);

  if (isLoading && !session) return <FullPageLoader label={copy.loading} />;
  if (!session || !activeQuestion) {
    if (session && !session.nextQuestion && !questionId) {
      return <Navigate to={`/assessment/session/${session.id}/review`} replace />;
    }
    return (
      <main className="assessment-main assessment-centered-page">
        <Card className="assessment-message-card" role="alert">
          <h1>{error?.message ?? copy.loadError}</h1>
          <Button onClick={() => void loadSession(sessionId)}>{copy.retry}</Button>
        </Card>
      </main>
    );
  }

  const answerIndex = session.answers.findIndex(
    (answer) => answer.questionId === activeQuestion.id,
  );
  const previousQuestionId =
    answerIndex > 0
      ? session.answers[answerIndex - 1]?.questionId
      : answerIndex < 0
        ? session.answers.at(-1)?.questionId
        : undefined;
  const existing = session.answers.find((answer) => answer.questionId === activeQuestion.id)?.value;
  const step = answerIndex >= 0 ? answerIndex + 1 : session.answers.length + 1;
  const total = Math.max(session.answers.length + (session.nextQuestion ? 1 : 0), step);
  const localized = localizeQuestion(activeQuestion, locale);

  return (
    <QuestionStep
      key={`${localized.id}-${locale}-${session.revision}`}
      question={localized}
      initialValue={existing}
      sessionId={session.id}
      previousQuestionId={previousQuestionId}
      step={step}
      total={total}
    />
  );
}
