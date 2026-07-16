import hashlib
import json
from dataclasses import dataclass

from app.models.workout import ExperienceLevel, TrainingGoal, TrainingLocation
from app.profile.models import AgeGroup
from app.readiness.models import ReadinessResult, ReadinessStatus
from app.users.models import UserIntelligenceSnapshot
from app.workouts.exceptions import WorkoutGenerationError
from app.workouts.exercises.models import ExerciseLocation, MovementPattern
from app.workouts.models import SetPrescription, WorkoutPlanType
from app.workouts.rules import (
    EXPERIENCE_LIMITS,
    GOAL_PRESCRIPTIONS,
    MAX_SESSION_EXERCISES,
    MAX_SESSION_MINUTES,
    MIN_SESSION_EXERCISES,
    MIN_SESSION_MINUTES,
    RECOVERY_WEEKDAYS,
    RULES_VERSION,
)


@dataclass(frozen=True)
class DayTemplate:
    day_number: int
    weekday: int
    focus: str
    main_patterns: tuple[MovementPattern, ...]
    accessory_patterns: tuple[MovementPattern, ...]
    include_conditioning: bool
    high_intensity: bool


@dataclass(frozen=True)
class WorkoutConstraints:
    plan_type: WorkoutPlanType
    days: tuple[DayTemplate, ...]
    session_minutes: int
    prescription: SetPrescription
    locations: frozenset[ExerciseLocation]
    maximum_weekly_sets: int
    minimum_session_exercises: int
    maximum_session_exercises: int
    generation_key: str


