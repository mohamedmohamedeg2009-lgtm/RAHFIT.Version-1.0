export type TrainingGoal =
  | "fat_loss"
  | "muscle_gain"
  | "strength"
  | "general_fitness"
  | "endurance"
  | "football_performance"
  | "goalkeeper_performance";

export interface WorkoutExercise {
  exerciseId: string;
  name: string;
  description: string;
  muscleGroups: string[];
  equipment: string[];
  sets: number;
  reps: string;
  restSeconds: number;
  tempo: string;
  notes: string;
}

export interface WorkoutDay {
  id: string;
  dayNumber: number;
  title: string;
  focus: string;
  estimatedDurationMinutes: number;
  exercises: WorkoutExercise[];
}

export interface WorkoutPlan {
  id: string;
  goal: TrainingGoal;
  experience: "beginner" | "intermediate" | "advanced";
  location: "commercial_gym" | "home_gym" | "bodyweight_only";
  equipment: string[];
  injuries: string[];
  availableDays: number;
  sessionDurationMinutes: number;
  days: WorkoutDay[];
  status: "active" | "archived";
  version: number;
  generatedAt: string;
}

export interface ExerciseProgress {
  exerciseId: string;
  completedSets: number;
  skipped: boolean;
}

export interface WorkoutSession {
  id: string;
  planId: string;
  workoutDayId: string;
  status: "in_progress" | "completed";
  exerciseProgress: ExerciseProgress[];
  progress: {
    completedSets: number;
    totalSets: number;
    completedExercises: number;
    totalExercises: number;
    completionPercentage: number;
  };
  startedAt: string;
  completedAt: string | null;
}

export interface CurrentWorkout {
  plan: WorkoutPlan;
  today: WorkoutDay;
  session: WorkoutSession | null;
}

export interface WorkoutHistory {
  plans: WorkoutPlan[];
  completedSessions: number;
  weeklyAdherencePercentage: number;
}
