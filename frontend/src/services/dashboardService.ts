import { apiRequest } from "./apiClient";
import type {
  DashboardAction,
  DashboardAssessmentSummary,
  DashboardData,
  DashboardFeature,
  DashboardMetadata,
  DashboardSafetyNotice,
  DashboardUserSummary,
  DashboardSummaryData,
} from "../types/dashboard";

type RawAction = {
  action_type: DashboardAction["actionType"];
  title: string;
  description: string;
  destination_route: string | null;
  priority_reason: string;
  severity: DashboardAction["severity"];
};

type RawUser = {
  display_name: string;
  primary_goal: string | null;
  preferred_units: string;
  assessment_status: DashboardUserSummary["assessmentStatus"];
  profile_completeness: number;
  missing_profile_fields: string[];
};

type RawAssessment = {
  status: DashboardAssessmentSummary["status"];
  session_id: string | null;
  completion_percentage: number;
  readiness_score: number | null;
  risk_level: DashboardAssessmentSummary["riskLevel"];
  safety_status: DashboardAssessmentSummary["safetyStatus"];
  missing_categories: DashboardAssessmentSummary["missingCategories"];
  latest_completion_date: string | null;
  reassessment_recommended: boolean;
};

type RawFeature = {
  key: string;
  title: string;
  status: DashboardFeature["status"];
  reason: string;
  destination_route: string | null;
};

type RawSafetyNotice = {
  status: DashboardSafetyNotice["status"];
  title: string;
  message: string;
  severity: DashboardSafetyNotice["severity"];
  plan_generation_blocked: boolean;
};

type RawProgress = {
  assessment_completion: number;
  profile_completeness: number;
  latest_readiness_score: number | null;
  last_activity_date: string | null;
};

type RawMetadata = {
  generated_at: string;
  data_freshness: DashboardMetadata["dataFreshness"];
  partial_data: boolean;
  dashboard_version: string;
};

interface RawDashboard {
  user: RawUser;
  assessment: RawAssessment;
  workout: {
    plan_id: string;
    day_id: string;
    title: string;
    focus: string;
    status: string;
    completion_percentage: number;
    destination_route: string;
    last_activity_at: string | null;
  } | null;
  nutrition: {
    plan_id: string;
    target_calories: number;
    calories_consumed: number;
    calories_remaining: number;
    water_target_ml: number;
    water_consumed_ml: number;
    meals_completed: number;
    total_meals: number;
    destination_route: string;
  } | null;
  daily_priority: RawAction;
  features: RawFeature[];
  safety_notice: RawSafetyNotice | null;
  progress: RawProgress;
  quick_actions: RawAction[];
  metadata: RawMetadata;
}

function action(raw: RawAction): DashboardAction {
  return {
    actionType: raw.action_type,
    title: raw.title,
    description: raw.description,
    destinationRoute: raw.destination_route,
    priorityReason: raw.priority_reason,
    severity: raw.severity,
  };
}

function mapDashboard(raw: RawDashboard): DashboardData {
  return {
    user: {
      displayName: raw.user.display_name,
      primaryGoal: raw.user.primary_goal,
      preferredUnits: raw.user.preferred_units,
      assessmentStatus: raw.user.assessment_status,
      profileCompleteness: raw.user.profile_completeness,
      missingProfileFields: raw.user.missing_profile_fields,
    },
    assessment: {
      status: raw.assessment.status,
      sessionId: raw.assessment.session_id,
      completionPercentage: raw.assessment.completion_percentage,
      readinessScore: raw.assessment.readiness_score,
      riskLevel: raw.assessment.risk_level,
      safetyStatus: raw.assessment.safety_status,
      missingCategories: raw.assessment.missing_categories,
      latestCompletionDate: raw.assessment.latest_completion_date,
      reassessmentRecommended: raw.assessment.reassessment_recommended,
    },
    workout: raw.workout
      ? {
          planId: raw.workout.plan_id,
          dayId: raw.workout.day_id,
          title: raw.workout.title,
          focus: raw.workout.focus,
          status: raw.workout.status,
          completionPercentage: raw.workout.completion_percentage,
          destinationRoute: raw.workout.destination_route,
          lastActivityAt: raw.workout.last_activity_at,
        }
      : null,
    nutrition: raw.nutrition
      ? {
          planId: raw.nutrition.plan_id,
          targetCalories: raw.nutrition.target_calories,
          caloriesConsumed: raw.nutrition.calories_consumed,
          caloriesRemaining: raw.nutrition.calories_remaining,
          waterTargetMl: raw.nutrition.water_target_ml,
          waterConsumedMl: raw.nutrition.water_consumed_ml,
          mealsCompleted: raw.nutrition.meals_completed,
          totalMeals: raw.nutrition.total_meals,
          destinationRoute: raw.nutrition.destination_route,
        }
      : null,
    dailyPriority: action(raw.daily_priority),
    features: raw.features.map((feature) => ({
      key: feature.key,
      title: feature.title,
      status: feature.status,
      reason: feature.reason,
      destinationRoute: feature.destination_route,
    })),
    safetyNotice: raw.safety_notice
      ? {
          status: raw.safety_notice.status,
          title: raw.safety_notice.title,
          message: raw.safety_notice.message,
          severity: raw.safety_notice.severity,
          planGenerationBlocked: raw.safety_notice.plan_generation_blocked,
        }
      : null,
    progress: {
      assessmentCompletion: raw.progress.assessment_completion,
      profileCompleteness: raw.progress.profile_completeness,
      latestReadinessScore: raw.progress.latest_readiness_score,
      lastActivityDate: raw.progress.last_activity_date,
    },
    quickActions: raw.quick_actions.map(action),
    metadata: {
      generatedAt: raw.metadata.generated_at,
      dataFreshness: raw.metadata.data_freshness,
      partialData: raw.metadata.partial_data,
      dashboardVersion: raw.metadata.dashboard_version,
    },
  };
}

