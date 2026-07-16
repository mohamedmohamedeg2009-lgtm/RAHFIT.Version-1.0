from collections import Counter
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.workout import ExperienceLevel
from app.users.models import UserIntelligenceSnapshot
from app.workouts.exceptions import WorkoutValidationError
from app.workouts.exercises.catalog import ExerciseCatalog
from app.workouts.exercises.models import ExerciseLocation, MovementPattern
from app.workouts.models import SectionType, WorkoutPlan, WorkoutStatus
from app.workouts.planner import WorkoutPlanner
from app.workouts.rules import (
    EXPERIENCE_LIMITS,
    MAX_CONSECUTIVE_TRAINING_DAYS,
    MAX_PROGRESSION_PERCENTAGE,
    MAX_SESSION_EXERCISES,
    MIN_COOLDOWN_MINUTES,
    MIN_SESSION_EXERCISES,
    MIN_WARMUP_MINUTES,
    RULES_VERSION,
    maximum_consecutive_days,
)


class ValidationSeverity(StrEnum):
    ERROR = "error"
    WARNING = "warning"


class WorkoutValidationStatus(StrEnum):
    VALID = "valid"
    VALID_WITH_WARNINGS = "valid_with_warnings"
    INVALID = "invalid"


class WorkoutValidationIssue(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str
    severity: ValidationSeverity
    field_path: str
    message: str


class WorkoutValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    status: WorkoutValidationStatus
    valid: bool
    errors: tuple[WorkoutValidationIssue, ...]
    warnings: tuple[WorkoutValidationIssue, ...]
    validation_codes: tuple[str, ...]
    safe_metadata: dict[str, Any]


_LEVEL = {
    ExperienceLevel.BEGINNER: 0,
    ExperienceLevel.INTERMEDIATE: 1,
    ExperienceLevel.ADVANCED: 2,
}


class WorkoutValidator:
    """Final fail-closed gate; repositories receive only valid plans from the service."""

    def validate(
        self, plan: WorkoutPlan, snapshot: UserIntelligenceSnapshot, catalog: ExerciseCatalog
    ) -> WorkoutValidationResult:
        issues: list[WorkoutValidationIssue] = []
        profile, health = snapshot.profile, snapshot.health_profile
        if profile is None or health is None:
            issues.append(
                self._error(
                    "snapshot.incomplete", "snapshot", "Profile and health profile are required."
                )
            )
            return self._result(plan, issues)

        if plan.user_id != snapshot.user_id:
            issues.append(
                self._error(
                    "owner.mismatch",
                    "user_id",
                    "Plan owner does not match the authenticated intelligence snapshot.",
                )
            )
        if plan.generation_metadata.rules_version != RULES_VERSION:
            issues.append(
                self._error("version.rules", "generation_metadata", "Rules version is invalid.")
            )
        if plan.status not in {WorkoutStatus.ACTIVE, WorkoutStatus.ARCHIVED}:
            issues.append(self._error("status.invalid", "status", "Plan status is invalid."))
        if len({day.weekday for day in plan.weekly_schedule}) != len(plan.weekly_schedule):
            issues.append(
                self._error(
                    "schedule.duplicate_day",
                    "weekly_schedule",
                    "Training weekdays must be unique.",
                )
            )
        weekdays = tuple(day.weekday for day in plan.weekly_schedule)
        if maximum_consecutive_days(weekdays) > MAX_CONSECUTIVE_TRAINING_DAYS:
            issues.append(
                self._error(
                    "schedule.consecutive_days",
                    "weekly_schedule",
                    "The schedule exceeds consecutive training-day limits.",
                )
            )

        limits = EXPERIENCE_LIMITS[profile.training.experience]
        if (
            sum(day.high_intensity for day in plan.weekly_schedule)
            > limits.maximum_high_intensity_days
        ):
            issues.append(
                self._error(
                    "schedule.high_intensity",
                    "weekly_schedule",
                    "High-intensity exposure exceeds the experience limit.",
                )
            )
        active_injuries = {item.area.lower() for item in health.injuries if item.active}
        pain_areas = {item.area.lower() for item in health.pain_areas if item.intensity > 0}
        mobility = {item.area.lower() for item in health.mobility_limitations}
        conditions = {item.name.lower() for item in health.chronic_conditions}
        locations = set(WorkoutPlanner.locations(profile.training.workout_location))
        weekly_sets = 0
        weekly_patterns: Counter[MovementPattern] = Counter()
        push_count = pull_count = 0

        for day in plan.weekly_schedule:
            self._validate_required_sections(day, issues)
            if day.estimated_duration_minutes > profile.training.session_duration_minutes:
                issues.append(
                    self._error(
                        "duration.exceeded",
                        f"day.{day.day_number}",
                        "Day duration exceeds the available session duration.",
                    )
                )
            exercises = tuple(item for section in day.sections for item in section.exercises)
            if not MIN_SESSION_EXERCISES <= len(exercises) <= MAX_SESSION_EXERCISES:
                issues.append(
                    self._error(
                        "exercise.count",
                        f"day.{day.day_number}",
                        "Session exercise count is outside the approved range.",
                    )
                )
            ids = tuple(item.exercise_id for item in exercises)
            if len(ids) != len(set(ids)):
                issues.append(
                    self._error(
                        "exercise.duplicate",
                        f"day.{day.day_number}",
                        "Exercises cannot repeat within a day.",
                    )
                )
            pattern_counts = Counter(item.movement_pattern for item in exercises)
            if any(
                count > limits.maximum_repeated_pattern_per_day
                for pattern, count in pattern_counts.items()
                if pattern not in {MovementPattern.MOBILITY}
            ):
                issues.append(
                    self._error(
                        "movement.duplicate_loading",
                        f"day.{day.day_number}",
                        "Repeated loading patterns exceed the daily limit.",
                    )
                )
            weekly_patterns.update(pattern_counts)
            push_count += pattern_counts[MovementPattern.PUSH]
            pull_count += pattern_counts[MovementPattern.PULL]
            estimated = sum(item.estimated_duration_minutes for item in exercises)
            if estimated > day.estimated_duration_minutes:
                issues.append(
                    self._error(
                        "duration.underestimated",
                        f"day.{day.day_number}",
                        "Exercise duration exceeds the declared session duration.",
                    )
                )
            for planned in exercises:
                weekly_sets += planned.prescription.sets
                self._validate_exercise(
                    planned,
                    day.day_number,
                    profile.training.available_equipment,
                    profile.training.experience,
                    locations,
                    active_injuries,
                    pain_areas,
                    mobility,
                    conditions,
                    health.requires_medical_clearance,
                    catalog,
                    issues,
                )

        required_patterns = {
            MovementPattern.HINGE,
            MovementPattern.PUSH,
            MovementPattern.PULL,
            MovementPattern.CORE,
        }
        if "shoulder" in active_injuries or "shoulder" in pain_areas:
            required_patterns -= {MovementPattern.PUSH, MovementPattern.PULL}
        if active_injuries.intersection({"lower back", "hip"}) or pain_areas.intersection(
            {"lower back", "hip"}
        ):
            required_patterns.discard(MovementPattern.HINGE)
        for required in sorted(required_patterns, key=lambda item: item.value):
            if weekly_patterns[required] == 0:
                issues.append(
                    self._error(
                        "movement.required",
                        "weekly_schedule",
                        f"Required movement pattern is missing: {required.value}.",
                    )
                )
        if abs(push_count - pull_count) > plan.training_days_per_week:
            issues.append(
                self._warning(
                    "movement.push_pull_balance",
                    "weekly_schedule",
                    "Push and pull exposure should be reviewed for balance.",
                )
            )
        if weekly_sets > limits.maximum_weekly_sets:
            issues.append(
                self._error(
                    "volume.exceeded",
                    "weekly_schedule",
                    "Weekly set volume exceeds the experience limit.",
                )
            )
        return self._result(plan, issues)

    def _validate_required_sections(self, day: Any, issues: list[WorkoutValidationIssue]) -> None:
        sections = {item.section_type: item for item in day.sections}
        for required in (SectionType.WARMUP, SectionType.MAIN, SectionType.COOLDOWN):
            if required not in sections:
                issues.append(
                    self._error(
                        "section.required",
                        f"day.{day.day_number}",
                        f"{required.value} section is required.",
                    )
                )
        warmup = sections.get(SectionType.WARMUP)
        cooldown = sections.get(SectionType.COOLDOWN)
        if warmup and warmup.estimated_duration_minutes < MIN_WARMUP_MINUTES:
            issues.append(
                self._error(
                    "warmup.duration", f"day.{day.day_number}", "Warm-up duration is too short."
                )
            )
        if cooldown and cooldown.estimated_duration_minutes < MIN_COOLDOWN_MINUTES:
            issues.append(
                self._error(
                    "cooldown.duration",
                    f"day.{day.day_number}",
                    "Cooldown duration is too short.",
                )
            )

    def _validate_exercise(
        self,
        planned: Any,
        day_number: int,
        equipment: tuple[Any, ...],
        experience: ExperienceLevel,
        locations: set[ExerciseLocation],
        active_injuries: set[str],
        pain_areas: set[str],
        mobility: set[str],
        conditions: set[str],
        clearance_restricted: bool,
        catalog: ExerciseCatalog,
        issues: list[WorkoutValidationIssue],
    ) -> None:
        source = catalog.get(planned.exercise_id)
        path = f"day.{day_number}.{planned.exercise_id}"
        if source is None:
            issues.append(
                self._error("exercise.unknown", path, "Exercise is not in the approved catalog.")
            )
            return
        required, available = set(source.equipment), set(equipment)
        equipment_ok = (
            required.issubset(available)
            if source.requires_all_equipment
            else bool(required.intersection(available))
        )
        checks = (
            (not equipment_ok, "exercise.equipment", "Required equipment is unavailable."),
            (
                not set(source.suitable_locations).intersection(locations),
                "exercise.location",
                "Exercise is unsuitable for the selected location.",
            ),
            (
                _LEVEL[source.difficulty] > _LEVEL[experience],
                "exercise.difficulty",
                "Exercise exceeds the approved experience level.",
            ),
            (
                bool(set(source.injury_exclusions).intersection(active_injuries)),
                "exercise.injury",
                "Exercise conflicts with a reported active injury.",
            ),
            (
                bool(set(source.pain_area_exclusions).intersection(pain_areas)),
                "exercise.pain",
                "Exercise conflicts with a reported pain area.",
            ),
            (
                bool(set(source.mobility_requirements).intersection(mobility)),
                "exercise.mobility",
                "Exercise exceeds an approved mobility restriction.",
            ),
            (
                bool(
                    (
                        set(source.chronic_condition_exclusions) | set(source.contraindications)
                    ).intersection(conditions)
                ),
                "exercise.condition",
                "Exercise conflicts with a declared condition restriction.",
            ),
            (
                source.requires_medical_clearance and clearance_restricted,
                "exercise.clearance",
                "Exercise requires clearance that is not currently approved.",
            ),
            (
                planned.prescription.progression_limit_percentage > MAX_PROGRESSION_PERCENTAGE,
                "progression.limit",
                "Exercise progression exceeds the approved limit.",
            ),
            (
                not 1 <= planned.prescription.sets <= 8,
                "prescription.sets",
                "Exercise sets are outside the approved range.",
            ),
            (
                not 1 <= planned.prescription.min_reps <= planned.prescription.max_reps <= 60,
                "prescription.repetitions",
                "Exercise repetitions are outside the approved range.",
            ),
            (
                not 15 <= planned.prescription.rest_seconds <= 300,
                "prescription.rest",
                "Exercise rest is outside the approved range.",
            ),
            (
                not 1 <= planned.prescription.rpe_min <= planned.prescription.rpe_max <= 10,
                "prescription.rpe",
                "Exercise exertion guidance is outside the approved range.",
            ),
        )
        for failed, code, message in checks:
            if failed:
                issues.append(self._error(code, path, message))
        for alternative_id in planned.alternatives:
            alternative = catalog.get(alternative_id)
            if alternative is None or alternative.movement_pattern != source.movement_pattern:
                issues.append(
                    self._error(
                        "exercise.alternative",
                        path,
                        "An exercise alternative is outside the approved candidate set.",
                    )
                )

    def validate_or_raise(
        self, plan: WorkoutPlan, snapshot: UserIntelligenceSnapshot, catalog: ExerciseCatalog
    ) -> None:
        self.raise_for_result(self.validate(plan, snapshot, catalog))

    @staticmethod
    def raise_for_result(result: WorkoutValidationResult) -> None:
        if not result.valid:
            raise WorkoutValidationError(tuple(item.code for item in result.errors))

    @staticmethod
    def _error(code: str, path: str, message: str) -> WorkoutValidationIssue:
        return WorkoutValidationIssue(
            code=code, severity=ValidationSeverity.ERROR, field_path=path, message=message
        )

    @staticmethod
    def _warning(code: str, path: str, message: str) -> WorkoutValidationIssue:
        return WorkoutValidationIssue(
            code=code, severity=ValidationSeverity.WARNING, field_path=path, message=message
        )

    @staticmethod
    def _result(plan: WorkoutPlan, issues: list[WorkoutValidationIssue]) -> WorkoutValidationResult:
        errors = tuple(item for item in issues if item.severity == ValidationSeverity.ERROR)
        warnings = tuple(item for item in issues if item.severity == ValidationSeverity.WARNING)
        status = (
            WorkoutValidationStatus.INVALID
            if errors
            else (
                WorkoutValidationStatus.VALID_WITH_WARNINGS
                if warnings
                else WorkoutValidationStatus.VALID
            )
        )
        return WorkoutValidationResult(
            status=status,
            valid=not errors,
            errors=errors,
            warnings=warnings,
            validation_codes=tuple(item.code for item in issues),
            safe_metadata={
                "plan_id": plan.plan_id,
                "training_days": plan.training_days_per_week,
                "catalog_version": plan.generation_metadata.catalog_version,
                "rules_version": plan.generation_metadata.rules_version,
            },
        )
