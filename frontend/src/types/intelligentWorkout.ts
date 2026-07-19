export type ISODateTime = string;
export type GenerationMode = "deterministic" | "ai_assisted" | "deterministic_fallback";
export type WorkoutStatus = "active" | "archived";
export type SessionStatus = "in_progress" | "completed" | "abandoned";
export type WorkoutPlanType =
  | "weight_loss"
  | "muscle_gain"
  | "general_fitness"
  | "strength"
  | "football_performance"
  | "goalkeeper_performance"
  | "home_workout"
  | "beginner_foundation";
export type SectionType = "warmup" | "main" | "accessory" | "conditioning" | "cooldown";
export type MovementPattern =
  | "squat"
  | "hinge"
  | "push"
  | "pull"
  | "lunge"
  | "carry"
  | "core"
  | "rotation"
  | "locomotion"
  | "mobility"
  | "conditioning";

export interface WorkoutWarning {
  code: string;
  message: string;
  professional_guidance: boolean;
}

export interface SetPrescription {
  sets: number;
  min_reps: number;
  max_reps: number;
  rest_seconds: number;
  tempo: string;
  intensity_guidance: string;
  rpe_min: number;
  rpe_max: number;
  reps_in_reserve: number;
  duration_seconds: number | null;
  distance_meters: number | null;
  progression_limit_percentage: number;
}

export interface PlannedExercise {
  exercise_id: string;
  exercise_name: string;
  movement_pattern: MovementPattern;
  primary_muscles: string[];
  equipment: string[];
  prescription: SetPrescription;
  estimated_duration_minutes: number;
  alternatives: string[];
  instructions: string[];
  safety_notes: string[];
}

export interface WorkoutDay {
  day_number: number;
  weekday: number;
  title: string;
  focus: string;
  estimated_duration_minutes: number;
  sections: Array<{ section_type: SectionType; exercises: PlannedExercise[] }>;
  recovery_notes: string[];
  warnings: WorkoutWarning[];
  high_intensity: boolean;
}

export interface WorkoutPlanResponse {
  plan_id: string;
  plan_type: WorkoutPlanType;
  status: WorkoutStatus;
  duration_weeks: number;
  training_days_per_week: number;
  weekly_schedule: WorkoutDay[];
  warnings: WorkoutWarning[];
  safety_notes: string[];
  progression_guidance: string[];
  explanation: {
    summary: string;
    rationale: string[];
    motivation: string;
    recovery_reminder: string;
  };
  generation_mode: GenerationMode;
  generated_at: ISODateTime;
  activated_at: ISODateTime | null;
  archived_at: ISODateTime | null;
  version: number;
}

export interface CompletedSetInput {
  set_number: number;
  actual_reps?: number | null;
  actual_load_kg?: number | null;
  perceived_exertion?: number | null;
  completed: boolean;
}

export interface CompletedExerciseInput {
  exercise_id: string;
  completed_sets: CompletedSetInput[];
  skipped?: boolean;
  pain_reported?: boolean;
  pain_area?: string | null;
}

export interface WorkoutSessionResponse {
  session_id: string;
  plan_id: string;
  workout_day_id: string;
  day_number: number;
  status: SessionStatus;
  completion_percentage: number;
  completed_exercises: CompletedExerciseInput[];
  skipped_exercise_ids: string[];
  adaptation_flags: string[];
  planned_duration_minutes: number;
  actual_duration_minutes: number | null;
  notes?: string | null;
  started_at: ISODateTime;
  completed_at: ISODateTime | null;
  updated_at: ISODateTime;
}

export interface WorkoutAdaptationResponse {
  recommendation_code: string;
  action:
    | "reduce_volume"
    | "reduce_intensity"
    | "replace_exercise"
    | "add_recovery_day"
    | "shorten_session"
    | "maintain_plan"
    | "require_review"
    | "block_training";
  reason_code: string;
  severity: "info" | "caution" | "high" | "critical";
  evidence_summary: string[];
  automatic_application_allowed: boolean;
  affected_exercise_id: string | null;
  affected_day_number: number | null;
}

export interface Page<T> {
  items: T[];
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface GenerateWorkoutPlanRequest {
  duration_weeks?: number;
  use_ai_assistance?: boolean;
}
export interface CreateWorkoutSessionRequest {
  plan_id: string;
  day_number: number;
  status: SessionStatus;
  completed_exercises: CompletedExerciseInput[];
  actual_duration_minutes?: number | null;
  notes?: string | null;
}
export interface UpdateWorkoutSessionRequest {
  status?: SessionStatus | null;
  completed_exercises?: CompletedExerciseInput[] | null;
  actual_duration_minutes?: number | null;
  notes?: string | null;
}

export type TrainingGoal =
  | "fat_loss"
  | "muscle_gain"
  | "strength"
  | "general_fitness"
  | "endurance"
  | "football_performance"
  | "goalkeeper_performance";
export type Equipment =
  | "barbell"
  | "dumbbell"
  | "machine"
  | "cable"
  | "resistance_band"
  | "bodyweight"
  | "kettlebell"
  | "medicine_ball"
  | "bench"
  | "pull_up_bar"
  | "cardio_machine";

export interface UserProfileRequest {
  identity: {
    full_name: string;
    age: number;
    gender: "male" | "female" | "non_binary" | "prefer_not_to_say";
    country: string;
  };
  body: { height_cm: number; weight_kg: number; body_fat_percentage: number | null };
  goals: {
    primary_goal: TrainingGoal;
    secondary_goal: TrainingGoal | null;
    target_weight_kg: number | null;
    target_date: string | null;
  };
  training: {
    experience: "beginner" | "intermediate" | "advanced";
    available_days: number;
    session_duration_minutes: number;
    available_equipment: Equipment[];
    workout_location: "commercial_gym" | "home_gym" | "bodyweight_only" | "outdoor";
  };
  lifestyle: {
    sleep_hours: number;
    stress_level: number;
    activity_level: "sedentary" | "light" | "moderate" | "very_active" | "extra_active";
    daily_water_ml: number;
  };
  nutrition: {
    dietary_preferences: Array<"halal" | "vegetarian" | "vegan" | "no_pork" | "no_seafood">;
    allergies: Array<
      "milk" | "egg" | "peanut" | "tree_nut" | "soy" | "fish" | "shellfish" | "gluten"
    >;
    dietary_restrictions: string[];
  };
}

export type HealthSeverity = "mild" | "moderate" | "severe";
export interface HealthProfileRequest {
  injuries: Array<{
    area: string;
    description: string;
    severity: HealthSeverity;
    active: boolean;
    medically_cleared: boolean;
  }>;
  chronic_conditions: Array<{ name: string; controlled: boolean; medically_cleared: boolean }>;
  pain_areas: Array<{ area: string; intensity: number; movement_related: boolean }>;
  mobility_limitations: Array<{ area: string; description: string; severity: HealthSeverity }>;
  surgery_history: Array<{ procedure: string; surgery_date: string; medically_cleared: boolean }>;
}
