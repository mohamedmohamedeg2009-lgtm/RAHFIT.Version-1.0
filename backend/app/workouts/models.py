from datetime import UTC, datetime
from enum import StrEnum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from app.models.workout import (
    Equipment,
    ExperienceLevel,
    MuscleGroup,
    TrainingGoal,
    TrainingLocation,
)
from app.readiness.models import ReadinessStatus
from app.workouts.exercises.models import MovementPattern


class WorkoutPlanType(StrEnum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    GENERAL_FITNESS = "general_fitness"
    STRENGTH = "strength"
    FOOTBALL_PERFORMANCE = "football_performance"
    GOALKEEPER_PERFORMANCE = "goalkeeper_performance"
    HOME_WORKOUT = "home_workout"
    BEGINNER_FOUNDATION = "beginner_foundation"


class WorkoutStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"


class SectionType(StrEnum):
    WARMUP = "warmup"
    MAIN = "main"
    ACCESSORY = "accessory"
    CONDITIONING = "conditioning"
    COOLDOWN = "cooldown"


class GenerationMode(StrEnum):
    DETERMINISTIC = "deterministic"
    AI_ASSISTED = "ai_assisted"
    DETERMINISTIC_FALLBACK = "deterministic_fallback"


class SetPrescription(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sets: int = Field(ge=1, le=8)
    min_reps: int = Field(ge=1, le=60)
    max_reps: int = Field(ge=1, le=60)
    rest_seconds: int = Field(ge=15, le=300)
    tempo: str = Field(default="controlled", min_length=1, max_length=40)
    intensity_guidance: str = Field(default="Leave repetitions in reserve.", max_length=200)
    rpe_min: int = Field(default=5, ge=1, le=10)
    rpe_max: int = Field(default=7, ge=1, le=10)
    reps_in_reserve: int = Field(default=3, ge=0, le=5)
    duration_seconds: int | None = Field(default=None, ge=10, le=3600)
    distance_meters: int | None = Field(default=None, ge=10, le=50_000)
    progression_limit_percentage: float = Field(default=5.0, ge=0, le=10)

    @model_validator(mode="after")
    def validate_ranges(self) -> "SetPrescription":
        if self.min_reps > self.max_reps:
            raise ValueError("Repetition range must be ordered.")
        if self.rpe_min > self.rpe_max:
            raise ValueError("RPE range must be ordered.")
        if self.duration_seconds is not None and self.distance_meters is not None:
            raise ValueError("Use either duration or distance, not both.")
        return self


class PlannedExercise(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    exercise_id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    exercise_name: str = Field(min_length=2, max_length=100)
    movement_pattern: MovementPattern
    primary_muscles: tuple[MuscleGroup, ...] = Field(min_length=1)
    equipment: tuple[Equipment, ...] = Field(min_length=1)
    prescription: SetPrescription
    estimated_duration_minutes: int = Field(ge=1, le=30)
    alternatives: tuple[str, ...] = ()
    instructions: tuple[str, ...] = Field(min_length=1)
    safety_notes: tuple[str, ...] = Field(min_length=1)

    @property
    def name(self) -> str:
        return self.exercise_name


class WorkoutSection(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    section_type: SectionType
    exercises: tuple[PlannedExercise, ...] = Field(min_length=1)

    @property
    def estimated_duration_minutes(self) -> int:
        return sum(item.estimated_duration_minutes for item in self.exercises)


class WorkoutWarning(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    message: str = Field(min_length=1, max_length=500)
    professional_guidance: bool = False


class IntelligentWorkoutDay(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    day_number: int = Field(ge=1, le=7)
    weekday: int = Field(ge=1, le=7)
    title: str = Field(min_length=2, max_length=100)
    focus: str = Field(min_length=2, max_length=100)
    estimated_duration_minutes: int = Field(ge=15, le=120)
    sections: tuple[WorkoutSection, ...] = Field(min_length=3, max_length=5)
    recovery_notes: tuple[str, ...] = Field(min_length=1)
    warnings: tuple[WorkoutWarning, ...] = ()
    high_intensity: bool = False

    def section(self, section_type: SectionType) -> WorkoutSection | None:
        return next((item for item in self.sections if item.section_type == section_type), None)

    @model_validator(mode="after")
    def unique_sections(self) -> "IntelligentWorkoutDay":
        types = tuple(item.section_type for item in self.sections)
        if len(types) != len(set(types)):
            raise ValueError("Workout day sections must be unique.")
        return self


# Internal compatibility alias. The distinct class name keeps the public OpenAPI
# component stable and separate from the legacy workout contract.
WorkoutDay = IntelligentWorkoutDay


class WorkoutExplanation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    summary: str = Field(min_length=1, max_length=1000)
    rationale: tuple[str, ...] = Field(min_length=1, max_length=8)
    motivation: str = Field(min_length=1, max_length=500)
    recovery_reminder: str = Field(
        default="Keep recovery consistent and stop if unusual symptoms occur.",
        min_length=1,
        max_length=500,
    )


class WorkoutGenerationMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: GenerationMode
    catalog_version: int = Field(ge=1)
    rules_version: int = Field(ge=1)
    readiness_status: ReadinessStatus
    generation_key: str = Field(min_length=16, max_length=128)
    selected_exercise_count: int = Field(default=0, ge=0, le=100)
    rejected_by_reason: dict[str, int] = Field(default_factory=dict)
    validation_codes: tuple[str, ...] = ()
    fallback_reason: str | None = Field(default=None, max_length=120)
    provider: str | None = Field(default=None, max_length=80)
    model: str | None = Field(default=None, max_length=120)


class WorkoutPlan(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    plan_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=256)
    primary_goal: TrainingGoal
    secondary_goal: TrainingGoal | None = None
    plan_type: WorkoutPlanType
    experience_level: ExperienceLevel
    location: TrainingLocation
    equipment: tuple[Equipment, ...] = Field(min_length=1)
    duration_weeks: int = Field(ge=4, le=12)
    training_days_per_week: int = Field(ge=1, le=6)
    weekly_schedule: tuple[WorkoutDay, ...]
    warnings: tuple[WorkoutWarning, ...] = ()
    safety_notes: tuple[str, ...] = Field(min_length=1)
    progression_guidance: tuple[str, ...] = Field(min_length=1)
    explanation: WorkoutExplanation
    generation_metadata: WorkoutGenerationMetadata
    status: WorkoutStatus = WorkoutStatus.ACTIVE
    version: int = Field(default=1, ge=1)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    activated_at: datetime | None = None
    archived_at: datetime | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def id(self) -> str:
        return self.plan_id

    @property
    def experience(self) -> ExperienceLevel:
        return self.experience_level

    @property
    def metadata(self) -> WorkoutGenerationMetadata:
        return self.generation_metadata

    @model_validator(mode="after")
    def validate_lifecycle_and_schedule(self) -> "WorkoutPlan":
        if len(self.weekly_schedule) != self.training_days_per_week:
            raise ValueError("Workout schedule must match weekly frequency.")
        if self.status == WorkoutStatus.ACTIVE and self.archived_at is not None:
            raise ValueError("An active plan cannot have an archive timestamp.")
        if self.status == WorkoutStatus.ARCHIVED and self.archived_at is None:
            raise ValueError("An archived plan requires an archive timestamp.")
        return self


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class CompletedSet(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    set_number: int = Field(ge=1, le=8)
    actual_reps: int | None = Field(
        default=None, ge=0, le=100, validation_alias=AliasChoices("actual_reps", "reps")
    )
    actual_load_kg: float | None = Field(
        default=None,
        ge=0,
        le=1000,
        validation_alias=AliasChoices("actual_load_kg", "load_kg"),
    )
    perceived_exertion: int | None = Field(default=None, ge=1, le=10)
    completed: bool


class CompletedExercise(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    exercise_id: str
    completed_sets: tuple[CompletedSet, ...] = Field(
        validation_alias=AliasChoices("completed_sets", "sets")
    )
    skipped: bool = False
    pain_reported: bool = False
    pain_area: str | None = Field(default=None, max_length=80)

    @property
    def sets(self) -> tuple[CompletedSet, ...]:
        return self.completed_sets


class WorkoutSession(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str = Field(min_length=1, max_length=128)
    user_id: str = Field(min_length=1, max_length=256)
    plan_id: str = Field(min_length=1, max_length=128)
    workout_day_id: str = Field(min_length=1, max_length=80)
    day_number: int = Field(ge=1, le=7)
    status: SessionStatus
    planned_exercise_ids: tuple[str, ...] = Field(min_length=1)
    completed_exercises: tuple[CompletedExercise, ...]
    skipped_exercise_ids: tuple[str, ...] = ()
    completion_percentage: int = Field(ge=0, le=100)
    planned_duration_minutes: int = Field(ge=15, le=120)
    actual_duration_minutes: int | None = Field(default=None, ge=1, le=300)
    notes: str | None = Field(default=None, max_length=1000)
    adaptation_flags: tuple[str, ...] = ()
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def id(self) -> str:
        return self.session_id

    @property
    def exercises(self) -> tuple[CompletedExercise, ...]:
        return self.completed_exercises


# Backward-compatible names within the new, unregistered application boundary.
SetResult = CompletedSet
ExercisePerformance = CompletedExercise
