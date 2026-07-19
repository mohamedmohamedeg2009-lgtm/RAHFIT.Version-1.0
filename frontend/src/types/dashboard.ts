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
  nutrition: {
    planId: string;
    targetCalories: number;
    caloriesConsumed: number;
    caloriesRemaining: number;
    waterTargetMl: number;
    waterConsumedMl: number;
    mealsCompleted: number;
    totalMeals: number;
    destinationRoute: string;
  } | null;
  dailyPriority: DashboardAction;
  features: DashboardFeature[];
  safetyNotice: DashboardSafetyNotice | null;
  progress: DashboardProgressSnapshot;
  quickActions: DashboardAction[];
  metadata: DashboardMetadata;
}

export interface DashboardActivity {
  id: string;
  occurredAt: string;
  kind: string;
  title: string;
  detail: string | null;
  status: string;
}

export interface DashboardHistoryPoint {
  date: string;
  caloriesConsumed: number | null;
  workoutsCompleted: number | null;
  activeMinutes: number | null;
  readinessScore: number | null;
}

export interface DashboardSummaryData {
  user: DashboardUserSummary;
  assessment: DashboardAssessmentSummary;
  latestCheckIn: {
    hasCheckedInToday: boolean;
    date: string | null;
    readinessScore: number | null;
    readinessLevel: string | null;
    recommendedAction: string | null;
    warningCodes: string[];
  } | null;
  nutrition: {
    date: string;
    caloriesConsumed: number | null;
    proteinConsumed: number | null;
    waterConsumedMl: number | null;
    targetCalories: number | null;
    waterTargetMl: number | null;
  } | null;
  workout: {
    sessionId: string;
    status: string;
    completionPercentage: number | null;
    startedAt: string;
    completedAt: string | null;
  } | null;
  recentActivities: DashboardActivity[];
  history: DashboardHistoryPoint[];
  metadata: DashboardMetadata;
}
