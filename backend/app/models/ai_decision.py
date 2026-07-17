from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.health.models import HealthProfile
from app.models.nutrition import NutritionProgress
from app.models.workout import WorkoutPlan
from app.profile.models import UserProfile


class DecisionStatus(StrEnum):
    APPROVED = "approved"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    NEEDS_INFO = "needs_info"


class DecisionReason(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    message_en: str
    message_ar: str


class DecisionWarning(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    message_en: str
    message_ar: str


class DecisionFinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    category: str  # e.g., "safety", "policy", "classifier"
    code: str
    message: str
    severity: str  # e.g., "critical", "warning", "info"


class DecisionMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    engine_version: str = "rahfit-ai-decision-v1"
    context_version: str = "v1"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    effective_date: date
    data_quality_score: int = Field(ge=0, le=100)
    confidence_score: int = Field(ge=0, le=100)
    missing_inputs: tuple[str, ...] = ()


class DecisionTrace(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    rule_name: str
    condition_met: bool
    action_taken: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DecisionInputSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    user_id: str
    profile: UserProfile | None = None
    health_profile: HealthProfile | None = None
    active_workout_plan: WorkoutPlan | None = None
    recent_sessions: tuple[Any, ...] = ()  # Holds recent workout sessions
    recent_nutrition_logs: tuple[NutritionProgress, ...] = ()
    input_hash: str


class DecisionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    user_id: str
    target_date: date | None = None
    force_regenerate: bool = False


class TrainingDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    action: str  # e.g., "continue_plan", "reduce_intensity", "reduce_volume", "full_rest"
    affected_exercises: tuple[str, ...] = ()
    intensity_multiplier: float = 1.0
    volume_multiplier: float = 1.0
    duration_adjustment_minutes: int = 0
    rest_seconds_adjustment: int = 0
    reason_codes: tuple[str, ...] = ()
    safety_justification: str
    confidence: int


class NutritionDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    action: str  # e.g., "keep_targets", "adjust_calories", "simplify_meals"
    calorie_adjustment: int = 0
    protein_adjustment_grams: int = 0
    hydration_adjustment_ml: int = 0
    warnings: tuple[str, ...] = ()
    reason_codes: tuple[str, ...] = ()
    explanation: str


class RecoveryDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    guidance: str  # e.g., "normal_recovery", "sleep_priority", "full_rest"
    hydration_priority: bool = False
    mobility_focus: bool = False
    stress_management_prompt: bool = False
    reassessment_required: bool = False


class InjuryDecision(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    blocked_movements: tuple[str, ...] = ()
    pain_areas_active: tuple[str, ...] = ()
    requires_medical_clearance: bool = False
    warning_message_en: str | None = None
    warning_message_ar: str | None = None


class DailyDecision(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str
    user_id: str
    effective_date: date
    status: DecisionStatus
    approved_actions: tuple[str, ...] = ()
    blocked_actions: tuple[str, ...] = ()
    modifications: tuple[str, ...] = ()
    warnings: tuple[DecisionWarning, ...] = ()
    reason_codes: tuple[DecisionReason, ...] = ()
    human_readable_explanation_en: str
    human_readable_explanation_ar: str
    training: TrainingDecision
    nutrition: NutritionDecision
    recovery: RecoveryDecision
    injury: InjuryDecision
    findings: tuple[DecisionFinding, ...] = ()
    trace: tuple[DecisionTrace, ...] = ()
    metadata: DecisionMetadata
    input_snapshot_hash: str
    superseded_by: str | None = None
    is_active: bool = True
