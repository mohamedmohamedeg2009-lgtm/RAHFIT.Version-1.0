from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

HEALTH_PROFILE_SCHEMA_VERSION = 1

StrictInt = Annotated[int, Field(strict=True)]
StrictString = Annotated[str, Field(strict=True)]


class HealthSeverity(StrEnum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class InjuryRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    area: StrictString = Field(min_length=1, max_length=80)
    description: StrictString = Field(min_length=1, max_length=300)
    severity: HealthSeverity
    active: bool
    medically_cleared: bool

    @field_validator("area", "description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class ChronicConditionRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: StrictString = Field(min_length=1, max_length=120)
    controlled: bool
    medically_cleared: bool

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return " ".join(value.split())


class PainAreaRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    area: StrictString = Field(min_length=1, max_length=80)
    intensity: StrictInt = Field(ge=0, le=10)
    movement_related: bool

    @field_validator("area")
    @classmethod
    def normalize_area(cls, value: str) -> str:
        return " ".join(value.split())


class MobilityLimitationRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    area: StrictString = Field(min_length=1, max_length=80)
    description: StrictString = Field(min_length=1, max_length=300)
    severity: HealthSeverity

    @field_validator("area", "description")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return " ".join(value.split())


class SurgeryRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    procedure: StrictString = Field(min_length=1, max_length=160)
    surgery_date: date
    medically_cleared: bool

    @field_validator("procedure")
    @classmethod
    def normalize_procedure(cls, value: str) -> str:
        return " ".join(value.split())

    @model_validator(mode="after")
    def reject_future_surgery(self) -> "SurgeryRecord":
        if self.surgery_date > date.today():
            raise ValueError("Surgery date cannot be in the future.")
        return self


class HealthProfileData(BaseModel):
    """Explicit health declaration; empty tuples mean the user confirmed none."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    injuries: tuple[InjuryRecord, ...]
    chronic_conditions: tuple[ChronicConditionRecord, ...]
    pain_areas: tuple[PainAreaRecord, ...]
    mobility_limitations: tuple[MobilityLimitationRecord, ...]
    surgery_history: tuple[SurgeryRecord, ...]
    notes: StrictString | None = Field(default=None, max_length=2_000)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = " ".join(value.split())
        return normalized or None

    @model_validator(mode="after")
    def reject_duplicate_health_records(self) -> "HealthProfileData":
        groups = (
            (item.area.lower() for item in self.injuries),
            (item.name.lower() for item in self.chronic_conditions),
            (item.area.lower() for item in self.pain_areas),
            (item.area.lower() for item in self.mobility_limitations),
        )
        for values in groups:
            items = tuple(values)
            if len(items) != len(set(items)):
                raise ValueError("Health profile records cannot contain duplicate areas or names.")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def active_injury_areas(self) -> tuple[str, ...]:
        return tuple(item.area for item in self.injuries if item.active)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def requires_medical_clearance(self) -> bool:
        unsafe_injury = any(item.active and not item.medically_cleared for item in self.injuries)
        unsafe_condition = any(
            not item.controlled or not item.medically_cleared for item in self.chronic_conditions
        )
        unsafe_surgery = any(not item.medically_cleared for item in self.surgery_history)
        return unsafe_injury or unsafe_condition or unsafe_surgery


class HealthProfile(HealthProfileData):
    id: str
    user_id: str = Field(min_length=1, max_length=256)
    schema_version: int = Field(default=HEALTH_PROFILE_SCHEMA_VERSION, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
