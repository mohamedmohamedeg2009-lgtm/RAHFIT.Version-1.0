import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import WorkoutAdaptationPage from "../pages/intelligentWorkout/WorkoutAdaptationPage";
import WorkoutGenerationPage from "../pages/intelligentWorkout/WorkoutGenerationPage";
import WorkoutHealthSetupPage from "../pages/intelligentWorkout/WorkoutHealthSetupPage";
import WorkoutOverviewPage from "../pages/intelligentWorkout/WorkoutOverviewPage";
import WorkoutPlanDetailPage from "../pages/intelligentWorkout/WorkoutPlanDetailPage";
import WorkoutProfileSetupPage from "../pages/intelligentWorkout/WorkoutProfileSetupPage";
import IntelligentWorkoutSessionPage from "../pages/intelligentWorkout/WorkoutSessionPage";
import { ApiError, setAccessToken } from "../services/apiClient";
import { intelligentWorkoutService } from "../services/intelligentWorkoutService";
import { mapWorkoutError } from "../services/workoutErrorMapper";
import type { WorkoutPlanResponse, WorkoutSessionResponse } from "../types/intelligentWorkout";

const exercise = {
  exercise_id: "goblet_squat",
  exercise_name: "Goblet Squat",
  movement_pattern: "squat" as const,
  primary_muscles: ["quadriceps"],
  equipment: ["dumbbell"],
  estimated_duration_minutes: 10,
  alternatives: ["box_squat"],
  instructions: ["Brace before descending."],
  safety_notes: ["Stop if pain occurs."],
  prescription: {
    sets: 2,
    min_reps: 8,
    max_reps: 10,
    rest_seconds: 60,
    tempo: "controlled",
    intensity_guidance: "Leave three repetitions in reserve.",
    rpe_min: 5,
    rpe_max: 7,
    reps_in_reserve: 3,
    duration_seconds: null,
    distance_meters: null,
    progression_limit_percentage: 5,
  },
};
const warmupExercise = {
  ...exercise,
  exercise_id: "bodyweight_squat",
  exercise_name: "Bodyweight Squat",
};
const cooldownExercise = {
  ...exercise,
  exercise_id: "squat_mobility",
  exercise_name: "Squat Mobility",
};
const plan: WorkoutPlanResponse = {
  plan_id: "plan-1",
  plan_type: "general_fitness",
  status: "active",
  duration_weeks: 8,
  training_days_per_week: 1,
  weekly_schedule: [
    {
      day_number: 1,
      weekday: 1,
      title: "Foundation Day",
      focus: "Full body control",
      estimated_duration_minutes: 45,
      sections: [
        { section_type: "warmup", exercises: [warmupExercise] },
        { section_type: "main", exercises: [exercise] },
        { section_type: "cooldown", exercises: [cooldownExercise] },
      ],
      recovery_notes: ["Sleep well."],
      warnings: [],
      high_intensity: false,
    },
  ],
  warnings: [],
  safety_notes: ["Stop for unusual symptoms."],
  progression_guidance: ["Progress only inside the stated limit."],
  explanation: {
    summary: "A controlled foundation plan.",
    rationale: ["Matches current readiness."],
    motivation: "Consistency wins.",
    recovery_reminder: "Recover before the next session.",
  },
  generation_mode: "deterministic",
  generated_at: "2026-07-17T10:00:00Z",
  activated_at: "2026-07-17T10:00:00Z",
  archived_at: null,
  version: 1,
};
const session: WorkoutSessionResponse = {
  session_id: "session-1",
  plan_id: "plan-1",
  workout_day_id: "day-1",
  day_number: 1,
  status: "in_progress",
  completion_percentage: 0,
  completed_exercises: [],
  skipped_exercise_ids: [],
  adaptation_flags: [],
  planned_duration_minutes: 45,
  actual_duration_minutes: null,
  started_at: "2026-07-17T10:00:00Z",
  completed_at: null,
  updated_at: "2026-07-17T10:00:00Z",
};

