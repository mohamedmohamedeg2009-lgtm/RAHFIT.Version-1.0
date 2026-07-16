from datetime import UTC, date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class MuscleGroup(StrEnum):
    CHEST = "chest"
    BACK = "back"
    SHOULDERS = "shoulders"
    BICEPS = "biceps"
    TRICEPS = "triceps"
    QUADRICEPS = "quadriceps"
    HAMSTRINGS = "hamstrings"
    GLUTES = "glutes"
    CALVES = "calves"
    CORE = "core"
    FULL_BODY = "full_body"


class Equipment(StrEnum):
    BARBELL = "barbell"
    DUMBBELL = "dumbbell"
    MACHINE = "machine"
    CABLE = "cable"
    RESISTANCE_BAND = "resistance_band"
    BODYWEIGHT = "bodyweight"
    KETTLEBELL = "kettlebell"
    MEDICINE_BALL = "medicine_ball"
    BENCH = "bench"
    PULL_UP_BAR = "pull_up_bar"
    CARDIO_MACHINE = "cardio_machine"


class TrainingGoal(StrEnum):
    FAT_LOSS = "fat_loss"
    MUSCLE_GAIN = "muscle_gain"
    STRENGTH = "strength"
    GENERAL_FITNESS = "general_fitness"
    ENDURANCE = "endurance"
    FOOTBALL_PERFORMANCE = "football_performance"
    GOALKEEPER_PERFORMANCE = "goalkeeper_performance"


class ExperienceLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class TrainingLocation(StrEnum):
    COMMERCIAL_GYM = "commercial_gym"
    HOME_GYM = "home_gym"
    BODYWEIGHT_ONLY = "bodyweight_only"
    OUTDOOR = "outdoor"


class ExerciseDifficulty(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class MovementType(StrEnum):
    SQUAT = "squat"
    HINGE = "hinge"
    HORIZONTAL_PUSH = "horizontal_push"
    VERTICAL_PUSH = "vertical_push"
    HORIZONTAL_PULL = "horizontal_pull"
    VERTICAL_PULL = "vertical_pull"
    LUNGE = "lunge"
    CARRY = "carry"
    CORE = "core"
    LOCOMOTION = "locomotion"
    POWER = "power"


class ExerciseType(StrEnum):
    STRENGTH = "strength"
    CONDITIONING = "conditioning"
    POWER = "power"
    CORE = "core"
    MOBILITY = "mobility"


class ExerciseClassification(StrEnum):
    COMPOUND = "compound"
    ISOLATION = "isolation"


class WorkoutPlanStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class WorkoutSessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Exercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str
    description: str
    muscle_groups: tuple[MuscleGroup, ...]
    equipment: tuple[Equipment, ...]
    difficulty: ExerciseDifficulty
    experience_level: ExperienceLevel
    movement_type: MovementType
    exercise_type: ExerciseType
    classification: ExerciseClassification
    recommended_reps: str
    recommended_sets: tuple[int, int]
    rest_range_seconds: tuple[int, int]
    tempo: str
    contraindications: tuple[str, ...] = ()
    supported_injuries: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    active: bool = True
    version: int = Field(default=1, ge=1)


class WorkoutExercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    name: str
    description: str
    muscle_groups: tuple[MuscleGroup, ...]
    equipment: tuple[Equipment, ...]
    sets: int = Field(ge=1, le=10)
    reps: str
    rest_seconds: int = Field(ge=0, le=600)
    tempo: str
    notes: str


class WorkoutDay(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    day_number: int = Field(ge=1, le=7)
    title: str
    focus: str
    estimated_duration_minutes: int = Field(ge=20, le=120)
    exercises: tuple[WorkoutExercise, ...]


class WorkoutPlan(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    assessment_result_id: str
    goal: TrainingGoal
    experience: ExperienceLevel
    location: TrainingLocation
    equipment: tuple[Equipment, ...]
    injuries: tuple[str, ...]
    available_days: int = Field(ge=2, le=6)
    session_duration_minutes: int = Field(ge=30, le=90)
    days: tuple[WorkoutDay, ...]
    status: WorkoutPlanStatus = WorkoutPlanStatus.ACTIVE
    generation_key: str
    version: int = Field(default=1, ge=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ExerciseProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    completed_sets: int = Field(default=0, ge=0, le=10)
    skipped: bool = False


class WorkoutProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    completed_sets: int = Field(ge=0)
    total_sets: int = Field(ge=0)
    completed_exercises: int = Field(ge=0)
    total_exercises: int = Field(ge=0)
    completion_percentage: int = Field(ge=0, le=100)


class WorkoutSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    user_id: str
    plan_id: str
    workout_day_id: str
    scheduled_date: date
    status: WorkoutSessionStatus = WorkoutSessionStatus.IN_PROGRESS
    exercise_progress: tuple[ExerciseProgress, ...]
    progress: WorkoutProgress
    revision: int = Field(default=0, ge=0)
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class WorkoutDashboardState(BaseModel):
    model_config = ConfigDict(frozen=True)

    plan_id: str
    day_id: str
    title: str
    focus: str
    status: str
    completion_percentage: int = Field(ge=0, le=100)
    destination_route: str
    last_activity_at: datetime | None = None


class WorkoutGenerationInput(BaseModel):
    model_config = ConfigDict(frozen=True)

    assessment_result_id: str
    goal: TrainingGoal
    experience: ExperienceLevel
    location: TrainingLocation
    equipment: tuple[Equipment, ...]
    injuries: tuple[str, ...] = ()
    available_days: int = Field(ge=2, le=6)
    session_duration_minutes: int = Field(ge=30, le=90)

    @model_validator(mode="after")
    def require_equipment(self) -> "WorkoutGenerationInput":
        if not self.equipment:
            raise ValueError("At least one supported equipment option is required.")
        return self
