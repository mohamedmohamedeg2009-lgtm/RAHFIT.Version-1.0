import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";

import { ApiError } from "../services/apiClient";
import { assessmentService } from "../services/assessmentService";
import type {
  AnswerValue,
  AssessmentQuestion,
  AssessmentResult,
  AssessmentSession,
} from "../types/assessment";

export interface AssessmentErrorState {
  message: string;
  code: string;
  field?: string;
}

export interface AssessmentContextValue {
  questions: AssessmentQuestion[];
  session: AssessmentSession | null;
  result: AssessmentResult | null;
  isLoading: boolean;
  isSaving: boolean;
  error: AssessmentErrorState | null;
  start: () => Promise<AssessmentSession>;
  resume: (sessionId: string) => Promise<AssessmentSession>;
  loadSession: (sessionId: string) => Promise<AssessmentSession>;
  saveAnswer: (
    sessionId: string,
    questionId: string,
    value: AnswerValue,
  ) => Promise<AssessmentSession>;
  finish: (sessionId: string) => Promise<AssessmentResult>;
  loadLatest: () => Promise<AssessmentResult>;
  clearError: () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AssessmentContext = createContext<AssessmentContextValue | null>(null);

function toErrorState(error: unknown): AssessmentErrorState {
  if (error instanceof ApiError) {
    const firstDetail = error.details[0];
    return {
      message: error.message,
      code: error.code,
      field: typeof firstDetail?.field === "string" ? firstDetail.field : undefined,
    };
  }
  return {
    message: "The assessment service could not be reached. Please try again.",
    code: "network_error",
  };
}

export function AssessmentProvider({ children }: { children: ReactNode }) {
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [session, setSession] = useState<AssessmentSession | null>(null);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<AssessmentErrorState | null>(null);

  const loadQuestions = useCallback(async (version: number) => {
    const loaded = await assessmentService.getQuestions(version);
    setQuestions(loaded);
  }, []);

  const runSessionLoad = useCallback(
    async (action: () => Promise<AssessmentSession>) => {
      setIsLoading(true);
      setError(null);
      try {
        const loaded = await action();
        await loadQuestions(loaded.assessmentVersion);
        setSession(loaded);
        return loaded;
      } catch (cause) {
        setError(toErrorState(cause));
        throw cause;
      } finally {
        setIsLoading(false);
      }
    },
    [loadQuestions],
  );

  const start = useCallback(
    () => runSessionLoad(() => assessmentService.start()),
    [runSessionLoad],
  );
  const resume = useCallback(
    (sessionId: string) => runSessionLoad(() => assessmentService.resume(sessionId)),
    [runSessionLoad],
  );
  const loadSession = useCallback(
    (sessionId: string) => runSessionLoad(() => assessmentService.getSession(sessionId)),
    [runSessionLoad],
  );

  const saveAnswer = useCallback(
    async (sessionId: string, questionId: string, value: AnswerValue) => {
      setIsSaving(true);
      setError(null);
      try {
        const updated = await assessmentService.saveAnswer(sessionId, questionId, value);
        setSession(updated);
        return updated;
      } catch (cause) {
        setError(toErrorState(cause));
        throw cause;
      } finally {
        setIsSaving(false);
      }
    },
    [],
  );

  const finish = useCallback(async (sessionId: string) => {
    setIsSaving(true);
    setError(null);
    try {
      const completed = await assessmentService.finish(sessionId);
      setResult(completed);
      return completed;
    } catch (cause) {
      setError(toErrorState(cause));
      throw cause;
    } finally {
      setIsSaving(false);
    }
  }, []);

  const loadLatest = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const latest = await assessmentService.getLatest();
      setResult(latest);
      return latest;
    } catch (cause) {
      setError(toErrorState(cause));
      throw cause;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);
  const value = useMemo<AssessmentContextValue>(
    () => ({
      questions,
      session,
      result,
      isLoading,
      isSaving,
      error,
      start,
      resume,
      loadSession,
      saveAnswer,
      finish,
      loadLatest,
      clearError,
    }),
    [
      questions,
      session,
      result,
      isLoading,
      isSaving,
      error,
      start,
      resume,
      loadSession,
      saveAnswer,
      finish,
      loadLatest,
      clearError,
    ],
  );

  return <AssessmentContext.Provider value={value}>{children}</AssessmentContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAssessment(): AssessmentContextValue {
  const context = useContext(AssessmentContext);
  if (!context) throw new Error("useAssessment must be used within AssessmentProvider.");
  return context;
}
