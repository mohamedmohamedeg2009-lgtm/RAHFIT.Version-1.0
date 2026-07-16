from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReadinessStatus(StrEnum):
    READY = "ready"
    CAUTION = "caution"
    NEEDS_INFORMATION = "needs_information"
    BLOCKED = "blocked"


class ReadinessSeverity(StrEnum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ReadinessIssue(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(pattern=r"^[a-z][a-z0-9_.]*$")
    severity: ReadinessSeverity
    field_path: str
    message: str
    requires_professional_guidance: bool = False


class ReadinessResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: ReadinessStatus
    ready_for_ai: bool
    completeness_score: int = Field(ge=0, le=100)
    missing_fields: tuple[str, ...]
    issues: tuple[ReadinessIssue, ...]
    checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @model_validator(mode="after")
    def validate_status(self) -> "ReadinessResult":
        is_ready_status = self.status in {ReadinessStatus.READY, ReadinessStatus.CAUTION}
        if self.ready_for_ai != is_ready_status:
            raise ValueError("AI readiness must match the structured status.")
        if self.missing_fields and self.completeness_score == 100:
            raise ValueError("Complete readiness cannot contain missing fields.")
        return self
