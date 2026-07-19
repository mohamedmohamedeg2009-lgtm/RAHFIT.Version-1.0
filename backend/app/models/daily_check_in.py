from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

CHECK_IN_ID_PATTERN = r"^[0-9a-f]{32}$"


class HydrationStatus(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    GOOD = "good"


class ReadinessLevel(StrEnum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    RECOVERY_REQUIRED = "recovery_required"


class CheckInRecommendedAction(StrEnum):
    NORMAL_TRAINING = "normal_training"
    REDUCED_INTENSITY = "reduced_intensity"
    RECOVERY_SESSION = "recovery_session"
    REST_AND_PROFESSIONAL_GUIDANCE = "rest_and_professional_guidance"


class CheckInWarningCode(StrEnum):
    HIGH_PAIN = "high_pain"
    MODERATE_PAIN = "moderate_pain"
    SEVERE_SORENESS = "severe_soreness"
    SLEEP_DEPRIVATION = "sleep_deprivation"
    HIGH_STRESS = "high_stress"
    DEHYDRATION = "dehydration"
    LOW_ENERGY = "low_energy"
    MULTIPLE_FATIGUE_FACTORS = "multiple_fatigue_factors"


class DailyCheckInInputs(BaseModel):
    """Raw daily readiness inputs provided by user."""

    model_config = ConfigDict(frozen=True)

    sleep_hours: float = Field(ge=0.0, le=24.0)
    sleep_quality: int = Field(ge=1, le=5)
    energy_level: int = Field(ge=1, le=5)
    stress_level: int = Field(ge=1, le=5)
    muscle_soreness: int = Field(ge=1, le=5)
    pain_level: int = Field(ge=0, le=10)
    hydration_status: HydrationStatus
    mood: int = Field(ge=1, le=5)
    optional_note: str | None = Field(default=None, max_length=500)


class DeterministicReadinessResult(BaseModel):
    """Calculated output from the deterministic Python readiness engine."""

    model_config = ConfigDict(frozen=True)

    readiness_score: int = Field(ge=0, le=100)
    readiness_level: ReadinessLevel
    recovery_score: int = Field(ge=0, le=100)
    sleep_score: int = Field(ge=0, le=100)
    stress_score: int = Field(ge=0, le=100)
    hydration_score: int = Field(ge=0, le=100)
    pain_flag: bool
    warning_codes: tuple[CheckInWarningCode, ...]
    recommended_action: CheckInRecommendedAction


class DailyCheckIn(BaseModel):
    """User-owned daily check-in aggregate root."""

    model_config = ConfigDict(frozen=True)

    id: Annotated[str, Field(pattern=CHECK_IN_ID_PATTERN)]
    user_id: str = Field(min_length=1)
    date: date
    inputs: DailyCheckInInputs
    readiness_result: DeterministicReadinessResult
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    schema_version: int = Field(default=1, ge=1)