function renderRoute(element: React.ReactNode, path = "/intelligent-workouts", route = path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route path={route} element={element} />
        <Route path="*" element={<p>Destination</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

beforeEach(() => {
  setAccessToken("access-token");
});
afterEach(() => vi.restoreAllMocks());

describe("intelligent workout API service", () => {
  it("uses the authenticated central client and exact generation contract", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(plan), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      }),
    );
    await intelligentWorkoutService.generatePlan({ duration_weeks: 8, use_ai_assistance: true });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/intelligent-workouts/plans/generate"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ duration_weeks: 8, use_ai_assistance: true }),
        headers: expect.objectContaining({ Authorization: "Bearer access-token" }),
      }),
    );
  });

  it("preserves the ownership-safe not-found response", () => {
    const mapped = mapWorkoutError(new ApiError("Not found", 404, "workout_plan_not_found"));
    expect(mapped.message).not.toContain("owner");
    expect(mapped.actionPath).toBe("/intelligent-workouts");
  });

  it("uses exact setup, session, adaptation, and pagination paths without owner fields", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ items: [], limit: 10, offset: 0, has_more: false }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    await intelligentWorkoutService.listSessions(10, 0, "plan-1");
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining("/intelligent-workouts/sessions?limit=10&offset=0&plan_id=plan-1"),
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: expect.any(String) }),
      }),
    );

    fetchMock.mockResolvedValueOnce(new Response(null, { status: 204 }));
    await intelligentWorkoutService.updateHealthProfile({
      injuries: [],
      chronic_conditions: [],
      pain_areas: [],
      mobility_limitations: [],
      surgery_history: [],
    });
    const healthRequest = fetchMock.mock.calls.at(-1)?.[1];
    expect(fetchMock.mock.calls.at(-1)?.[0]).toEqual(expect.stringContaining("/health-profile"));
    expect(healthRequest).toEqual(expect.objectContaining({ method: "PUT" }));
    expect(String(healthRequest?.body)).not.toContain("user_id");

    fetchMock.mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          recommendation_code: "maintain",
          action: "maintain_plan",
          reason_code: "stable",
          severity: "info",
          evidence_summary: [],
          automatic_application_allowed: false,
          affected_exercise_id: null,
          affected_day_number: null,
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    await intelligentWorkoutService.analyzeAdaptation("plan-1");
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining("/intelligent-workouts/adaptation/analyze"),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ plan_id: "plan-1" }) }),
    );
  });

  it("maps authentication, profile, health, readiness, and clearance codes deterministically", () => {
    expect(mapWorkoutError(new ApiError("", 401, "request_failed")).actionPath).toBe("/login");
    expect(
      mapWorkoutError(new ApiError("", 409, "workout_profile_incomplete")).actionPath,
    ).toContain("profile");
    expect(
      mapWorkoutError(new ApiError("", 409, "workout_health_profile_incomplete")).actionPath,
    ).toContain("health");
    expect(mapWorkoutError(new ApiError("", 403, "workout_readiness_blocked")).retryable).toBe(
      false,
    );
    expect(mapWorkoutError(new ApiError("", 403, "workout_medical_clearance_required")).title).toBe(
      "Medical clearance required",
    );
  });
});