export const dashboardService = {
  async getDashboard(options?: Parameters<typeof apiRequest>[1]): Promise<DashboardData> {
    return mapDashboard(await apiRequest<RawDashboard>("/dashboard", options));
  },
  async getSummary(options?: Parameters<typeof apiRequest>[1]): Promise<DashboardSummaryData> {
    const raw = await apiRequest<{
      user: RawUser;
      assessment: RawAssessment;
      latest_check_in: {
        has_checked_in_today: boolean;
        date: string | null;
        readiness_score: number | null;
        readiness_level: string | null;
        recommended_action: string | null;
        warning_codes: string[];
      } | null;
      nutrition: {
        date: string;
        calories_consumed: number | null;
        protein_consumed: number | null;
        water_consumed_ml: number | null;
        target_calories: number | null;
        water_target_ml: number | null;
      } | null;
      workout: {
        session_id: string;
        status: string;
        completion_percentage: number | null;
        started_at: string;
        completed_at: string | null;
      } | null;
      recent_activities: {
        id: string;
        occurred_at: string;
        kind: string;
        title: string;
        detail: string | null;
        status: string;
      }[];
      history: {
        date: string;
        calories_consumed: number | null;
        workouts_completed: number | null;
        active_minutes: number | null;
        readiness_score: number | null;
      }[];
      metadata: RawMetadata;
    }>("/dashboard/summary", options);
    return {
      user: {
        displayName: raw.user.display_name,
        primaryGoal: raw.user.primary_goal,
        preferredUnits: raw.user.preferred_units,
        assessmentStatus: raw.user.assessment_status,
        profileCompleteness: raw.user.profile_completeness,
        missingProfileFields: raw.user.missing_profile_fields,
      },
      assessment: {
        status: raw.assessment.status,
        sessionId: raw.assessment.session_id,
        completionPercentage: raw.assessment.completion_percentage,
        readinessScore: raw.assessment.readiness_score,
        riskLevel: raw.assessment.risk_level,
        safetyStatus: raw.assessment.safety_status,
        missingCategories: raw.assessment.missing_categories,
        latestCompletionDate: raw.assessment.latest_completion_date,
        reassessmentRecommended: raw.assessment.reassessment_recommended,
      },
      latestCheckIn: raw.latest_check_in && {
        hasCheckedInToday: raw.latest_check_in.has_checked_in_today,
        date: raw.latest_check_in.date,
        readinessScore: raw.latest_check_in.readiness_score,
        readinessLevel: raw.latest_check_in.readiness_level,
        recommendedAction: raw.latest_check_in.recommended_action,
        warningCodes: raw.latest_check_in.warning_codes,
      },
      nutrition: raw.nutrition && {
        date: raw.nutrition.date,
        caloriesConsumed: raw.nutrition.calories_consumed,
        proteinConsumed: raw.nutrition.protein_consumed,
        waterConsumedMl: raw.nutrition.water_consumed_ml,
        targetCalories: raw.nutrition.target_calories,
        waterTargetMl: raw.nutrition.water_target_ml,
      },
      workout: raw.workout && {
        sessionId: raw.workout.session_id,
        status: raw.workout.status,
        completionPercentage: raw.workout.completion_percentage,
        startedAt: raw.workout.started_at,
        completedAt: raw.workout.completed_at,
      },
      recentActivities: raw.recent_activities.map((item) => ({
        id: item.id,
        occurredAt: item.occurred_at,
        kind: item.kind,
        title: item.title,
        detail: item.detail,
        status: item.status,
      })),
      history: raw.history.map((item) => ({
        date: item.date,
        caloriesConsumed: item.calories_consumed,
        workoutsCompleted: item.workouts_completed,
        activeMinutes: item.active_minutes,
        readinessScore: item.readiness_score,
      })),
      metadata: {
        generatedAt: raw.metadata.generated_at,
        dataFreshness: raw.metadata.data_freshness,
        partialData: raw.metadata.partial_data,
        dashboardVersion: raw.metadata.dashboard_version,
      },
    };
  },
};
