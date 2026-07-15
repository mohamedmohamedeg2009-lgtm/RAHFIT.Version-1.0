export type AssessmentQuestionType =
  | "text"
  | "textarea"
  | "number"
  | "integer"
  | "boolean"
  | "single_choice"
  | "multiple_choice"
  | "date"
  | "height"
  | "weight"
  | "time"
  | "slider";

export type AssessmentCategory =
  | "personal_information"
  | "goals"
  | "lifestyle"
  | "medical"
  | "injuries"
  | "sleep"
  | "stress"
  | "experience"
  | "equipment"
  | "nutrition"
  | "recovery"
  | "sports"
  | "football"
  | "goalkeeper";

export type AnswerValue = string | number | boolean | string[];
export type SafetyStatus = "safe" | "caution" | "stop";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface QuestionOption {
  value: string;
  label: string;
}

export interface AssessmentQuestion {
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
  displayOrder: number;
  version: number;
}

export interface AssessmentAnswer {
  questionId: string;
  value: AnswerValue;
  answeredAt: string;
}

export interface SafetyEvaluation {
  status: SafetyStatus;
  riskLevel: RiskLevel;
  explanations: string[];
  triggeredRuleIds: string[];
}

export interface AssessmentProgress {
  assessmentCompleteness: number;
  readinessScore: number;
  missingCategories: AssessmentCategory[];
  safety: SafetyEvaluation;
}

export interface AssessmentSession {
  id: string;
  assessmentVersion: number;
  status: "in_progress" | "completed";
  answers: AssessmentAnswer[];
  revision: number;
  startedAt: string;
  lastActivityAt: string;
  completedAt: string | null;
  resultId: string | null;
  progress: AssessmentProgress;
  nextQuestion: AssessmentQuestion | null;
}

export interface AssessmentSummary {
  goals: string[];
  lifestyle: string[];
  medicalConsiderations: string[];
  trainingReadiness: string;
  equipment: string[];
  experience: string | null;
}

export interface AssessmentResult {
  id: string;
  sessionId: string;
  assessmentVersion: number;
  profile: Record<string, Record<string, AnswerValue>>;
  answeredQuestionIds: string[];
  completedCategories: AssessmentCategory[];
  completionPercentage: number;
  assessmentCompleteness: number;
  readinessScore: number;
  missingCategories: AssessmentCategory[];
  safetyStatus: SafetyStatus;
  riskLevel: RiskLevel;
  safetyExplanations: string[];
  summary: AssessmentSummary;
  generatedAt: string;
}
