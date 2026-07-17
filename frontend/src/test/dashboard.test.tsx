import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AuthContext } from "../contexts/AuthContext";
import { LocaleProvider } from "../contexts/LocaleContext";
import DashboardPage from "../pages/dashboard/DashboardPage";
import { setAccessToken, setRefreshHandler } from "../services/apiClient";
import { ThemeProvider } from "../theme";
import type { AuthContextValue, AuthUser } from "../types/auth";

const authUser: AuthUser = {
  id: "user-1",
  email: "mohamed.ahmed@example.com",
  is_active: true,
  created_at: "2026-01-01T00:00:00Z",
};

const baseDashboard = {
  user: {
    display_name: "Mohamed Ahmed",
    primary_goal: null,
    preferred_units: "metric",
    assessment_status: "not_started",
    profile_completeness: 100,
    missing_profile_fields: [],
  },
  assessment: {
    status: "not_started",
    session_id: null,
    completion_percentage: 0,
    readiness_score: null,
    risk_level: null,
    safety_status: null,
    missing_categories: [],
    latest_completion_date: null,
    reassessment_recommended: false,
  },
  daily_priority: {
    action_type: "start_assessment",
    title: "Start your smart assessment",
    description: "Tell us about your goals, routine, and safety context.",
    destination_route: "/assessment",
    priority_reason: "An assessment is required before personalized planning.",
    severity: "info",
  },
  features: [
    {
      key: "assessment",
      title: "Smart assessment",
      status: "action_required",
      reason: "Complete the assessment to unlock personalized planning.",
      destination_route: "/assessment",
    },
    {
      key: "workout",
      title: "Workout planning",
      status: "locked",
      reason: "Complete the smart assessment first.",
      destination_route: null,
    },
    {
      key: "nutrition",
      title: "Nutrition planning",
      status: "locked",
      reason: "Complete the smart assessment first.",
      destination_route: null,
    },
    {
      key: "ai_coach",
      title: "AI Coach",
      status: "locked",
      reason: "Complete the smart assessment first.",
      destination_route: null,
    },
    {
      key: "progress",
      title: "Progress tracking",
      status: "locked",
      reason: "Complete the smart assessment first.",
      destination_route: null,
    },
    {
      key: "reports",
      title: "Reports",
      status: "locked",
      reason: "Reports require sufficient real progress data.",
      destination_route: null,
    },
  ],
  safety_notice: null,
  progress: {
    assessment_completion: 0,
    profile_completeness: 100,
    latest_readiness_score: null,
    last_activity_date: null,
  },
  quick_actions: [
    {
      action_type: "start_assessment",
      title: "Start assessment",
      description: "Open the assessment experience.",
      destination_route: "/assessment",
      priority_reason: "This action is valid for the current assessment state.",
      severity: "info",
    },
    {
      action_type: "log_out",
      title: "Log out",
      description: "End this authenticated session.",
      destination_route: null,
      priority_reason: "Logout is always available.",
      severity: "info",
    },
  ],
  metadata: {
    generated_at: "2026-07-16T08:00:00Z",
    data_freshness: "live",
    partial_data: false,
    dashboard_version: "1.0",
  },
};

function authContext(overrides: Partial<AuthContextValue> = {}): AuthContextValue {
  return {
    user: authUser,
    isLoading: false,
    error: null,
    login: vi.fn(),
    register: vi.fn(),
    loginWithGoogle: vi.fn(),
    logout: vi.fn().mockResolvedValue(undefined),
    clearError: vi.fn(),
    ...overrides,
  };
}

function renderDashboard(payload: object = baseDashboard) {
  vi.spyOn(window, "fetch").mockResolvedValue(
    new Response(JSON.stringify(payload), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }),
  );
  render(
    <ThemeProvider>
      <LocaleProvider>
        <AuthContext.Provider value={authContext()}>
          <MemoryRouter initialEntries={["/app"]}>
            <Routes>
              <Route path="/app" element={<DashboardPage />} />
              <Route path="/assessment" element={<p>Assessment destination</p>} />
              <Route path="/assessment/resume/:sessionId" element={<p>Resume destination</p>} />
              <Route
                path="/assessment/completed/:sessionId"
                element={<p>Completed destination</p>}
              />
            </Routes>
          </MemoryRouter>
        </AuthContext.Provider>
      </LocaleProvider>
    </ThemeProvider>,
  );
}

