from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.workout import Equipment, ExperienceLevel, MuscleGroup


class ExerciseCategory(StrEnum):
    STRENGTH = "strength"
    POWER = "power"
    CARDIO = "cardio"
    MOBILITY = "mobility"
    WARMUP = "warmup"
    COOLDOWN = "cooldown"


class MovementPattern(StrEnum):
    SQUAT = "squat"
    HINGE = "hinge"
    PUSH = "push"
    PULL = "pull"
    LUNGE = "lunge"
    CARRY = "carry"
    CORE = "core"
    ROTATION = "rotation"
    LOCOMOTION = "locomotion"
    MOBILITY = "mobility"
    CONDITIONING = "conditioning"


class ExerciseLocation(StrEnum):
    HOME = "home"
    GYM = "gym"
    OUTDOOR = "outdoor"


class CatalogExercise(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2, max_length=100)
    category: ExerciseCategory
    movement_pattern: MovementPattern
    primary_muscles: tuple[MuscleGroup, ...] = Field(min_length=1)
    secondary_muscles: tuple[MuscleGroup, ...] = ()
    equipment: tuple[Equipment, ...] = Field(min_length=1)
    requires_all_equipment: bool = False
    suitable_locations: tuple[ExerciseLocation, ...] = Field(min_length=1)
    difficulty: ExperienceLevel
    contraindications: tuple[str, ...] = ()
    injury_exclusions: tuple[str, ...] = ()
    pain_area_exclusions: tuple[str, ...] = ()
    mobility_requirements: tuple[str, ...] = ()
    chronic_condition_exclusions: tuple[str, ...] = ()
    requires_medical_clearance: bool = False
    default_rep_range: tuple[int, int] = (8, 12)
    default_sets: int = Field(default=3, ge=1, le=6)
    default_rest_seconds: int = Field(default=60, ge=15, le=300)
    estimated_duration_minutes: int = Field(default=5, ge=1, le=20)
    instructions: tuple[str, ...] = Field(min_length=1)
    safety_notes: tuple[str, ...] = Field(min_length=1)
    active: bool = True
    version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def validate_ranges(self) -> "CatalogExercise":
        if self.default_rep_range[0] < 1 or self.default_rep_range[0] > self.default_rep_range[1]:
            raise ValueError("Exercise repetition range must be ordered.")
        if len(self.equipment) != len(set(self.equipment)):
            raise ValueError("Exercise equipment must be unique.")
        normalized_groups = (
            self.contraindications,
            self.injury_exclusions,
            self.pain_area_exclusions,
            self.mobility_requirements,
            self.chronic_condition_exclusions,
        )
        if any(len(group) != len(set(group)) for group in normalized_groups):
            raise ValueError("Exercise safety metadata cannot contain duplicates.")
        return self
