from pydantic import BaseModel, ConfigDict

from app.health.models import (
    ChronicConditionRecord,
    InjuryRecord,
    MobilityLimitationRecord,
    PainAreaRecord,
    SurgeryRecord,
)


class HealthProfileUpdateRequest(BaseModel):
    """Minimum HTTP declaration; private free-text notes stay outside this contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    injuries: tuple[InjuryRecord, ...]
    chronic_conditions: tuple[ChronicConditionRecord, ...]
    pain_areas: tuple[PainAreaRecord, ...]
    mobility_limitations: tuple[MobilityLimitationRecord, ...]
    surgery_history: tuple[SurgeryRecord, ...]
