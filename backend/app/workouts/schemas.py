from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.workouts.adaptation import AdaptationAction, AdaptationSeverity
from app.workouts.models import (
    CompletedExercise,
    GenerationMode,
    SessionStatus,
    WorkoutDay,
    WorkoutExplanation,
    WorkoutPlan,
    WorkoutPlanType,
    WorkoutSession,
    WorkoutStatus,
    WorkoutWarning,
)


class WorkoutGenerationRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={"examples": [{"duration_weeks": 8, "use_ai_assistance": False}]},
    )

    duration_weeks: int = Field(default=8, ge=4, le=12)
    use_ai_assistance: bool = False


class AIWorkoutEnhancement(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    approved_exercise_ids: tuple[str, ...] = Field(min_length=1)
    explanation: WorkoutExplanation


class WorkoutPlanResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    plan_id: str
    plan_type: WorkoutPlanType
    status: WorkoutStatus
    duration_weeks: int
    training_days_per_week: int
    weekly_schedule: tuple[WorkoutDay, ...]
    warnings: tuple[WorkoutWarning, ...]
    safety_notes: tuple[str, ...]
    progression_guidance: tuple[str, ...]
    explanation: WorkoutExplanation
    generation_mode: GenerationMode
    generated_at: datetime
    activated_at: datetime | None
    archived_at: datetime | None
    version: int

    @property
    def id(self) -> str:
        return self.plan_id

    @classmethod
    def from_domain(cls, plan: WorkoutPlan) -> "WorkoutPlanResponse":
        return cls(
            plan_id=plan.plan_id,
            plan_type=plan.plan_type,
            status=plan.status,
            duration_weeks=plan.duration_weeks,
            training_days_per_week=plan.training_days_per_week,
            weekly_schedule=plan.weekly_schedule,
            warnings=plan.warnings,
            safety_notes=plan.safety_notes,
            progression_guidance=plan.progression_guidance,
            explanation=plan.explanation,
            generation_mode=plan.generation_metadata.mode,
            generated_at=plan.generated_at,
            activated_at=plan.activated_at,
            archived_at=plan.archived_at,
            version=plan.version,
        )


class RecordWorkoutSessionRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "plan_id": "plan-identifier",
                    "day_number": 1,
                    "status": "in_progress",
                    "completed_exercises": [],
                }
            ]
        },
    )

    plan_id: str
    day_number: int = Field(ge=1, le=7)
    status: SessionStatus
    completed_exercises: tuple[CompletedExercise, ...]
    actual_duration_minutes: int | None = Field(default=None, ge=1, le=300)
    notes: str | None = Field(default=None, max_length=1000)


class UpdateWorkoutSessionRequest(BaseModel):
    """A full progress snapshot for the mutable fields of an owned session."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={
            "examples": [
                {
                    "status": "in_progress",
                    "completed_exercises": [
                        {
                            "exercise_id": "approved_exercise_id",
                            "completed_sets": [
                                {"set_number": 1, "actual_reps": 8, "completed": True}
                            ],
                            "skipped": False,
                            "pain_reported": False,
                        }
                    ],
                    "actual_duration_minutes": 30,
                }
            ]
        },
    )

    status: SessionStatus | None = None
    completed_exercises: tuple[CompletedExercise, ...] | None = None
    actual_duration_minutes: int | None = Field(default=None, ge=1, le=300)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def require_update(self) -> "UpdateWorkoutSessionRequest":
        if not self.model_fields_set:
            raise ValueError("At least one session field must be supplied.")
        return self


class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str
    plan_id: str
    workout_day_id: str
    day_number: int
    status: SessionStatus
    completion_percentage: int
    completed_exercises: tuple[CompletedExercise, ...]
    skipped_exercise_ids: tuple[str, ...]
    adaptation_flags: tuple[str, ...]
    planned_duration_minutes: int
    actual_duration_minutes: int | None
    started_at: datetime
    completed_at: datetime | None
    updated_at: datetime

    @property
    def id(self) -> str:
        return self.session_id

    @classmethod
    def from_domain(cls, session: WorkoutSession) -> "WorkoutSessionResponse":
        return cls(
            session_id=session.session_id,
            plan_id=session.plan_id,
            workout_day_id=session.workout_day_id,
            day_number=session.day_number,
            status=session.status,
            completion_percentage=session.completion_percentage,
            completed_exercises=session.completed_exercises,
            skipped_exercise_ids=session.skipped_exercise_ids,
            adaptation_flags=session.adaptation_flags,
            planned_duration_minutes=session.planned_duration_minutes,
            actual_duration_minutes=session.actual_duration_minutes,
            started_at=session.started_at,
            completed_at=session.completed_at,
            updated_at=session.updated_at,
        )


class WorkoutAdaptationResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    recommendation_code: str
    action: AdaptationAction
    reason_code: str
    severity: AdaptationSeverity
    evidence_summary: tuple[str, ...]
    automatic_application_allowed: bool
    affected_exercise_id: str | None
    affected_day_number: int | None


class WorkoutAdaptationRequest(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        json_schema_extra={"examples": [{"plan_id": "plan-identifier"}]},
    )

    plan_id: str = Field(min_length=1, max_length=128)


class WorkoutPlanListResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    items: tuple[WorkoutPlanResponse, ...]
    limit: int
    offset: int
    has_more: bool


class WorkoutSessionListResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    items: tuple[WorkoutSessionResponse, ...]
    limit: int
    offset: int
    has_more: bool


class WorkoutArchiveResponse(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    plan_id: str
    status: WorkoutStatus = WorkoutStatus.ARCHIVED
