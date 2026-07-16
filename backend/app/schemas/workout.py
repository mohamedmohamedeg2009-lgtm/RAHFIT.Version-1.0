from pydantic import BaseModel, Field

from app.models.workout import WorkoutDay, WorkoutPlan, WorkoutSession


class GenerateWorkoutRequest(BaseModel):
    available_days: int | None = Field(default=None, ge=2, le=6)
    session_duration_minutes: int | None = Field(default=None, ge=30, le=90)


class UpdateExerciseRequest(BaseModel):
    completed_sets: int = Field(ge=0, le=10)
    skipped: bool = False


class CurrentWorkoutResponse(BaseModel):
    plan: WorkoutPlan
    today: WorkoutDay
    session: WorkoutSession | None = None


class WorkoutHistoryResponse(BaseModel):
    plans: tuple[WorkoutPlan, ...]
    completed_sessions: int = Field(ge=0)
    weekly_adherence_percentage: int = Field(ge=0, le=100)
