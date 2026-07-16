from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta

from app.health.models import HealthProfile, HealthSeverity
from app.models.nutrition import ActivityLevel
from app.models.workout import ExperienceLevel, TrainingGoal
from app.profile.models import UserProfile
from app.readiness.models import (
    ReadinessIssue,
    ReadinessResult,
    ReadinessSeverity,
    ReadinessStatus,
)
from app.users.models import UserIntelligenceSnapshot

_REQUIRED_PROFILE_FIELDS = (
    "profile.identity.full_name",
    "profile.identity.age",
    "profile.identity.gender",
    "profile.identity.country",
    "profile.body.height_cm",
    "profile.body.weight_kg",
    "profile.goals.primary_goal",
    "profile.training.experience",
    "profile.training.available_days",
    "profile.training.session_duration_minutes",
    "profile.training.available_equipment",
    "profile.training.workout_location",
    "profile.lifestyle.sleep_hours",
    "profile.lifestyle.stress_level",
    "profile.lifestyle.activity_level",
    "profile.lifestyle.daily_water_ml",
    "profile.nutrition.dietary_preferences",
    "profile.nutrition.allergies",
    "profile.nutrition.dietary_restrictions",
)
_REQUIRED_HEALTH_FIELDS = (
    "health_profile.injuries",
    "health_profile.chronic_conditions",
    "health_profile.pain_areas",
    "health_profile.mobility_limitations",
    "health_profile.surgery_history",
)
_ALL_REQUIRED_FIELDS = _REQUIRED_PROFILE_FIELDS + _REQUIRED_HEALTH_FIELDS
_RECENT_SURGERY_WINDOW = timedelta(weeks=12)


