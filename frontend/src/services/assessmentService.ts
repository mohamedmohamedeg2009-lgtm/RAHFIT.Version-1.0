import { apiRequest } from "./apiClient";
import type {
  AnswerValue,
  AssessmentAnswer,
  AssessmentCategory,
  AssessmentProgress,
  AssessmentQuestion,
  AssessmentQuestionType,
  AssessmentResult,
  AssessmentSession,
  AssessmentSummary,
  QuestionOption,
  RiskLevel,
  SafetyStatus,
} from "../types/assessment";

interface ApiQuestion {
  id: string;
  category: AssessmentCategory;
  title: string;
  description: string | null;
  type: AssessmentQuestionType;
  required: boolean;
  placeholder: string | null;
  min: number | null;
  max: number | null;
  unit: string | null;
  options: QuestionOption[];
  display_order: number;
  version: number;
}

interface ApiAnswer {
  question_id: string;
  value: AnswerValue;
  answered_at: string;
}

interface ApiSafety {
  status: SafetyStatus;
  risk_level: RiskLevel;
  explanations: string[];
  triggered_rule_ids: string[];
}

interface ApiProgress {
  assessment_completeness: number;
  readiness_score: number;
  missing_categories: AssessmentCategory[];
  safety: ApiSafety;
}

interface ApiSession {
  id: string;
  assessment_version: number;
  status: "in_progress" | "completed";
  answers: ApiAnswer[];
  revision: number;
  started_at: string;
  last_activity_at: string;
  completed_at: string | null;
  result_id: string | null;
  progress: ApiProgress;
  next_question: ApiQuestion | null;
}

interface ApiSummary {
  goals: string[];
  lifestyle: string[];
  medical_considerations: string[];
  training_readiness: string;
  equipment: string[];
  experience: string | null;
}

interface ApiResult {
  id: string;
  session_id: string;
  assessment_version: number;
  profile: Record<string, Record<string, AnswerValue>>;
  answered_question_ids: string[];
  completed_categories: AssessmentCategory[];
  completion_percentage: number;
  assessment_completeness: number;
  readiness_score: number;
  missing_categories: AssessmentCategory[];
  safety_status: SafetyStatus;
  risk_level: RiskLevel;
  safety_explanations: string[];
  summary: ApiSummary;
  generated_at: string;
}

const mapQuestion = (question: ApiQuestion): AssessmentQuestion => ({
  id: question.id,
  category: question.category,
  title: question.title,
  description: question.description,
  type: question.type,
  required: question.required,
  placeholder: question.placeholder,
  min: question.min,
  max: question.max,
  unit: question.unit,
  options: question.options,
  displayOrder: question.display_order,
  version: question.version,
});

const mapAnswer = (answer: ApiAnswer): AssessmentAnswer => ({
  questionId: answer.question_id,
  value: answer.value,
  answeredAt: answer.answered_at,
});

const mapProgress = (progress: ApiProgress): AssessmentProgress => ({
  assessmentCompleteness: progress.assessment_completeness,
  readinessScore: progress.readiness_score,
  missingCategories: progress.missing_categories,
  safety: {
    status: progress.safety.status,
    riskLevel: progress.safety.risk_level,
    explanations: progress.safety.explanations,
    triggeredRuleIds: progress.safety.triggered_rule_ids,
  },
});

const mapSession = (session: ApiSession): AssessmentSession => ({
  id: session.id,
  assessmentVersion: session.assessment_version,
  status: session.status,
  answers: session.answers.map(mapAnswer),
  revision: session.revision,
  startedAt: session.started_at,
  lastActivityAt: session.last_activity_at,
  completedAt: session.completed_at,
  resultId: session.result_id,
  progress: mapProgress(session.progress),
  nextQuestion: session.next_question ? mapQuestion(session.next_question) : null,
});

const mapSummary = (summary: ApiSummary): AssessmentSummary => ({
  goals: summary.goals,
  lifestyle: summary.lifestyle,
  medicalConsiderations: summary.medical_considerations,
  trainingReadiness: summary.training_readiness,
  equipment: summary.equipment,
  experience: summary.experience,
});

const mapResult = (result: ApiResult): AssessmentResult => ({
  id: result.id,
  sessionId: result.session_id,
  assessmentVersion: result.assessment_version,
  profile: result.profile,
  answeredQuestionIds: result.answered_question_ids,
  completedCategories: result.completed_categories,
  completionPercentage: result.completion_percentage,
  assessmentCompleteness: result.assessment_completeness,
  readinessScore: result.readiness_score,
  missingCategories: result.missing_categories,
  safetyStatus: result.safety_status,
  riskLevel: result.risk_level,
  safetyExplanations: result.safety_explanations,
  summary: mapSummary(result.summary),
  generatedAt: result.generated_at,
});

export const assessmentService = {
  async getQuestions(version?: number) {
    const query = version ? `?version=${version}` : "";
    return (await apiRequest<ApiQuestion[]>(`/assessments/questions${query}`)).map(mapQuestion);
  },
  async start(version?: number) {
    return mapSession(
      await apiRequest<ApiSession>("/assessments/start", {
        method: "POST",
        body: version ? { version } : {},
      }),
    );
  },
  async saveAnswer(sessionId: string, questionId: string, value: AnswerValue) {
    const response = await apiRequest<{ session: ApiSession; next_question: ApiQuestion | null }>(
      `/assessments/${encodeURIComponent(sessionId)}/answer`,
      { method: "POST", body: { question_id: questionId, value } },
    );
    const session = mapSession(response.session);
    session.nextQuestion = response.next_question ? mapQuestion(response.next_question) : null;
    return session;
  },
  async finish(sessionId: string) {
    return mapResult(
      await apiRequest<ApiResult>(`/assessments/${encodeURIComponent(sessionId)}/finish`, {
        method: "POST",
      }),
    );
  },
  async getLatest() {
    return mapResult(await apiRequest<ApiResult>("/assessments/latest"));
  },
  async getSession(sessionId: string) {
    return mapSession(
      await apiRequest<ApiSession>(`/assessments/sessions/${encodeURIComponent(sessionId)}`),
    );
  },
  async resume(sessionId: string) {
    return mapSession(
      await apiRequest<ApiSession>(
        `/assessments/sessions/${encodeURIComponent(sessionId)}/resume`,
        { method: "POST" },
      ),
    );
  },
};
