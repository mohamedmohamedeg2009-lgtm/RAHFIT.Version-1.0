import { ApiError } from "./apiClient";

export interface WorkoutClientError {
  code: string;
  title: string;
  message: string;
  actionLabel?: string;
  actionPath?: string;
  retryable: boolean;
}

const known: Record<string, Omit<WorkoutClientError, "code">> = {
  workout_profile_incomplete: {
    title: "Complete your profile",
    message: "Your training profile is required before a plan can be generated.",
    actionLabel: "Complete profile",
    actionPath: "/intelligent-workouts/setup/profile",
    retryable: false,
  },
  workout_health_profile_incomplete: {
    title: "Health declaration required",
    message: "Confirm your health history before generating a safe plan.",
    actionLabel: "Review health declaration",
    actionPath: "/intelligent-workouts/setup/health",
    retryable: false,
  },
  workout_readiness_blocked: {
    title: "Training is paused",
    message:
      "Your readiness result does not currently allow plan generation. Follow the professional guidance provided by RAHFIT AI.",
    retryable: false,
  },
  workout_medical_clearance_required: {
    title: "Medical clearance required",
    message: "Please obtain professional medical clearance before continuing with training.",
    retryable: false,
  },
  workout_plan_not_found: {
    title: "Plan unavailable",
    message: "This plan does not exist or is not available to your account.",
    actionLabel: "View workouts",
    actionPath: "/intelligent-workouts",
    retryable: false,
  },
  workout_session_not_found: {
    title: "Session unavailable",
    message: "This session does not exist or is not available to your account.",
    actionLabel: "View session history",
    actionPath: "/intelligent-workouts/history/sessions",
    retryable: false,
  },
  workout_plan_archived: {
    title: "Plan is archived",
    message: "Archived plans cannot accept new workout sessions. Activate an eligible plan first.",
    actionLabel: "View plan history",
    actionPath: "/intelligent-workouts/history/plans",
    retryable: false,
  },
  workout_session_state_invalid: {
    title: "Session already closed",
    message: "Completed or abandoned sessions cannot be changed. Refresh to view the latest state.",
    retryable: false,
  },
  workout_active_plan_conflict: {
    title: "Active plan changed",
    message: "Another plan is already active. Refresh your workout state before continuing.",
    retryable: true,
  },
  workout_exercise_unavailable: {
    title: "Exercise unavailable",
    message:
      "One or more submitted exercises are not part of this plan day. Refresh and try again.",
    retryable: true,
  },
  workout_validation_failed: {
    title: "Check your workout details",
    message: "Some workout values were rejected. Review the highlighted entries and try again.",
    retryable: false,
  },
  validation_error: {
    title: "Check your entries",
    message: "Some values are missing or outside their allowed range.",
    retryable: false,
  },
  workout_generation_failed: {
    title: "Plan generation unavailable",
    message: "A safe plan could not be generated right now. Try again later.",
    retryable: true,
  },
  workout_persistence_failed: {
    title: "Workout not saved",
    message: "The server could not confirm the save. Refresh before trying again.",
    retryable: true,
  },
};

export function mapWorkoutError(cause: unknown): WorkoutClientError {
  if (cause instanceof ApiError) {
    const item = known[cause.code];
    if (item) return { code: cause.code, ...item };
    if (cause.status === 401)
      return {
        code: cause.code,
        title: "Session expired",
        message: "Sign in again to continue.",
        actionLabel: "Sign in",
        actionPath: "/login",
        retryable: false,
      };
    if (cause.status >= 500)
      return {
        code: cause.code,
        title: "Workout service unavailable",
        message:
          "We could not complete this request. Your existing workout data has not been changed.",
        retryable: true,
      };
    return {
      code: cause.code,
      title: "Request unavailable",
      message: cause.message,
      retryable: false,
    };
  }
  return {
    code: "network_error",
    title: "Connection problem",
    message: "Check your internet connection and try again.",
    retryable: true,
  };
}