class WorkoutPlanner:
    """Pure rules engine for deterministic structure, recovery, and prescriptions."""

    def create_constraints(
        self, snapshot: UserIntelligenceSnapshot, readiness: ReadinessResult
    ) -> WorkoutConstraints:
        profile = snapshot.profile
        if profile is None or snapshot.health_profile is None or not readiness.ready_for_ai:
            raise WorkoutGenerationError("workout_snapshot_not_eligible")
        duration = profile.training.session_duration_minutes
        if not MIN_SESSION_MINUTES <= duration <= MAX_SESSION_MINUTES:
            raise WorkoutGenerationError("workout_session_duration_unsupported")

        limits = EXPERIENCE_LIMITS[profile.training.experience]
        maximum_days = limits.maximum_days
        if profile.age_group in {AgeGroup.ADOLESCENT, AgeGroup.OLDER_ADULT}:
            maximum_days = min(maximum_days, 4)
        if readiness.status == ReadinessStatus.CAUTION:
            maximum_days = min(maximum_days, 4)
        frequency = min(profile.training.available_days, maximum_days)
        if frequency < 1:
            raise WorkoutGenerationError("workout_frequency_unsupported")

        plan_type = self._plan_type(
            profile.goals.primary_goal,
            profile.training.experience,
            profile.training.workout_location,
        )
        days = self._days(profile.goals.primary_goal, frequency, limits.maximum_high_intensity_days)
        prescription = self._prescription(profile.goals.primary_goal, profile.training.experience)
        stable = json.dumps(
            {
                "user": snapshot.user_id,
                "profile_version": profile.schema_version,
                "health_version": snapshot.health_profile.schema_version,
                "goal": profile.goals.primary_goal.value,
                "secondary_goal": (
                    profile.goals.secondary_goal.value if profile.goals.secondary_goal else None
                ),
                "age_group": profile.age_group.value,
                "experience": profile.training.experience.value,
                "readiness": readiness.status.value,
                "frequency": frequency,
                "duration": duration,
                "location": profile.training.workout_location.value,
                "equipment": sorted(item.value for item in profile.training.available_equipment),
                "sleep": profile.lifestyle.sleep_hours,
                "stress": profile.lifestyle.stress_level,
                "rules": RULES_VERSION,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return WorkoutConstraints(
            plan_type=plan_type,
            days=days,
            session_minutes=duration,
            prescription=prescription,
            locations=self.locations(profile.training.workout_location),
            maximum_weekly_sets=limits.maximum_weekly_sets,
            minimum_session_exercises=MIN_SESSION_EXERCISES,
            maximum_session_exercises=MAX_SESSION_EXERCISES,
            generation_key=hashlib.sha256(stable.encode()).hexdigest(),
        )

    @staticmethod
    def locations(location: TrainingLocation) -> frozenset[ExerciseLocation]:
        return {
            TrainingLocation.COMMERCIAL_GYM: frozenset({ExerciseLocation.GYM}),
            TrainingLocation.HOME_GYM: frozenset({ExerciseLocation.HOME}),
            TrainingLocation.BODYWEIGHT_ONLY: frozenset(
                {ExerciseLocation.HOME, ExerciseLocation.OUTDOOR}
            ),
            TrainingLocation.OUTDOOR: frozenset({ExerciseLocation.OUTDOOR}),
        }[location]

    @staticmethod
    def _plan_type(
        goal: TrainingGoal, experience: ExperienceLevel, location: TrainingLocation
    ) -> WorkoutPlanType:
        if experience == ExperienceLevel.BEGINNER and goal == TrainingGoal.GENERAL_FITNESS:
            return WorkoutPlanType.BEGINNER_FOUNDATION
        if (
            location in {TrainingLocation.HOME_GYM, TrainingLocation.BODYWEIGHT_ONLY}
            and goal == TrainingGoal.GENERAL_FITNESS
        ):
            return WorkoutPlanType.HOME_WORKOUT
        return {
            TrainingGoal.FAT_LOSS: WorkoutPlanType.WEIGHT_LOSS,
            TrainingGoal.MUSCLE_GAIN: WorkoutPlanType.MUSCLE_GAIN,
            TrainingGoal.STRENGTH: WorkoutPlanType.STRENGTH,
            TrainingGoal.FOOTBALL_PERFORMANCE: WorkoutPlanType.FOOTBALL_PERFORMANCE,
            TrainingGoal.GOALKEEPER_PERFORMANCE: WorkoutPlanType.GOALKEEPER_PERFORMANCE,
            TrainingGoal.GENERAL_FITNESS: WorkoutPlanType.GENERAL_FITNESS,
            TrainingGoal.ENDURANCE: WorkoutPlanType.GENERAL_FITNESS,
        }[goal]

    @staticmethod
    def _days(
        goal: TrainingGoal, frequency: int, maximum_high_intensity_days: int
    ) -> tuple[DayTemplate, ...]:
        upper = (MovementPattern.PUSH, MovementPattern.PULL, MovementPattern.CARRY)
        lower = (MovementPattern.SQUAT, MovementPattern.HINGE, MovementPattern.LUNGE)
        full = (
            MovementPattern.SQUAT,
            MovementPattern.HINGE,
            MovementPattern.PUSH,
            MovementPattern.PULL,
        )
        performance = (MovementPattern.HINGE, MovementPattern.LUNGE, MovementPattern.ROTATION)
        days: list[DayTemplate] = []
        for index, weekday in enumerate(RECOVERY_WEEKDAYS[frequency], start=1):
            patterns: tuple[MovementPattern, ...]
            if goal in {TrainingGoal.FOOTBALL_PERFORMANCE, TrainingGoal.GOALKEEPER_PERFORMANCE}:
                patterns = performance if index % 2 else upper
                focus = "Performance and control" if index % 2 else "Upper body resilience"
                conditioning = index % 2 == 1
            elif frequency <= 3:
                patterns, focus = full, "Full body foundation"
                conditioning = goal in {TrainingGoal.FAT_LOSS, TrainingGoal.ENDURANCE}
            elif index % 2:
                patterns, focus, conditioning = lower, "Lower body and core", False
            else:
                patterns, focus = upper, "Upper body and posture"
                conditioning = goal in {TrainingGoal.FAT_LOSS, TrainingGoal.ENDURANCE}
            high_intensity = (
                goal
                in {
                    TrainingGoal.STRENGTH,
                    TrainingGoal.FOOTBALL_PERFORMANCE,
                    TrainingGoal.GOALKEEPER_PERFORMANCE,
                }
                and index <= maximum_high_intensity_days
                and index % 2 == 1
            )
            days.append(
                DayTemplate(
                    day_number=index,
                    weekday=weekday,
                    focus=focus,
                    main_patterns=patterns,
                    accessory_patterns=(MovementPattern.CORE,),
                    include_conditioning=conditioning,
                    high_intensity=high_intensity,
                )
            )
        return tuple(days)

    @staticmethod
    def _prescription(goal: TrainingGoal, experience: ExperienceLevel) -> SetPrescription:
        minimum, maximum, rest, rpe_min, rpe_max = GOAL_PRESCRIPTIONS[goal]
        return SetPrescription(
            sets=EXPERIENCE_LIMITS[experience].sets_per_exercise,
            min_reps=minimum,
            max_reps=maximum,
            rest_seconds=rest,
            rpe_min=rpe_min,
            rpe_max=rpe_max,
            reps_in_reserve=max(1, 10 - rpe_max),
            progression_limit_percentage=5.0,
        )
