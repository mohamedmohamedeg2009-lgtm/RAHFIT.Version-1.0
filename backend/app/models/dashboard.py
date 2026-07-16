from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.assessment import QuestionCategory, RiskLevel, SafetyStatus
from app.models.nutrition import NutritionDashboardState
from app.models.workout import WorkoutDashboardState


class DashboardAssessmentStatus(StrEnum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    UNAVAILABLE = "unavailable"


class DashboardActionType(StrEnum):
    START_ASSESSMENT = "start_assessment"
    RESUME_ASSESSMENT = "resume_assessment"
    REVIEW_SAFETY = "review_safety_warning"
    COMPLETE_PROFILE = "complete_missing_profile_information"
    VIEW_ASSESSMENT = "view_assessment_summary"
    CONTINUE_AVAILABLE = "continue_available_feature"
    GENERATE_WORKOUT = "generate_workout"
    START_WORKOUT = "start_workout"
    CONTINUE_WORKOUT = "continue_workout"
    LOG_OUT = "log_out"


class DashboardSeverity(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"


class FeatureStatus(StrEnum):
    AVAILABLE = "available"
    LOCKED = "locked"
    COMING_SOON = "coming_soon"
    ACTION_REQUIRED = "action_required"


class DashboardFreshness(StrEnum):
    LIVE = "live"
    PARTIAL = "partial"


class DashboardUserSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    display_name: str
    primary_goal: str | None = None
    preferred_units: str
    assessment_status: DashboardAssessmentStatus
    profile_completeness: int = Field(ge=0, le=100)
    missing_profile_fields: tuple[str, ...] = ()


class DashboardAssessmentSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: DashboardAssessmentStatus
    session_id: str | None = None
    completion_percentage: int = Field(ge=0, le=100)
    readiness_score: int | None = Field(default=None, ge=0, le=100)
    risk_level: RiskLevel | None = None
    safety_status: SafetyStatus | None = None
    missing_categories: tuple[QuestionCategory, ...] = ()
    latest_completion_date: datetime | None = None
    reassessment_recommended: bool = False


class DashboardAction(BaseModel):
    model_config = ConfigDict(frozen=True)

    action_type: DashboardActionType
    title: str
    description: str
    destination_route: str | None = None
    priority_reason: str
    severity: DashboardSeverity


class DashboardFeature(BaseModel):
    model_config = ConfigDict(frozen=True)

    key: str
    title: str
    status: FeatureStatus
    reason: str
    destination_route: str | None = None


class DashboardSafetyNotice(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: SafetyStatus
    title: str
    message: str
    severity: DashboardSeverity
    plan_generation_blocked: bool


class DashboardProgressSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True)

    assessment_completion: int = Field(ge=0, le=100)
    profile_completeness: int = Field(ge=0, le=100)
    latest_readiness_score: int | None = Field(default=None, ge=0, le=100)
    last_activity_date: datetime | None = None


class DashboardMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    generated_at: datetime
    data_freshness: DashboardFreshness
    partial_data: bool
    dashboard_version: str


class DashboardView(BaseModel):
    model_config = ConfigDict(frozen=True)

    user: DashboardUserSummary
    assessment: DashboardAssessmentSummary
    workout: WorkoutDashboardState | None = None
    nutrition: NutritionDashboardState | None = None
    daily_priority: DashboardAction
    features: tuple[DashboardFeature, ...]
    safety_notice: DashboardSafetyNotice | None = None
    progress: DashboardProgressSnapshot
    quick_actions: tuple[DashboardAction, ...]
    metadata: DashboardMetadata
