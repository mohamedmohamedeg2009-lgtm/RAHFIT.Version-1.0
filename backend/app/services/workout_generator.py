from hashlib import sha256
from uuid import uuid4

from app.models.workout import (
    Equipment,
    Exercise,
    ExperienceLevel,
    TrainingGoal,
    WorkoutDay,
    WorkoutExercise,
    WorkoutGenerationInput,
    WorkoutPlan,
)
from app.services.exercise_catalog import ExerciseCatalog


class WorkoutGenerationError(Exception):
    """Raised when safe deterministic generation cannot produce a complete plan."""


class WorkoutGenerator:
    """Rules-only workout generator with deterministic selection and prescriptions."""

    def __init__(self, catalog: ExerciseCatalog | None = None) -> None:
        self.catalog = catalog or ExerciseCatalog()

    def generate(self, user_id: str, inputs: WorkoutGenerationInput) -> WorkoutPlan:
        focuses = self._split(inputs.experience, inputs.available_days)
        exercise_count = (
            4
            if inputs.session_duration_minutes <= 40
            else 5
            if inputs.session_duration_minutes <= 60
            else 6
        )
        days = tuple(
            self._day(number, focus, exercise_count, inputs)
            for number, focus in enumerate(focuses, start=1)
        )
        generation_key = self.generation_key(inputs)
        return WorkoutPlan(
            id=uuid4().hex,
            user_id=user_id,
            assessment_result_id=inputs.assessment_result_id,
            goal=inputs.goal,
            experience=inputs.experience,
            location=inputs.location,
            equipment=inputs.equipment,
            injuries=inputs.injuries,
            available_days=len(days),
            session_duration_minutes=inputs.session_duration_minutes,
            days=days,
            generation_key=generation_key,
        )

    @staticmethod
    def generation_key(inputs: WorkoutGenerationInput) -> str:
        payload = inputs.model_dump_json(exclude_none=True)
        return sha256(payload.encode()).hexdigest()

    @staticmethod
    def default_days(experience: ExperienceLevel) -> int:
        return {
            ExperienceLevel.BEGINNER: 3,
            ExperienceLevel.INTERMEDIATE: 4,
            ExperienceLevel.ADVANCED: 6,
        }[experience]

    @staticmethod
    def _split(experience: ExperienceLevel, days: int) -> tuple[str, ...]:
        if experience == ExperienceLevel.BEGINNER:
            return tuple("full_body" for _ in range(days))
        if experience == ExperienceLevel.INTERMEDIATE:
            pattern: tuple[str, ...] = ("upper", "lower")
            return tuple(pattern[index % 2] for index in range(days))
        pattern = ("push", "pull", "legs")
        return tuple(pattern[index % 3] for index in range(days))

    def _day(
        self,
        number: int,
        focus: str,
        count: int,
        inputs: WorkoutGenerationInput,
    ) -> WorkoutDay:
        candidates = self._safe_candidates(focus, inputs)
        selected = self._select_with_movement_variety(candidates, count, inputs)
        if len(selected) < count:
            raise WorkoutGenerationError(
                "Available equipment and safety constraints cannot produce a complete plan."
            )
        exercises = tuple(self._prescribe(exercise, inputs) for exercise in selected)
        return WorkoutDay(
            id=f"day_{number}",
            day_number=number,
            title=self._title(focus, number),
            focus=focus,
            estimated_duration_minutes=inputs.session_duration_minutes,
            exercises=exercises,
        )

    def _safe_candidates(self, focus: str, inputs: WorkoutGenerationInput) -> list[Exercise]:
        equipment = set(inputs.equipment)
        injuries = set(inputs.injuries)
        level = self._level(inputs.experience)
        return [
            exercise
            for exercise in self.catalog.active()
            if focus in exercise.tags
            and set(exercise.equipment).intersection(equipment)
            and not injuries.intersection(exercise.contraindications)
            and self._level(exercise.experience_level) <= level
        ]

    @staticmethod
    def _level(level: ExperienceLevel) -> int:
        return {
            ExperienceLevel.BEGINNER: 1,
            ExperienceLevel.INTERMEDIATE: 2,
            ExperienceLevel.ADVANCED: 3,
        }[level]

    def _select_with_movement_variety(
        self,
        candidates: list[Exercise],
        count: int,
        inputs: WorkoutGenerationInput,
    ) -> list[Exercise]:
        goal_tag = self._goal_tag(inputs.goal)
        injuries = set(inputs.injuries)

        def score(exercise: Exercise) -> tuple[int, str]:
            value = 0
            if goal_tag in exercise.tags:
                value += 4
            if injuries.intersection(exercise.supported_injuries):
                value += 3
            if Equipment.BODYWEIGHT not in exercise.equipment:
                value += 1
            return (-value, exercise.id)

        ordered = sorted(candidates, key=score)
        selected: list[Exercise] = []
        used_movements = set()
        for exercise in ordered:
            if exercise.movement_type in used_movements:
                continue
            selected.append(exercise)
            used_movements.add(exercise.movement_type)
            if len(selected) == count:
                return selected
        for exercise in ordered:
            if exercise not in selected:
                selected.append(exercise)
            if len(selected) == count:
                break
        return selected

    @staticmethod
    def _goal_tag(goal: TrainingGoal) -> str:
        return {
            TrainingGoal.FOOTBALL_PERFORMANCE: "football",
            TrainingGoal.GOALKEEPER_PERFORMANCE: "goalkeeper",
        }.get(goal, goal.value)

    @staticmethod
    def _prescription(goal: TrainingGoal) -> tuple[int, str, int]:
        return {
            TrainingGoal.FAT_LOSS: (3, "10-15", 60),
            TrainingGoal.MUSCLE_GAIN: (4, "8-12", 90),
            TrainingGoal.STRENGTH: (4, "4-6", 150),
            TrainingGoal.GENERAL_FITNESS: (3, "8-12", 75),
            TrainingGoal.ENDURANCE: (3, "12-20", 45),
            TrainingGoal.FOOTBALL_PERFORMANCE: (3, "6-10", 90),
            TrainingGoal.GOALKEEPER_PERFORMANCE: (3, "6-10", 90),
        }[goal]

    def _prescribe(self, exercise: Exercise, inputs: WorkoutGenerationInput) -> WorkoutExercise:
        sets, reps, rest = self._prescription(inputs.goal)
        if exercise.exercise_type.value in {"power", "core", "conditioning"}:
            reps = exercise.recommended_reps
            sets = min(sets, exercise.recommended_sets[1])
        notes = "Use controlled technique and stop if symptoms appear."
        if inputs.injuries and set(inputs.injuries).intersection(exercise.supported_injuries):
            notes = "Selected as a conservative option; keep the movement symptom-free."
        return WorkoutExercise(
            exercise_id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            muscle_groups=exercise.muscle_groups,
            equipment=exercise.equipment,
            sets=sets,
            reps=reps,
            rest_seconds=rest,
            tempo=exercise.tempo,
            notes=notes,
        )

    @staticmethod
    def _title(focus: str, number: int) -> str:
        label = {
            "full_body": "Full Body",
            "upper": "Upper Body",
            "lower": "Lower Body",
            "push": "Push",
            "pull": "Pull",
            "legs": "Legs",
        }[focus]
        return f"Day {number} · {label}"
