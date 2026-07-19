import { apiRequest } from "./apiClient";

export type HydrationStatus = "low" | "moderate" | "good";
export type ReadinessLevel = "high" | "moderate" | "low" | "recovery_required";
export type RecommendedAction =
  "normal_training" | "reduced_intensity" | "recovery_session" | "rest_and_professional_guidance";

export interface DailyCheckInInputs {
  sleep_hours: number;
  sleep_quality: number;
  energy_level: number;
  stress_level: number;
  muscle_soreness: number;
  pain_level: number;
  hydration_status: HydrationStatus;
  mood: number;
  optional_note?: string | null;
  check_in_date?: string | null;
}

export interface DeterministicReadinessResult {
  readiness_score: number;
  readiness_level: ReadinessLevel;
  recovery_score: number;
  sleep_score: number;
  stress_score: number;
  hydration_score: number;
  pain_flag: boolean;
  warning_codes: string[];
  recommended_action: RecommendedAction;
}

export interface DailyCheckIn {
  id: string;
  user_id: string;
  date: string;
  inputs: DailyCheckInInputs;
  readiness_result: DeterministicReadinessResult;
  created_at: string;
  updated_at: string;
  schema_version: number;
}

export interface DailyCheckInResponse {
  check_in: DailyCheckIn;
}

export interface DailyCheckInHistoryResponse {
  items: DailyCheckIn[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export const dailyCheckInService = {
  async submitCheckIn(
    inputs: DailyCheckInInputs,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<DailyCheckInResponse> {
    return apiRequest<DailyCheckInResponse>("/api/v1/check-ins/daily", {
      method: "POST",
      body: JSON.stringify(inputs),
      ...options,
    });
  },

  async getTodayCheckIn(options?: Parameters<typeof apiRequest>[1]): Promise<DailyCheckInResponse> {
    return apiRequest<DailyCheckInResponse>("/api/v1/check-ins/daily/today", {
      method: "GET",
      ...options,
    });
  },

  async getHistory(
    limit: number = 20,
    offset: number = 0,
    options?: Parameters<typeof apiRequest>[1],
  ): Promise<DailyCheckInHistoryResponse> {
    return apiRequest<DailyCheckInHistoryResponse>(
      `/api/v1/check-ins/daily/history?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        ...options,
      },
    );
  },
};
