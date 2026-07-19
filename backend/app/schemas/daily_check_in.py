import html
import re
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.daily_check_in import (
    DailyCheckIn,
    DailyCheckInInputs,
    HydrationStatus,
)

_UNSAFE_HTML_PATTERN = re.compile(r"<[^>]*>", re.IGNORECASE)


class DailyCheckInCreate(BaseModel):
    """Schema for submitting or updating a daily check-in."""

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
    check_in_date: date | None = Field(default=None)

    @field_validator("optional_note")
    @classmethod
    def validate_and_sanitize_note(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            return None
        if _UNSAFE_HTML_PATTERN.search(stripped):
            raise ValueError("Unsafe HTML tags are not permitted in optional note.")
        return html.escape(stripped)

    def to_inputs(self) -> DailyCheckInInputs:
        return DailyCheckInInputs(
            sleep_hours=self.sleep_hours,
            sleep_quality=self.sleep_quality,
            energy_level=self.energy_level,
            stress_level=self.stress_level,
            muscle_soreness=self.muscle_soreness,
            pain_level=self.pain_level,
            hydration_status=self.hydration_status,
            mood=self.mood,
            optional_note=self.optional_note,
        )


class DailyCheckInResponse(BaseModel):
    """API response containing the saved check-in and readiness result."""

    model_config = ConfigDict(frozen=True)

    check_in: DailyCheckIn


class DailyCheckInHistoryResponse(BaseModel):
    """Paginated list of historical daily check-ins."""

    model_config = ConfigDict(frozen=True)

    items: tuple[DailyCheckIn, ...]
    total: int = Field(ge=0)
    limit: int = Field(ge=1)
    offset: int = Field(ge=0)
    has_more: bool
