import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";
import { AuthContext } from "../contexts/AuthContext";
import { LocaleProvider } from "../contexts/LocaleContext";
import DashboardPage from "../pages/dashboard/DashboardPage";
import { setAccessToken, setRefreshHandler } from "../services/apiClient";
import { ThemeProvider } from "../theme";
import type { AuthContextValue, AuthUser } from "../types/auth";

const user: AuthUser = {
  id: "user-1",
  email: "member@example.com",
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};
const summary = {
  user: {
    display_name: "Member",
    primary_goal: "general_fitness",
    preferred_units: "metric",
    assessment_status: "completed",
    profile_completeness: 100,
    missing_profile_fields: [],
  },
  assessment: {
    status: "completed",
    session_id: "assessment-1",
    completion_percentage: 100,
    readiness_score: 80,
    risk_level: "low",
    safety_status: "safe",
    missing_categories: [],
    latest_completion_date: "2026-07-01T00:00:00Z",
    reassessment_recommended: false,
  },
  latest_check_in: {
    has_checked_in_today: true,
    date: "2026-07-19",
    readiness_score: 82,
    readiness_level: "ready",
    recommended_action: "train",
    warning_codes: [],
  },
  nutrition: {
    date: "2026-07-19",
    calories_consumed: 640,
    protein_consumed: 48,
    water_consumed_ml: 900,
    target_calories: 2200,
    water_target_ml: 2500,
    has_record: true,
  },
  workout: {
    session_id: "session-1",
    status: "completed",
    completion_percentage: 100,
    started_at: "2026-07-19T08:00:00Z",
    completed_at: "2026-07-19T08:45:00Z",
  },
  recent_activities: [
    {
      id: "workout:session-1",
      occurred_at: "2026-07-19T08:00:00Z",
      kind: "workout",
      title: "Workout recorded",
      detail: null,
      status: "completed",
    },
  ],
  history: [
    {
      date: "2026-07-19",
      calories_consumed: 640,
      workouts_completed: 1,
      active_minutes: 45,
      readiness_score: 82,
    },
  ],
  metadata: {
    generated_at: "2026-07-19T08:00:00Z",
    data_freshness: "live",
    partial_data: false,
    dashboard_version: "2.0",
  },
};
function renderDashboard() {
  const context: AuthContextValue = {
    user,
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    loginWithGoogle: vi.fn(),
    logout: vi.fn(),
    clearError: vi.fn(),
  };
  return render(
    <ThemeProvider>
      <LocaleProvider>
        <AuthContext.Provider value={context}>
          <MemoryRouter>
            <DashboardPage />
          </MemoryRouter>
        </AuthContext.Provider>
      </LocaleProvider>
    </ThemeProvider>,
  );
}
beforeEach(() => {
  vi.restoreAllMocks();
  setAccessToken("token");
  setRefreshHandler(null);
});
describe("record-backed dashboard summary", () => {
  it("shows loading while the summary is pending", () => {
    vi.spyOn(window, "fetch").mockReturnValue(new Promise(() => undefined));
    renderDashboard();
    expect(screen.getByLabelText("Preparing your dashboard")).toBeInTheDocument();
  });
  it("renders stored summary data and calls the summary endpoint", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(JSON.stringify(summary), { status: 200 }),
    );
    renderDashboard();
    expect(await screen.findByText("Workout recorded")).toBeVisible();
    expect(screen.getByText("640")).toBeVisible();
    expect(window.fetch).toHaveBeenCalledWith(
      expect.stringContaining("/dashboard/summary"),
      expect.any(Object),
    );
  });
  it("renders honest empty states without fabricated metrics", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          ...summary,
          latest_check_in: null,
          nutrition: null,
          workout: null,
          recent_activities: [],
          history: [],
        }),
        { status: 200 },
      ),
    );
    renderDashboard();
    expect(await screen.findByText("No weekly analytics records yet.")).toBeVisible();
    expect(screen.getByText("No workouts recorded yet")).toBeVisible();
    expect(screen.queryByText("1200")).not.toBeInTheDocument();
  });
  it("offers retry after a safe API failure", async () => {
    const fetch = vi
      .spyOn(window, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: "internal" }), { status: 503 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(summary), { status: 200 }));
    const actor = userEvent.setup();
    renderDashboard();
    const retry = await screen.findByRole("button", { name: "Refresh dashboard" });
    await actor.click(retry);
    expect(await screen.findByText("Workout recorded")).toBeVisible();
    expect(fetch).toHaveBeenCalledTimes(2);
  });
});