describe("intelligent dashboard", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    window.localStorage.setItem("rahfit.locale", "en");
    setAccessToken("test-access-token");
    setRefreshHandler(null);
  });

  it("announces the loading skeleton while the dashboard request is pending", () => {
    vi.spyOn(window, "fetch").mockReturnValue(new Promise(() => undefined));
    render(
      <ThemeProvider>
        <LocaleProvider>
          <AuthContext.Provider value={authContext()}>
            <MemoryRouter>
              <DashboardPage />
            </MemoryRouter>
          </AuthContext.Provider>
        </LocaleProvider>
      </ThemeProvider>,
    );

    expect(screen.getByLabelText("Preparing your dashboard")).toHaveAttribute("aria-busy", "true");
  });

  it("renders the real no-assessment state and navigates to assessment", async () => {
    const user = userEvent.setup();
    renderDashboard();

    expect(
      await screen.findByRole("heading", { name: "Start your smart assessment" }),
    ).toBeVisible();
    expect(
      screen
        .getAllByRole("progressbar", { name: "Assessment completion" })
        .every((progress) => progress.getAttribute("aria-valuenow") === "0"),
    ).toBe(true);
    await user.click(screen.getAllByRole("link", { name: "Start assessment" })[0]);
    expect(screen.getByText("Assessment destination")).toBeInTheDocument();
  });

  it("renders the resume priority and saved progress", async () => {
    renderDashboard({
      ...baseDashboard,
      user: { ...baseDashboard.user, assessment_status: "in_progress" },
      assessment: {
        ...baseDashboard.assessment,
        status: "in_progress",
        session_id: "session-1",
        completion_percentage: 42,
        readiness_score: 35,
        risk_level: "low",
        safety_status: "safe",
        missing_categories: ["medical"],
      },
      daily_priority: {
        ...baseDashboard.daily_priority,
        action_type: "resume_assessment",
        title: "Continue your assessment",
        destination_route: "/assessment/resume/session-1",
      },
    });

    expect(await screen.findByRole("heading", { name: "Continue your assessment" })).toBeVisible();
    expect(screen.getByRole("link", { name: "Resume assessment" })).toHaveAttribute(
      "href",
      "/assessment/resume/session-1",
    );
    expect(screen.getByText("Health and safety")).toBeInTheDocument();
  });

  it("renders completed assessment scores and coming-soon modules", async () => {
    renderDashboard({
      ...baseDashboard,
      user: { ...baseDashboard.user, primary_goal: "muscle_gain", assessment_status: "completed" },
      assessment: {
        ...baseDashboard.assessment,
        status: "completed",
        session_id: "completed-session",
        completion_percentage: 100,
        readiness_score: 86,
        risk_level: "low",
        safety_status: "safe",
        latest_completion_date: "2026-07-16T08:00:00Z",
      },
      daily_priority: {
        ...baseDashboard.daily_priority,
        action_type: "view_assessment_summary",
        title: "Review your assessment summary",
        destination_route: "/assessment/completed/completed-session",
        severity: "success",
      },
      features: baseDashboard.features.map((feature) =>
        feature.key === "assessment"
          ? {
              ...feature,
              status: "available",
              destination_route: "/assessment/completed/completed-session",
            }
          : feature.key === "reports"
            ? feature
            : {
                ...feature,
                status: "coming_soon",
                reason: "This module is planned but is not available.",
              },
      ),
      progress: {
        ...baseDashboard.progress,
        assessment_completion: 100,
        latest_readiness_score: 86,
        last_activity_date: "2026-07-16T08:00:00Z",
      },
    });

    expect(
      await screen.findByRole("heading", { name: "Review your assessment summary" }),
    ).toBeVisible();
    expect(screen.getByText("86")).toBeInTheDocument();
    expect(screen.getAllByText("Coming soon").length).toBeGreaterThan(0);
  });

  it("announces STOP safety and keeps planning features locked", async () => {
    renderDashboard({
      ...baseDashboard,
      user: { ...baseDashboard.user, assessment_status: "in_progress" },
      assessment: {
        ...baseDashboard.assessment,
        status: "in_progress",
        session_id: "session-stop",
        completion_percentage: 75,
        readiness_score: 20,
        risk_level: "critical",
        safety_status: "stop",
      },
      daily_priority: {
        ...baseDashboard.daily_priority,
        action_type: "review_safety_warning",
        title: "Review your safety notice",
        destination_route: "/assessment/resume/session-stop",
        severity: "danger",
      },
      safety_notice: {
        status: "stop",
        title: "Personalized planning is paused",
        message: "Medical clearance is required before personalized exercise guidance.",
        severity: "danger",
        plan_generation_blocked: true,
      },
    });

    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent("Personalized planning is paused");
    expect(alert).toHaveTextContent("Plan generation blocked");
    const workoutCard = screen
      .getByRole("heading", { name: "Workout planning" })
      .closest(".dashboard-feature-card");
    expect(workoutCard).not.toBeNull();
    expect(within(workoutCard as HTMLElement).getByText("Locked")).toBeInTheDocument();
  });

  it("announces partial data and refreshes through the network boundary", async () => {
    const user = userEvent.setup();
    const partial = {
      ...baseDashboard,
      assessment: { ...baseDashboard.assessment, status: "unavailable" },
      daily_priority: {
        ...baseDashboard.daily_priority,
        action_type: "continue_available_feature",
        title: "Dashboard data needs a refresh",
        description: "Some assessment data could not load.",
        destination_route: "/app",
        severity: "warning",
      },
      metadata: { ...baseDashboard.metadata, data_freshness: "partial", partial_data: true },
    };
    renderDashboard(partial);

    expect(await screen.findByText("Some dashboard data is temporarily unavailable")).toBeVisible();
    await user.click(screen.getByRole("button", { name: "Refresh dashboard" }));
    expect(window.fetch).toHaveBeenCalledTimes(2);
  });

  it("renders a safe backend error state", async () => {
    vi.spyOn(window, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ detail: "internal detail" }), { status: 503 }),
    );
    render(
      <ThemeProvider>
        <LocaleProvider>
          <AuthContext.Provider value={authContext()}>
            <MemoryRouter>
              <DashboardPage />
            </MemoryRouter>
          </AuthContext.Provider>
        </LocaleProvider>
      </ThemeProvider>,
    );

    expect(
      await screen.findByText("Your account is safe. Check the backend connection and try again."),
    ).toBeVisible();
    expect(screen.queryByText("internal detail")).not.toBeInTheDocument();
  });

  it("keeps the dashboard protected from unauthenticated access", () => {
    render(
      <AuthContext.Provider value={authContext({ user: null })}>
        <MemoryRouter initialEntries={["/app"]}>
          <Routes>
            <Route element={<ProtectedRoute />}>
              <Route path="/app" element={<p>Dashboard private content</p>} />
            </Route>
            <Route path="/login" element={<p>Login required</p>} />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );

    expect(screen.getByText("Login required")).toBeInTheDocument();
    expect(screen.queryByText("Dashboard private content")).not.toBeInTheDocument();
  });
});
