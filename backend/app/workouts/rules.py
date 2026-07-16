from dataclasses import dataclass

from app.models.workout import ExperienceLevel, TrainingGoal

RULES_VERSION = 2
MIN_SESSION_MINUTES = 20
MAX_SESSION_MINUTES = 120
MIN_WARMUP_MINUTES = 4
MIN_COOLDOWN_MINUTES = 4
MIN_SESSION_EXERCISES = 4
MAX_SESSION_EXERCISES = 8
MAX_CONSECUTIVE_TRAINING_DAYS = 3
MAX_PROGRESSION_PERCENTAGE = 10.0


@dataclass(frozen=True)
class ExperienceLimits:
    maximum_days: int
    maximum_weekly_sets: int
    maximum_high_intensity_days: int
    sets_per_exercise: int
    maximum_repeated_pattern_per_day: int


EXPERIENCE_LIMITS = {
    ExperienceLevel.BEGINNER: ExperienceLimits(4, 60, 1, 2, 1),
    ExperienceLevel.INTERMEDIATE: ExperienceLimits(5, 100, 2, 3, 2),
    ExperienceLevel.ADVANCED: ExperienceLimits(5, 140, 3, 4, 2),
}

GOAL_PRESCRIPTIONS: dict[TrainingGoal, tuple[int, int, int, int, int]] = {
    TrainingGoal.STRENGTH: (4, 6, 120, 5, 7),
    TrainingGoal.FAT_LOSS: (10, 15, 45, 5, 7),
    TrainingGoal.ENDURANCE: (12, 20, 45, 5, 7),
    TrainingGoal.MUSCLE_GAIN: (8, 12, 75, 6, 8),
    TrainingGoal.GENERAL_FITNESS: (8, 12, 60, 5, 7),
    TrainingGoal.FOOTBALL_PERFORMANCE: (6, 10, 75, 6, 8),
    TrainingGoal.GOALKEEPER_PERFORMANCE: (6, 10, 75, 6, 8),
}

RECOVERY_WEEKDAYS: dict[int, tuple[int, ...]] = {
    1: (1,),
    2: (1, 4),
    3: (1, 3, 5),
    4: (1, 2, 4, 6),
    5: (1, 2, 4, 5, 7),
    6: (1, 2, 3, 5, 6, 7),
}


def maximum_consecutive_days(weekdays: tuple[int, ...]) -> int:
    if not weekdays:
        return 0
    selected = set(weekdays)
    doubled = tuple(range(1, 8)) + tuple(range(1, 8))
    longest = current = 0
    for day in doubled:
        if day in selected:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return min(longest, len(selected))
