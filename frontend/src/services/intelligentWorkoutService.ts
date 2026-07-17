import { apiRequest } from "./apiClient";
import type {
  CreateWorkoutSessionRequest,
  GenerateWorkoutPlanRequest,
  HealthProfileRequest,
  Page,
  UpdateWorkoutSessionRequest,
  UserProfileRequest,
  WorkoutAdaptationResponse,
  WorkoutPlanResponse,
  WorkoutSessionResponse,
} from "../types/intelligentWorkout";

const ROOT = "/intelligent-workouts";
const resource = (value: string) => encodeURIComponent(value);

export const intelligentWorkoutService = {
  generatePlan: (body: GenerateWorkoutPlanRequest) =>
    apiRequest<WorkoutPlanResponse>(`${ROOT}/plans/generate`, { method: "POST", body }),
  getActivePlan: () => apiRequest<WorkoutPlanResponse>(`${ROOT}/plans/active`),
  listPlans: (limit = 10, offset = 0) =>
    apiRequest<Page<WorkoutPlanResponse>>(`${ROOT}/plans?limit=${limit}&offset=${offset}`),
  getPlan: (planId: string) => apiRequest<WorkoutPlanResponse>(`${ROOT}/plans/${resource(planId)}`),
  activatePlan: (planId: string) =>
    apiRequest<WorkoutPlanResponse>(`${ROOT}/plans/${resource(planId)}/activate`, {
      method: "POST",
    }),
  archivePlan: (planId: string) =>
    apiRequest<{ plan_id: string; status: "archived" }>(
      `${ROOT}/plans/${resource(planId)}/archive`,
      { method: "POST" },
    ),
  createSession: (body: CreateWorkoutSessionRequest) =>
    apiRequest<WorkoutSessionResponse>(`${ROOT}/sessions`, { method: "POST", body }),
  listSessions: (limit = 10, offset = 0, planId?: string) => {
    const query = new URLSearchParams({ limit: String(limit), offset: String(offset) });
    if (planId) query.set("plan_id", planId);
    return apiRequest<Page<WorkoutSessionResponse>>(`${ROOT}/sessions?${query.toString()}`);
  },
  getSession: (sessionId: string) =>
    apiRequest<WorkoutSessionResponse>(`${ROOT}/sessions/${resource(sessionId)}`),
  updateSession: (sessionId: string, body: UpdateWorkoutSessionRequest) =>
    apiRequest<WorkoutSessionResponse>(`${ROOT}/sessions/${resource(sessionId)}`, {
      method: "PATCH",
      body,
    }),
  analyzeAdaptation: (planId: string) =>
    apiRequest<WorkoutAdaptationResponse>(`${ROOT}/adaptation/analyze`, {
      method: "POST",
      body: { plan_id: planId },
    }),
  updateProfile: (body: UserProfileRequest) =>
    apiRequest<void>("/profile", { method: "PUT", body }),
  updateHealthProfile: (body: HealthProfileRequest) =>
    apiRequest<void>("/health-profile", { method: "PUT", body }),
};
