from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class AIAvailabilityStatus(StrEnum):
    DISABLED = "disabled"
    SETUP_REQUIRED = "setup_required"
    AVAILABLE = "available"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"


class AIAvailability(BaseModel):
    model_config = ConfigDict(frozen=True)

    feature_enabled: bool
    status: AIAvailabilityStatus
    provider: str | None = None
    model: str | None = None
    reason_code: str
    message: str