class ReadinessChecker:
    """Deterministic pre-generation validation for canonical user intelligence."""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.clock = clock or (lambda: datetime.now(UTC))

    def check(self, snapshot: UserIntelligenceSnapshot) -> ReadinessResult:
        checked_at = self.clock()
        missing = self._missing_fields(snapshot)
        issues: list[ReadinessIssue] = []
        if snapshot.profile is not None:
            issues.extend(self._profile_issues(snapshot.profile, checked_at.date()))
        if snapshot.health_profile is not None:
            issues.extend(self._health_issues(snapshot.health_profile, checked_at.date()))
        status = self._status(missing, issues)
        completeness = round(
            100 * (len(_ALL_REQUIRED_FIELDS) - len(missing)) / len(_ALL_REQUIRED_FIELDS)
        )
        return ReadinessResult(
            status=status,
            ready_for_ai=status in {ReadinessStatus.READY, ReadinessStatus.CAUTION},
            completeness_score=completeness,
            missing_fields=missing,
            issues=tuple(issues),
            checked_at=checked_at,
        )

    @staticmethod
    def _missing_fields(snapshot: UserIntelligenceSnapshot) -> tuple[str, ...]:
        missing: list[str] = []
        if snapshot.profile is None:
            missing.extend(_REQUIRED_PROFILE_FIELDS)
        elif (
            snapshot.profile.goals.target_weight_kg is not None
            and snapshot.profile.goals.target_date is None
        ):
            missing.append("profile.goals.target_date")
        if snapshot.health_profile is None:
            missing.extend(_REQUIRED_HEALTH_FIELDS)
        return tuple(missing)

    def _profile_issues(self, profile: UserProfile, today: date) -> list[ReadinessIssue]:
        issues: list[ReadinessIssue] = []
        goals = profile.goals
        current_weight = profile.body.weight_kg
        target_weight = goals.target_weight_kg
        if target_weight is not None:
            if goals.primary_goal == TrainingGoal.FAT_LOSS and target_weight >= current_weight:
                issues.append(
                    self._issue(
                        "goal.fat_loss_target_direction",
                        ReadinessSeverity.ERROR,
                        "profile.goals.target_weight_kg",
                        "A fat-loss target must be below the current weight.",
                    )
                )
            if goals.primary_goal == TrainingGoal.MUSCLE_GAIN and target_weight <= current_weight:
                issues.append(
                    self._issue(
                        "goal.muscle_gain_target_direction",
                        ReadinessSeverity.ERROR,
                        "profile.goals.target_weight_kg",
                        "A muscle-gain target must be above the current weight.",
                    )
                )
            if goals.target_date is not None:
                issues.extend(
                    self._target_rate_issues(
                        profile,
                        current_weight,
                        target_weight,
                        goals.target_date,
                        today,
                    )
                )
        if profile.bmi < 15 or profile.bmi > 45:
            issues.append(
                self._issue(
                    "body.extreme_bmi",
                    ReadinessSeverity.CRITICAL,
                    "profile.bmi",
                    "The computed BMI requires professional review before personalization.",
                    guidance=True,
                )
            )
        body_fat = profile.body.body_fat_percentage
        if body_fat is not None and (body_fat < 3 or body_fat > 60):
            issues.append(
                self._issue(
                    "body.extreme_body_fat",
                    ReadinessSeverity.CRITICAL,
                    "profile.body.body_fat_percentage",
                    "The body-fat value requires professional verification.",
                    guidance=True,
                )
            )
        lifestyle = profile.lifestyle
        high_activity = lifestyle.activity_level in {
            ActivityLevel.VERY_ACTIVE,
            ActivityLevel.EXTRA_ACTIVE,
        }
        if lifestyle.sleep_hours < 4 and lifestyle.stress_level >= 8 and high_activity:
            issues.append(
                self._issue(
                    "lifestyle.recovery_risk",
                    ReadinessSeverity.CRITICAL,
                    "profile.lifestyle",
                    "Very low sleep, high stress, and high activity create a recovery risk.",
                    guidance=True,
                )
            )
        elif lifestyle.sleep_hours < 5:
            issues.append(
                self._issue(
                    "lifestyle.low_sleep",
                    ReadinessSeverity.WARNING,
                    "profile.lifestyle.sleep_hours",
                    "Low sleep should limit training intensity and recovery expectations.",
                )
            )
        if profile.training.available_days == 7:
            issues.append(
                self._issue(
                    "training.no_rest_day",
                    ReadinessSeverity.WARNING,
                    "profile.training.available_days",
                    "Seven available training days still require planned recovery.",
                )
            )
        if profile.identity.age < 16 and profile.training.experience == ExperienceLevel.ADVANCED:
            issues.append(
                self._issue(
                    "training.minor_advanced_programming",
                    ReadinessSeverity.WARNING,
                    "profile.training.experience",
                    "Advanced programming for a young user requires conservative supervision.",
                    guidance=True,
                )
            )
        if lifestyle.daily_water_ml < 500:
            issues.append(
                self._issue(
                    "lifestyle.very_low_hydration",
                    ReadinessSeverity.WARNING,
                    "profile.lifestyle.daily_water_ml",
                    "Reported daily water intake is unusually low.",
                )
            )
        return issues

    def _target_rate_issues(
        self,
        profile: UserProfile,
        current_weight: float,
        target_weight: float,
        target_date: date,
        today: date,
    ) -> list[ReadinessIssue]:
        if target_date <= today:
            return [
                self._issue(
                    "goal.target_date_not_future",
                    ReadinessSeverity.ERROR,
                    "profile.goals.target_date",
                    "Target date must be in the future.",
                )
            ]
        weeks = max((target_date - today).days / 7, 1 / 7)
        weekly_change = abs(target_weight - current_weight) / current_weight / weeks
        threshold = 0.01 if profile.goals.primary_goal == TrainingGoal.FAT_LOSS else 0.0075
        if weekly_change <= threshold:
            return []
        return [
            self._issue(
                "goal.aggressive_weight_change",
                ReadinessSeverity.CRITICAL,
                "profile.goals.target_date",
                "The requested weekly weight change exceeds the safe planning threshold.",
                guidance=True,
            )
        ]

    def _health_issues(self, health: HealthProfile, today: date) -> list[ReadinessIssue]:
        issues: list[ReadinessIssue] = []
        for injury in health.injuries:
            if injury.active and injury.severity == HealthSeverity.SEVERE:
                issues.append(
                    self._issue(
                        "health.severe_active_injury",
                        ReadinessSeverity.CRITICAL,
                        "health_profile.injuries",
                        "A severe active injury requires professional clearance.",
                        guidance=True,
                    )
                )
            elif injury.active and not injury.medically_cleared:
                issues.append(
                    self._issue(
                        "health.active_injury_not_cleared",
                        ReadinessSeverity.WARNING,
                        "health_profile.injuries",
                        "An active injury requires conservative limits until cleared.",
                        guidance=True,
                    )
                )
        for condition in health.chronic_conditions:
            if not condition.controlled or not condition.medically_cleared:
                issues.append(
                    self._issue(
                        "health.condition_not_cleared",
                        ReadinessSeverity.CRITICAL,
                        "health_profile.chronic_conditions",
                        "An uncontrolled or uncleared chronic condition requires guidance.",
                        guidance=True,
                    )
                )
        for pain in health.pain_areas:
            if pain.intensity >= 8:
                issues.append(
                    self._issue(
                        "health.severe_pain",
                        ReadinessSeverity.CRITICAL,
                        "health_profile.pain_areas",
                        "Severe reported pain requires professional assessment.",
                        guidance=True,
                    )
                )
            elif pain.intensity >= 5:
                issues.append(
                    self._issue(
                        "health.moderate_pain",
                        ReadinessSeverity.WARNING,
                        "health_profile.pain_areas",
                        "Moderate pain requires conservative exercise selection.",
                    )
                )
        recent_boundary = today - _RECENT_SURGERY_WINDOW
        for surgery in health.surgery_history:
            if surgery.surgery_date >= recent_boundary and not surgery.medically_cleared:
                issues.append(
                    self._issue(
                        "health.recent_surgery_not_cleared",
                        ReadinessSeverity.CRITICAL,
                        "health_profile.surgery_history",
                        "Recent surgery requires professional clearance.",
                        guidance=True,
                    )
                )
            elif not surgery.medically_cleared:
                issues.append(
                    self._issue(
                        "health.surgery_not_cleared",
                        ReadinessSeverity.WARNING,
                        "health_profile.surgery_history",
                        "Reported surgery remains uncleared and requires conservative limits.",
                        guidance=True,
                    )
                )
        if any(item.severity == HealthSeverity.SEVERE for item in health.mobility_limitations):
            issues.append(
                self._issue(
                    "health.severe_mobility_limitation",
                    ReadinessSeverity.WARNING,
                    "health_profile.mobility_limitations",
                    "A severe mobility limitation requires adapted movement selection.",
                    guidance=True,
                )
            )
        return issues

    @staticmethod
    def _status(
        missing: tuple[str, ...],
        issues: list[ReadinessIssue],
    ) -> ReadinessStatus:
        if any(
            issue.severity in {ReadinessSeverity.ERROR, ReadinessSeverity.CRITICAL}
            for issue in issues
        ):
            return ReadinessStatus.BLOCKED
        if missing:
            return ReadinessStatus.NEEDS_INFORMATION
        if issues:
            return ReadinessStatus.CAUTION
        return ReadinessStatus.READY

    @staticmethod
    def _issue(
        code: str,
        severity: ReadinessSeverity,
        field_path: str,
        message: str,
        *,
        guidance: bool = False,
    ) -> ReadinessIssue:
        return ReadinessIssue(
            code=code,
            severity=severity,
            field_path=field_path,
            message=message,
            requires_professional_guidance=guidance,
        )
