import type { AssessmentCategory, RiskLevel, SafetyStatus } from "./assessment";

export type DashboardAssessmentStatus = "not_started" | "in_progress" | "completed" | "unavailable";
export type DashboardActionType =
  | "start_assessment"
  | "resume_assessment"
  | "review_safety_warning"
  | "complete_missing_profile_information"
  | "view_assessment_summary"
  | "continue_available_feature"
  | "generate_workout"
  | "start_workout"
  | "continue_workout"
  | "log_out";
export type DashboardSeverity = "info" | "success" | "warning" | "danger";
export type FeatureStatus = "available" | "locked" | "coming_soon" | "action_required";

export interface DashboardUserSummary {
  displayName: string;
  primaryGoal: string | null;
  preferredUnits: string;
  assessmentStatus: DashboardAssessmentStatus;
  profileCompleteness: number;
  missingProfileFields: string[];
}

export interface DashboardAssessmentSummary {
  status: DashboardAssessmentStatus;
  sessionId: string | null;
  completionPercentage: number;
  readinessScore: number | null;
  riskLevel: RiskLevel | null;
  safetyStatus: SafetyStatus | null;
  missingCategories: AssessmentCategory[];
  latestCompletionDate: string | null;
  reassessmentRecommended: boolean;
}

export interface DashboardAction {
  actionType: DashboardActionType;
  title: string;
  description: string;
  destinationRoute: string | null;
  priorityReason: string;
  severity: DashboardSeverity;
}

export interface DashboardFeature {
  key: string;
  title: string;
  status: FeatureStatus;
  reason: string;
  destinationRoute: string | null;
}

export interface DashboardSafetyNotice {
  status: SafetyStatus;
  title: string;
  message: string;
  severity: DashboardSeverity;
  planGenerationBlocked: boolean;
}

export interface DashboardProgressSnapshot {
  assessmentCompletion: number;
  profileCompleteness: number;
  latestReadinessScore: number | null;
  lastActivityDate: string | null;
}

export interface DashboardMetadata {
  generatedAt: string;
  dataFreshness: "live" | "partial";
  partialData: boolean;
  dashboardVersion: string;
}

export interface DashboardData {
  user: DashboardUserSummary;
  assessment: DashboardAssessmentSummary;
  workout: {
    planId: string;
    dayId: string;
    title: string;
    focus: string;
    status: string;
    completionPercentage: number;
    destinationRoute: string;
    lastActivityAt: string | null;
  } | null;
  dailyPriority: DashboardAction;
  features: DashboardFeature[];
  safetyNotice: DashboardSafetyNotice | null;
  progress: DashboardProgressSnapshot;
  quickActions: DashboardAction[];
  metadata: DashboardMetadata;
}
