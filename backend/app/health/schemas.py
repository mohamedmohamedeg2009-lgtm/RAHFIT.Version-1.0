from pydantic import BaseModel, ConfigDict

from app.health.models import (
    ChronicConditionRecord,
    HealthProfile,
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


class HealthProfileReadResponse(HealthProfileUpdateRequest):
    """Client-safe health projection that deliberately excludes private notes."""

    @classmethod
    def from_domain(cls, profile: HealthProfile) -> "HealthProfileReadResponse":
        return cls(
            injuries=profile.injuries,
            chronic_conditions=profile.chronic_conditions,
            pain_areas=profile.pain_areas,
            mobility_limitations=profile.mobility_limitations,
            surgery_history=profile.surgery_history,
        )