describe("intelligent workout screens", () => {
  it("shows a loading skeleton while the active plan request is pending", () => {
    vi.spyOn(intelligentWorkoutService, "getActivePlan").mockReturnValue(
      new Promise(() => undefined),
    );
    const view = renderRoute(<WorkoutOverviewPage />);
    expect(view.container.querySelector(".ds-skeleton")).not.toBeNull();
  });

  it("renders the active overview and a server-owned schedule", async () => {
    vi.spyOn(intelligentWorkoutService, "getActivePlan").mockResolvedValue(plan);
    renderRoute(<WorkoutOverviewPage />);
    expect(await screen.findByRole("heading", { name: "Foundation Day" })).toBeInTheDocument();
    expect(screen.getByText("Deterministic")).toBeInTheDocument();
  });

  it("shows the setup path when no active plan exists", async () => {
    vi.spyOn(intelligentWorkoutService, "getActivePlan").mockRejectedValue(
      new ApiError("Not found", 404, "workout_plan_not_found"),
    );
    renderRoute(<WorkoutOverviewPage />);
    expect(await screen.findByRole("link", { name: "Start setup" })).toHaveAttribute(
      "href",
      "/intelligent-workouts/setup/profile",
    );
  });

  it.each([
    ["workout_profile_incomplete", "Complete your profile"],
    ["workout_health_profile_incomplete", "Health declaration required"],
    ["workout_readiness_blocked", "Training is paused"],
  ])("renders actionable overview error %s", async (code, title) => {
    vi.spyOn(intelligentWorkoutService, "getActivePlan").mockRejectedValue(
      new ApiError("", code === "workout_readiness_blocked" ? 403 : 409, code),
    );
    renderRoute(<WorkoutOverviewPage />);
    expect(await screen.findByText(title)).toBeInTheDocument();
  });

  it("keeps native required profile validation on the client", async () => {
    const update = vi
      .spyOn(intelligentWorkoutService, "updateProfile")
      .mockResolvedValue(undefined);
    renderRoute(<WorkoutProfileSetupPage />, "/intelligent-workouts/setup/profile");
    await userEvent.click(screen.getByRole("button", { name: "Save and continue" }));
    expect(update).not.toHaveBeenCalled();
  });

  it("submits a complete profile then advances to health setup", async () => {
    const update = vi
      .spyOn(intelligentWorkoutService, "updateProfile")
      .mockResolvedValue(undefined);
    renderRoute(<WorkoutProfileSetupPage />, "/intelligent-workouts/setup/profile");
    await userEvent.type(screen.getByLabelText(/Full name/), "Mohamed Ahmed");
    await userEvent.type(screen.getByLabelText(/Country code/), "eg");
    await userEvent.click(screen.getByRole("button", { name: "Save and continue" }));
    await waitFor(() =>
      expect(update).toHaveBeenCalledWith(
        expect.objectContaining({
          identity: expect.objectContaining({ full_name: "Mohamed Ahmed", country: "EG" }),
        }),
      ),
    );
    expect(await screen.findByText("Destination")).toBeInTheDocument();
  });

  it("requires an explicit health declaration and sends empty categories", async () => {
    const update = vi
      .spyOn(intelligentWorkoutService, "updateHealthProfile")
      .mockResolvedValue(undefined);
    renderRoute(<WorkoutHealthSetupPage />, "/intelligent-workouts/setup/health");
    expect(screen.getByRole("button", { name: "Save health declaration" })).toBeDisabled();
    await userEvent.click(
      screen.getByRole("checkbox", {
        name: /I confirm this declaration is accurate and complete/,
      }),
    );
    await userEvent.click(screen.getByRole("button", { name: "Save health declaration" }));
    await waitFor(() =>
      expect(update).toHaveBeenCalledWith({
        injuries: [],
        chronic_conditions: [],
        pain_areas: [],
        mobility_limitations: [],
        surgery_history: [],
      }),
    );
  });

  it("shows backend validation errors without exposing private health fields", async () => {
    vi.spyOn(intelligentWorkoutService, "updateHealthProfile").mockRejectedValue(
      new ApiError("Rejected", 422, "validation_error"),
    );
    renderRoute(<WorkoutHealthSetupPage />, "/intelligent-workouts/setup/health");
    expect(screen.queryByLabelText(/private notes/i)).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("checkbox", { name: /I confirm this declaration/ }));
    await userEvent.click(screen.getByRole("button", { name: "Save health declaration" }));
    expect(await screen.findByText("Check your entries")).toBeInTheDocument();
  });

  it.each(["deterministic", "ai_assisted"] as const)(
    "accepts successful %s generation",
    async (mode) => {
      vi.spyOn(intelligentWorkoutService, "generatePlan").mockResolvedValue({
        ...plan,
        generation_mode: mode,
      });
      renderRoute(<WorkoutGenerationPage />, "/intelligent-workouts/generate");
      await userEvent.click(screen.getByRole("button", { name: "Generate safe plan" }));
      expect(await screen.findByText("Plan ready")).toBeInTheDocument();
    },
  );

  it("prevents duplicate generation while a request is pending", async () => {
    let resolvePlan: ((value: WorkoutPlanResponse) => void) | undefined;
    const pending = new Promise<WorkoutPlanResponse>((resolve) => {
      resolvePlan = resolve;
    });
    const generate = vi.spyOn(intelligentWorkoutService, "generatePlan").mockReturnValue(pending);
    renderRoute(<WorkoutGenerationPage />, "/intelligent-workouts/generate");
    const button = screen.getByRole("button", { name: "Generate safe plan" });
    await userEvent.click(button);
    expect(button).toBeDisabled();
    await userEvent.click(button);
    expect(generate).toHaveBeenCalledTimes(1);
    resolvePlan?.(plan);
    expect(await screen.findByText("Plan ready")).toBeInTheDocument();
  });

  it.each([
    ["workout_readiness_blocked", "Training is paused"],
    ["workout_medical_clearance_required", "Medical clearance required"],
  ])("blocks generation safely for %s", async (code, title) => {
    vi.spyOn(intelligentWorkoutService, "generatePlan").mockRejectedValue(
      new ApiError("", 403, code),
    );
    renderRoute(<WorkoutGenerationPage />, "/intelligent-workouts/generate");
    await userEvent.click(screen.getByRole("button", { name: "Generate safe plan" }));
    expect(await screen.findByText(title)).toBeInTheDocument();
  });

  it("treats deterministic fallback as a successful generated plan", async () => {
    vi.spyOn(intelligentWorkoutService, "generatePlan").mockResolvedValue({
      ...plan,
      generation_mode: "deterministic_fallback",
    });
    renderRoute(<WorkoutGenerationPage />, "/intelligent-workouts/generate");
    await userEvent.click(screen.getByRole("button", { name: "Generate safe plan" }));
    expect(await screen.findByText("Safe deterministic plan created")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open plan" })).toHaveAttribute(
      "href",
      "/intelligent-workouts/plans/plan-1",
    );
  });

  it("renders the complete plan hierarchy and safety notes", async () => {
    vi.spyOn(intelligentWorkoutService, "getPlan").mockResolvedValue({
      ...plan,
      user_id: "must-not-render",
      provider: "must-not-render",
    } as WorkoutPlanResponse);
    renderRoute(
      <WorkoutPlanDetailPage />,
      "/intelligent-workouts/plans/plan-1",
      "/intelligent-workouts/plans/:planId",
    );
    expect(await screen.findByRole("heading", { name: "Goblet Squat" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Bodyweight Squat" })).toBeInTheDocument();
    expect(screen.getAllByText("Stop if pain occurs.")).toHaveLength(3);
    expect(screen.queryByText("must-not-render")).not.toBeInTheDocument();
  });

  it("starts and saves a session snapshot without calculating progress", async () => {
    vi.spyOn(intelligentWorkoutService, "createSession").mockResolvedValue(session);
    vi.spyOn(intelligentWorkoutService, "getPlan").mockResolvedValue(plan);
    const update = vi
      .spyOn(intelligentWorkoutService, "updateSession")
      .mockResolvedValue({ ...session, completion_percentage: 50 });
    renderRoute(
      <IntelligentWorkoutSessionPage />,
      "/intelligent-workouts/plans/plan-1/session/1",
      "/intelligent-workouts/plans/:planId/session/:dayNumber",
    );
    await userEvent.click(await screen.findByRole("button", { name: "Start workout session" }));
    await userEvent.click((await screen.findAllByLabelText("Completed"))[0]);
    expect(screen.getAllByLabelText("Completed")).toHaveLength(6);
    expect(screen.queryByRole("button", { name: /add set/i })).not.toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Save progress" }));
    await waitFor(() =>
      expect(update).toHaveBeenCalledWith(
        "session-1",
        expect.objectContaining({ status: "in_progress", completed_exercises: expect.any(Array) }),
      ),
    );
    expect(await screen.findByText("50%", { selector: "strong" })).toBeInTheDocument();
  });

  it("shows pain flags and removes terminal mutation actions", async () => {
    vi.spyOn(intelligentWorkoutService, "getSession").mockResolvedValue({
      ...session,
      status: "completed",
      completion_percentage: 100,
      adaptation_flags: ["pain_reported"],
      completed_at: "2026-07-17T11:00:00Z",
    });
    vi.spyOn(intelligentWorkoutService, "getPlan").mockResolvedValue(plan);
    renderRoute(
      <IntelligentWorkoutSessionPage />,
      "/intelligent-workouts/sessions/session-1",
      "/intelligent-workouts/sessions/:sessionId",
    );
    expect(await screen.findByText("Pain Reported")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Complete session" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Save progress" })).not.toBeInTheDocument();
  });

  it("displays adaptation as guidance without applying it", async () => {
    const analyze = vi.spyOn(intelligentWorkoutService, "analyzeAdaptation").mockResolvedValue({
      recommendation_code: "maintain",
      action: "maintain_plan",
      reason_code: "stable",
      severity: "info",
      evidence_summary: ["Session evidence is stable."],
      automatic_application_allowed: false,
      affected_exercise_id: null,
      affected_day_number: null,
    });
    renderRoute(
      <WorkoutAdaptationPage />,
      "/intelligent-workouts/plans/plan-1/adaptation",
      "/intelligent-workouts/plans/:planId/adaptation",
    );
    await userEvent.click(screen.getByRole("button", { name: "Analyze adaptation" }));
    expect(
      await screen.findByText("This is guidance only. It has not changed your plan."),
    ).toBeInTheDocument();
    expect(analyze).toHaveBeenCalledWith("plan-1");
  });
});
