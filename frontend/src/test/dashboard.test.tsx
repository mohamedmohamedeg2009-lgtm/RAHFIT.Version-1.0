import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import "@testing-library/jest-dom/vitest";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { AuthContext } from "../contexts/AuthContext";
import { LocaleProvider } from "../contexts/LocaleContext";
import DashboardPage from "../pages/dashboard/DashboardPage";
import {
  setAccessToken,
  setRefreshHandler,
  apiRequest,
  ApiConnectionError,
} from "../services/apiClient";
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

  it("sends the authenticated token with the dashboard request", async () => {
    renderDashboard();

    await screen.findByRole("heading", { name: "Start your smart assessment" });
    const [, options] = vi.mocked(window.fetch).mock.calls[0];
    expect(new Headers(options?.headers).get("Authorization")).toBe("Bearer test-access-token");
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

  it("renders Smart Assessment as the primary feature with its real status", async () => {
    renderDashboard();

    const assessmentCard = (
      await screen.findByRole("heading", { name: "Smart assessment" })
    ).closest(".dashboard-feature-card");
    expect(assessmentCard).toHaveClass("is-primary");
    expect(within(assessmentCard as HTMLElement).getByText("Action required")).toBeVisible();
    expect(
      within(assessmentCard as HTMLElement).getByText("0% assessment completion"),
    ).toBeVisible();
  });

  it("shows the available workout plan using real dashboard values", async () => {
    renderDashboard({
      ...baseDashboard,
      workout: {
        plan_id: "plan-1",
        day_id: "day-2",
        title: "Strength foundation",
        focus: "Full body",
        status: "ready",
        completion_percentage: 25,
        destination_route: "/workouts/plan-1",
        last_activity_at: null,
      },
      features: baseDashboard.features.map((feature) =>
        feature.key === "workout"
          ? { ...feature, status: "available", destination_route: "/workouts/plan-1" }
          : feature,
      ),
    });

    const workoutCard = (await screen.findByRole("heading", { name: "Workout planning" })).closest(
      ".dashboard-feature-card",
    );
    expect(within(workoutCard as HTMLElement).getByText("Strength foundation")).toBeVisible();
    expect(within(workoutCard as HTMLElement).getByText("25% complete")).toBeVisible();
    expect(
      within(workoutCard as HTMLElement).getByRole("link", { name: "Open: Workout planning" }),
    ).toHaveAttribute("href", "/workouts/plan-1");
  });

  it("keeps nutrition, AI Coach, and reports honest when data or availability is missing", async () => {
    renderDashboard({
      ...baseDashboard,
      features: baseDashboard.features.map((feature) => {
        if (feature.key === "nutrition") {
          return {
            ...feature,
            status: "available",
            reason: "A nutrition plan has not been generated yet.",
          };
        }
        return feature;
      }),
    });

    const nutritionCard = (
      await screen.findByRole("heading", { name: "Nutrition planning" })
    ).closest(".dashboard-feature-card");
    expect(
      within(nutritionCard as HTMLElement).getByText(
        "A nutrition plan has not been generated yet.",
      ),
    ).toBeVisible();
    expect(
      within(nutritionCard as HTMLElement).queryByLabelText("Nutrition planning details"),
    ).not.toBeInTheDocument();

    const coachCard = screen
      .getByRole("heading", { name: "AI Coach" })
      .closest(".dashboard-feature-card");
    const reportsCard = screen
      .getByRole("heading", { name: "Reports" })
      .closest(".dashboard-feature-card");
    expect(within(coachCard as HTMLElement).getByText("Locked")).toBeVisible();
    expect(within(reportsCard as HTMLElement).getByText("Locked")).toBeVisible();
  });

  it("renders the feature grid in RTL when Arabic is selected", async () => {
    window.localStorage.setItem("rahfit.locale", "ar");
    renderDashboard();

    await screen.findByRole("heading", { name: "Smart assessment" });
    expect(document.documentElement).toHaveAttribute("dir", "rtl");
    expect(document.querySelector(".dashboard-feature-grid")).toBeInTheDocument();
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

  it("keeps loaded dashboard content visible when a refresh fails", async () => {
    const user = userEvent.setup();
    const partial = {
      ...baseDashboard,
      daily_priority: {
        ...baseDashboard.daily_priority,
        action_type: "continue_available_feature",
        title: "Dashboard data needs a refresh",
        severity: "warning",
      },
      metadata: { ...baseDashboard.metadata, data_freshness: "partial", partial_data: true },
    };
    vi.spyOn(window, "fetch")
      .mockResolvedValueOnce(new Response(JSON.stringify(partial), { status: 200 }))
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ detail: "unavailable" }), { status: 503 }),
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

    await screen.findByRole("heading", { name: "Dashboard data needs a refresh" });
    await user.click(screen.getByRole("button", { name: "Refresh dashboard" }));
    await screen.findByText("Your dashboard could not load");
    expect(screen.getByRole("heading", { name: "Dashboard data needs a refresh" })).toBeVisible();
  });

  it("cancels an in-flight dashboard request when the page unmounts", async () => {
    let capturedSignal: AbortSignal | undefined;
    vi.spyOn(window, "fetch").mockImplementation((_input, options) => {
      capturedSignal = options?.signal as AbortSignal;
      return new Promise(() => undefined);
    });
    const view = render(
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

    await waitFor(() => expect(capturedSignal).toBeDefined());
    view.unmount();
    expect(capturedSignal?.aborted).toBe(true);
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

  it("does not retry 4xx client responses", async () => {
    let callCount = 0;
    vi.spyOn(window, "fetch").mockImplementation(async () => {
      callCount++;
      return new Response(JSON.stringify({ detail: "bad request" }), { status: 400 });
    });

    await expect(apiRequest("/dashboard", { retries: 2, retryDelay: 1 })).rejects.toThrow();
    expect(callCount).toBe(1);
  });

  it("retries 5xx server responses with exponential backoff", async () => {
    let callCount = 0;
    vi.spyOn(window, "fetch").mockImplementation(async () => {
      callCount++;
      return new Response(JSON.stringify({ detail: "server error" }), { status: 500 });
    });

    await expect(apiRequest("/dashboard", { retries: 2, retryDelay: 1 })).rejects.toThrow();
    expect(callCount).toBe(3); // Initial call + 2 retries
  });

  it("respects and forwards AbortSignal user cancellation instantly without retry", async () => {
    let callCount = 0;
    vi.spyOn(window, "fetch").mockImplementation(async () => {
      callCount++;
      throw new DOMException("The user aborted a request.", "AbortError");
    });

    const controller = new AbortController();
    controller.abort();

    await expect(
      apiRequest("/dashboard", { signal: controller.signal, retries: 2, retryDelay: 1 }),
    ).rejects.toThrow(
      new ApiConnectionError("The request was cancelled.", "network_or_cors_error"),
    );
    expect(callCount).toBe(0); // Should not even make the call since already aborted
  });
});
