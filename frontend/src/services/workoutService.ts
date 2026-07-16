import { apiRequest } from "./apiClient";
import type {
  CurrentWorkout,
  ExerciseProgress,
  WorkoutDay,
  WorkoutExercise,
  WorkoutHistory,
  WorkoutPlan,
  WorkoutSession,
} from "../types/workout";

type RawExercise = Omit<WorkoutExercise, "exerciseId" | "muscleGroups" | "restSeconds"> & {
  exercise_id: string;
  muscle_groups: string[];
  rest_seconds: number;
};
type RawDay = Omit<WorkoutDay, "dayNumber" | "estimatedDurationMinutes" | "exercises"> & {
  day_number: number;
  estimated_duration_minutes: number;
  exercises: RawExercise[];
};
type RawPlan = Omit<
  WorkoutPlan,
  "availableDays" | "sessionDurationMinutes" | "generatedAt" | "days"
> & {
  available_days: number;
  session_duration_minutes: number;
  generated_at: string;
  days: RawDay[];
};
type RawSession = Omit<
  WorkoutSession,
  "planId" | "workoutDayId" | "exerciseProgress" | "startedAt" | "completedAt" | "progress"
> & {
  plan_id: string;
  workout_day_id: string;
  exercise_progress: Array<{ exercise_id: string; completed_sets: number; skipped: boolean }>;
  progress: {
    completed_sets: number;
    total_sets: number;
    completed_exercises: number;
    total_exercises: number;
    completion_percentage: number;
  };
  started_at: string;
  completed_at: string | null;
};

function exercise(raw: RawExercise): WorkoutExercise {
  return {
    ...raw,
    exerciseId: raw.exercise_id,
    muscleGroups: raw.muscle_groups,
    restSeconds: raw.rest_seconds,
  };
}
function day(raw: RawDay): WorkoutDay {
  return {
    id: raw.id,
    title: raw.title,
    focus: raw.focus,
    dayNumber: raw.day_number,
    estimatedDurationMinutes: raw.estimated_duration_minutes,
    exercises: raw.exercises.map(exercise),
  };
}
function plan(raw: RawPlan): WorkoutPlan {
  return {
    ...raw,
    availableDays: raw.available_days,
    sessionDurationMinutes: raw.session_duration_minutes,
    generatedAt: raw.generated_at,
    days: raw.days.map(day),
  };
}
function progress(raw: RawSession["exercise_progress"][number]): ExerciseProgress {
  return {
    exerciseId: raw.exercise_id,
    completedSets: raw.completed_sets,
    skipped: raw.skipped,
  };
}
function session(raw: RawSession): WorkoutSession {
  return {
    id: raw.id,
    planId: raw.plan_id,
    workoutDayId: raw.workout_day_id,
    status: raw.status,
    exerciseProgress: raw.exercise_progress.map(progress),
    progress: {
      completedSets: raw.progress.completed_sets,
      totalSets: raw.progress.total_sets,
      completedExercises: raw.progress.completed_exercises,
      totalExercises: raw.progress.total_exercises,
      completionPercentage: raw.progress.completion_percentage,
    },
    startedAt: raw.started_at,
    completedAt: raw.completed_at,
  };
}

export const workoutService = {
  async current(): Promise<CurrentWorkout> {
    const raw = await apiRequest<{ plan: RawPlan; today: RawDay; session: RawSession | null }>(
      "/workouts/current",
    );
    return {
      plan: plan(raw.plan),
      today: day(raw.today),
      session: raw.session ? session(raw.session) : null,
    };
  },
  async generate(availableDays: number, duration: number): Promise<WorkoutPlan> {
    return plan(
      await apiRequest<RawPlan>("/workouts/generate", {
        method: "POST",
        body: { available_days: availableDays, session_duration_minutes: duration },
      }),
    );
  },
  async details(planId: string): Promise<WorkoutPlan> {
    return plan(await apiRequest<RawPlan>(`/workouts/${planId}`));
  },
  async history(): Promise<WorkoutHistory> {
    const raw = await apiRequest<{
      plans: RawPlan[];
      completed_sessions: number;
      weekly_adherence_percentage: number;
    }>("/workouts/history");
    return {
      plans: raw.plans.map(plan),
      completedSessions: raw.completed_sessions,
      weeklyAdherencePercentage: raw.weekly_adherence_percentage,
    };
  },
  async start(planId: string, dayId: string): Promise<WorkoutSession> {
    return session(
      await apiRequest<RawSession>(`/workouts/${planId}/days/${dayId}/sessions/start`, {
        method: "POST",
      }),
    );
  },
  async update(
    sessionId: string,
    exerciseId: string,
    completedSets: number,
    skipped: boolean,
  ): Promise<WorkoutSession> {
    return session(
      await apiRequest<RawSession>(`/workouts/sessions/${sessionId}/exercises/${exerciseId}`, {
        method: "PATCH",
        body: { completed_sets: completedSets, skipped },
      }),
    );
  },
  async complete(sessionId: string): Promise<WorkoutSession> {
    return session(
      await apiRequest<RawSession>(`/workouts/sessions/${sessionId}/complete`, { method: "POST" }),
    );
  },
};
