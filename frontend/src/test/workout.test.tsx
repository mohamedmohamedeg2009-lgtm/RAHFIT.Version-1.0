import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { LocaleProvider } from "../contexts/LocaleContext";
import WorkoutPage from "../pages/workout/WorkoutPage";
import WorkoutSessionPage from "../pages/workout/WorkoutSessionPage";

const plan = {
  id: "plan-1",
  user_id: "user-1",
  assessment_result_id: "result-1",
  goal: "general_fitness",
  experience: "beginner",
  location: "home_gym",
  equipment: ["bodyweight"],
  injuries: [],
  available_days: 3,
  session_duration_minutes: 30,
  days: [
    {
      id: "day-1",
      day_number: 1,
      title: "Day 1 — Full Body",
      focus: "full_body",
      estimated_duration_minutes: 30,
      exercises: [
        {
          exercise_id: "box_squat",
          name: "Box Squat",
          description: "Sit back to a stable box and stand tall.",
          muscle_groups: ["quadriceps"],
          equipment: ["bodyweight"],
          sets: 2,
          reps: "8-12",
          rest_seconds: 60,
          tempo: "3-1-2",
          notes: "Use controlled technique.",
        },
      ],
    },
  ],
  status: "active",
  generation_key: "key",
  version: 1,
  generated_at: "2026-07-16T10:00:00Z",
  updated_at: "2026-07-16T10:00:00Z",
};
const session = {
  id: "session-1",
  user_id: "user-1",
  plan_id: "plan-1",
  workout_day_id: "day-1",
  scheduled_date: "2026-07-16",
  status: "in_progress",
  exercise_progress: [{ exercise_id: "box_squat", completed_sets: 0, skipped: false }],
  progress: {
    completed_sets: 0,
    total_sets: 2,
    completed_exercises: 0,
    total_exercises: 1,
    completion_percentage: 0,
  },
  revision: 0,
  started_at: "2026-07-16T10:00:00Z",
  completed_at: null,
  updated_at: "2026-07-16T10:00:00Z",
};

function json(payload: unknown, status = 200) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

afterEach(() => vi.restoreAllMocks());

describe("workout experience", () => {
  it("renders today's real plan returned by the API", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(() =>
      json({ plan, today: plan.days[0], session: null }),
    );
    render(
      <LocaleProvider>
        <MemoryRouter>
          <WorkoutPage />
        </MemoryRouter>
      </LocaleProvider>,
    );
    expect(await screen.findAllByRole("heading", { name: "Day 1 — Full Body" })).toHaveLength(2);
    expect(screen.getByRole("link", { name: "Open session" }).getAttribute("href")).toBe(
      "/workouts/plan-1/session/day-1",
    );
  });

  it("records completed sets through the session API", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockImplementation((request, init) => {
      const url = String(request);
      if (url.endsWith("/workouts/plan-1")) return json(plan);
      if (url.includes("sessions/start")) return json(session, 201);
      if (init?.method === "PATCH")
        return json({
          ...session,
          exercise_progress: [{ exercise_id: "box_squat", completed_sets: 1, skipped: false }],
          progress: { ...session.progress, completed_sets: 1, completion_percentage: 50 },
        });
      return json({}, 404);
    });
    render(
      <LocaleProvider>
        <MemoryRouter initialEntries={["/workouts/plan-1/session/day-1"]}>
          <Routes>
            <Route path="/workouts/:planId/session/:dayId" element={<WorkoutSessionPage />} />
          </Routes>
        </MemoryRouter>
      </LocaleProvider>,
    );
    await userEvent.click(await screen.findByRole("button", { name: "Complete set" }));
    await waitFor(() => expect(screen.getByText("1 / 2")).toBeTruthy());
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/exercises/box_squat"),
      expect.objectContaining({ method: "PATCH" }),
    );
  });
});
