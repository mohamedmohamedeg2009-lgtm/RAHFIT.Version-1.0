from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from app.models.workout import Equipment, ExperienceLevel, TrainingGoal
from app.profile.models import AgeGroup
from app.workouts.exercises.models import CatalogExercise, ExerciseLocation, MovementPattern


class RejectionReason(StrEnum):
    EQUIPMENT_UNAVAILABLE = "equipment_unavailable"
    INJURY_CONTRAINDICATION = "injury_contraindication"
    PAIN_AREA_CONFLICT = "pain_area_conflict"
    INSUFFICIENT_MOBILITY = "insufficient_mobility"
    CHRONIC_CONDITION_CONFLICT = "chronic_condition_conflict"
    CLEARANCE_RESTRICTION = "clearance_restriction"
    EXPERIENCE_TOO_LOW = "experience_too_low"
    LOCATION_INCOMPATIBLE = "location_incompatible"
    DURATION_LIMIT = "duration_limit"
    DUPLICATE_EXERCISE = "duplicate_exercise"
    DUPLICATE_PATTERN = "duplicate_pattern"
    WEEKLY_VOLUME_LIMIT = "weekly_volume_limit"
    AGE_GROUP_RESTRICTION = "age_group_restriction"
    UNSUPPORTED_GOAL = "unsupported_goal"
    RECOVERY_CONFLICT = "recovery_conflict"


class SelectionContext(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    equipment: frozenset[Equipment]
    locations: frozenset[ExerciseLocation]
    experience: ExperienceLevel
    age_group: AgeGroup = AgeGroup.YOUNG_ADULT
    goal: TrainingGoal = TrainingGoal.GENERAL_FITNESS
    injury_areas: frozenset[str] = frozenset()
    pain_areas: frozenset[str] = frozenset()
    mobility_limitations: frozenset[str] = frozenset()
    chronic_conditions: frozenset[str] = frozenset()
    medically_cleared: bool = True
    remaining_minutes: int = Field(ge=1, le=180)
    remaining_weekly_sets: int = Field(default=100, ge=0, le=200)
    excluded_ids: frozenset[str] = frozenset()
    used_patterns: frozenset[MovementPattern] = frozenset()


class ExerciseRejection(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    exercise_id: str
    reasons: tuple[RejectionReason, ...]


class ExerciseAlternative(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    selected_exercise_id: str
    approved_alternative_ids: tuple[str, ...]


class SelectionMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    eligible_count: int = Field(ge=0)
    selected_count: int = Field(ge=0)
    rejected_count: int = Field(ge=0)
    required_patterns: tuple[MovementPattern, ...]


class SelectionResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    selected: tuple[CatalogExercise, ...]
    alternatives: tuple[ExerciseAlternative, ...]
    rejections: tuple[ExerciseRejection, ...]
    metadata: SelectionMetadata


_LEVEL = {
    ExperienceLevel.BEGINNER: 0,
    ExperienceLevel.INTERMEDIATE: 1,
    ExperienceLevel.ADVANCED: 2,
}


class ExerciseSelector:
    """Deterministic allow-list selector with privacy-safe rejection codes."""

    def select(
        self,
        exercises: tuple[CatalogExercise, ...],
        context: SelectionContext,
        patterns: tuple[MovementPattern, ...],
    ) -> SelectionResult:
        eligible: list[CatalogExercise] = []
        rejected: list[ExerciseRejection] = []
        for exercise in sorted(exercises, key=self._rank):
            reasons = self._reasons(exercise, context)
            if reasons:
                rejected.append(ExerciseRejection(exercise_id=exercise.id, reasons=reasons))
            else:
                eligible.append(exercise)

        selected: list[CatalogExercise] = []
        for pattern in patterns:
            match = next(
                (
                    item
                    for item in eligible
                    if item.movement_pattern == pattern
                    and item.id not in {selected_item.id for selected_item in selected}
                ),
                None,
            )
            if match is not None:
                selected.append(match)

        alternatives = tuple(
            ExerciseAlternative(
                selected_exercise_id=item.id,
                approved_alternative_ids=tuple(
                    candidate.id
                    for candidate in eligible
                    if candidate.movement_pattern == item.movement_pattern
                    and candidate.id != item.id
                )[:3],
            )
            for item in selected
        )
        return SelectionResult(
            selected=tuple(selected),
            alternatives=alternatives,
            rejections=tuple(rejected),
            metadata=SelectionMetadata(
                eligible_count=len(eligible),
                selected_count=len(selected),
                rejected_count=len(rejected),
                required_patterns=patterns,
            ),
        )

    @staticmethod
    def _rank(exercise: CatalogExercise) -> tuple[int, int, str]:
        return (_LEVEL[exercise.difficulty], exercise.estimated_duration_minutes, exercise.id)

    @staticmethod
    def _reasons(
        exercise: CatalogExercise, context: SelectionContext
    ) -> tuple[RejectionReason, ...]:
        reasons: list[RejectionReason] = []
        available = set(context.equipment)
        required = set(exercise.equipment)
        equipment_ok = (
            required.issubset(available)
            if exercise.requires_all_equipment
            else bool(required.intersection(available))
        )
        if not equipment_ok:
            reasons.append(RejectionReason.EQUIPMENT_UNAVAILABLE)
        if not set(exercise.suitable_locations).intersection(context.locations):
            reasons.append(RejectionReason.LOCATION_INCOMPATIBLE)
        if _LEVEL[exercise.difficulty] > _LEVEL[context.experience]:
            reasons.append(RejectionReason.EXPERIENCE_TOO_LOW)
        if (
            context.age_group == AgeGroup.ADOLESCENT
            and exercise.difficulty == ExperienceLevel.ADVANCED
        ):
            reasons.append(RejectionReason.AGE_GROUP_RESTRICTION)
        if set(exercise.injury_exclusions).intersection(context.injury_areas):
            reasons.append(RejectionReason.INJURY_CONTRAINDICATION)
        if set(exercise.pain_area_exclusions).intersection(context.pain_areas):
            reasons.append(RejectionReason.PAIN_AREA_CONFLICT)
        if set(exercise.mobility_requirements).intersection(context.mobility_limitations):
            reasons.append(RejectionReason.INSUFFICIENT_MOBILITY)
        chronic_exclusions = set(exercise.chronic_condition_exclusions) | set(
            exercise.contraindications
        )
        if chronic_exclusions.intersection(context.chronic_conditions):
            reasons.append(RejectionReason.CHRONIC_CONDITION_CONFLICT)
        if exercise.requires_medical_clearance and not context.medically_cleared:
            reasons.append(RejectionReason.CLEARANCE_RESTRICTION)
        if exercise.estimated_duration_minutes > context.remaining_minutes:
            reasons.append(RejectionReason.DURATION_LIMIT)
        if exercise.default_sets > context.remaining_weekly_sets:
            reasons.append(RejectionReason.WEEKLY_VOLUME_LIMIT)
        if exercise.id in context.excluded_ids:
            reasons.append(RejectionReason.DUPLICATE_EXERCISE)
        if exercise.movement_pattern in context.used_patterns:
            reasons.append(RejectionReason.DUPLICATE_PATTERN)
        return tuple(reasons)
