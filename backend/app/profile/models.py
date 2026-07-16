from datetime import UTC, date, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator

from app.models.nutrition import ActivityLevel, Allergy, DietaryPreference
from app.models.workout import Equipment, ExperienceLevel, TrainingGoal, TrainingLocation

PROFILE_SCHEMA_VERSION = 1

StrictInt = Annotated[int, Field(strict=True)]
StrictFloat = Annotated[float, Field(strict=True)]
StrictString = Annotated[str, Field(strict=True)]


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class AgeGroup(StrEnum):
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young_adult"
    MIDDLE_ADULT = "middle_adult"
    OLDER_ADULT = "older_adult"


class IdentityProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    full_name: StrictString = Field(min_length=2, max_length=120)
    age: StrictInt = Field(ge=13, le=100)
    gender: Gender
    country: StrictString = Field(pattern=r"^[A-Z]{2}$")

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Full name must contain at least two visible characters.")
        return normalized

    @field_validator("country", mode="before")
    @classmethod
    def normalize_country(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value


class BodyProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    height_cm: StrictFloat = Field(ge=100, le=250)
    weight_kg: StrictFloat = Field(ge=30, le=350)
    body_fat_percentage: StrictFloat | None = Field(default=None, ge=2, le=70)


class GoalsProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    primary_goal: TrainingGoal
    secondary_goal: TrainingGoal | None = None
    target_weight_kg: StrictFloat | None = Field(default=None, ge=30, le=350)
    target_date: date | None = None

    @model_validator(mode="after")
    def require_distinct_goals(self) -> "GoalsProfile":
        if self.secondary_goal == self.primary_goal:
            raise ValueError("Primary and secondary goals must be different.")
        if (self.target_weight_kg is None) != (self.target_date is None):
            raise ValueError("Target weight and target date must be provided together.")
        return self


class TrainingProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    experience: ExperienceLevel
    available_days: StrictInt = Field(ge=1, le=7)
    session_duration_minutes: StrictInt = Field(ge=15, le=180)
    available_equipment: tuple[Equipment, ...] = Field(min_length=1, max_length=20)
    workout_location: TrainingLocation

    @field_validator("available_equipment")
    @classmethod
    def unique_equipment(cls, value: tuple[Equipment, ...]) -> tuple[Equipment, ...]:
        if len(value) != len(set(value)):
            raise ValueError("Available equipment cannot contain duplicates.")
        return value


class LifestyleProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    sleep_hours: StrictFloat = Field(ge=0, le=24)
    stress_level: StrictInt = Field(ge=1, le=10)
    activity_level: ActivityLevel
    daily_water_ml: StrictInt = Field(ge=0, le=10_000)


class NutritionProfile(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dietary_preferences: tuple[DietaryPreference, ...]
    allergies: tuple[Allergy, ...]
    dietary_restrictions: tuple[StrictString, ...]

    @field_validator("dietary_preferences", "allergies")
    @classmethod
    def unique_enums(cls, value: tuple[object, ...]) -> tuple[object, ...]:
        if len(value) != len(set(value)):
            raise ValueError("Values cannot contain duplicates.")
        return value

    @field_validator("dietary_restrictions")
    @classmethod
    def normalize_restrictions(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        normalized = tuple(" ".join(item.split()).lower() for item in value)
        if any(not item or len(item) > 80 for item in normalized):
            raise ValueError("Dietary restrictions must contain 1 to 80 visible characters.")
        if len(normalized) != len(set(normalized)):
            raise ValueError("Dietary restrictions cannot contain duplicates.")
        return normalized


class UserProfileData(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    identity: IdentityProfile
    body: BodyProfile
    goals: GoalsProfile
    training: TrainingProfile
    lifestyle: LifestyleProfile
    nutrition: NutritionProfile

    @computed_field  # type: ignore[prop-decorator]
    @property
    def bmi(self) -> float:
        height_m = self.body.height_cm / 100
        return round(self.body.weight_kg / (height_m * height_m), 2)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def bmr_kcal(self) -> int:
        gender_adjustment = {
            Gender.MALE: 5.0,
            Gender.FEMALE: -161.0,
            Gender.NON_BINARY: -78.0,
            Gender.PREFER_NOT_TO_SAY: -78.0,
        }[self.identity.gender]
        estimate = (
            10 * self.body.weight_kg
            + 6.25 * self.body.height_cm
            - 5 * self.identity.age
            + gender_adjustment
        )
        return round(estimate)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def age_group(self) -> AgeGroup:
        if self.identity.age < 18:
            return AgeGroup.ADOLESCENT
        if self.identity.age < 40:
            return AgeGroup.YOUNG_ADULT
        if self.identity.age < 60:
            return AgeGroup.MIDDLE_ADULT
        return AgeGroup.OLDER_ADULT


class UserProfile(UserProfileData):
    id: str
    user_id: str = Field(min_length=1, max_length=256)
    schema_version: int = Field(default=PROFILE_SCHEMA_VERSION, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
