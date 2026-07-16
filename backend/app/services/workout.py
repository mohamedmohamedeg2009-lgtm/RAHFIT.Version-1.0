from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Protocol
from uuid import uuid4

from app.models.assessment import AssessmentResult, SafetyStatus
from app.models.workout import (
    Equipment,
    ExerciseProgress,
    ExperienceLevel,
    TrainingGoal,
    TrainingLocation,
    WorkoutDashboardState,
    WorkoutDay,
    WorkoutGenerationInput,
    WorkoutPlan,
    WorkoutProgress,
    WorkoutSession,
    WorkoutSessionStatus,
)
from app.services.workout_generator import WorkoutGenerationError, WorkoutGenerator


class WorkoutAssessmentReader(Protocol):
    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None: ...


class WorkoutStore(Protocol):
    async def find_current_plan(self, user_id: str) -> WorkoutPlan | None: ...

    async def create_plan(self, plan: WorkoutPlan) -> WorkoutPlan: ...

    async def list_plans(self, user_id: str, limit: int = 20) -> list[WorkoutPlan]: ...

    async def find_plan(self, plan_id: str, user_id: str) -> WorkoutPlan | None: ...

    async def find_session(self, session_id: str, user_id: str) -> WorkoutSession | None: ...

    async def find_active_session(
        self, user_id: str, plan_id: str, day_id: str
    ) -> WorkoutSession | None: ...

    async def find_session_for_date(
        self, user_id: str, plan_id: str, day_id: str, scheduled_date: date
    ) -> WorkoutSession | None: ...

    async def create_session(self, session: WorkoutSession) -> WorkoutSession: ...

    async def update_exercise_progress(
        self,
        session: WorkoutSession,
        exercise_progress: tuple[ExerciseProgress, ...],
        progress: WorkoutProgress,
    ) -> WorkoutSession | None: ...

    async def complete_session(
        self, session: WorkoutSession, progress: WorkoutProgress
    ) -> WorkoutSession | None: ...

    async def list_sessions_since(self, user_id: str, since: datetime) -> list[WorkoutSession]: ...


class WorkoutNotFoundError(Exception):
    """Raised for absent or cross-owner workout resources."""


class WorkoutAssessmentRequiredError(Exception):
    """Raised when plan generation has no completed assessment source."""


class WorkoutSafetyRestrictedError(Exception):
    """Raised when deterministic assessment safety blocks plan generation."""


class WorkoutStateError(Exception):
    """Raised when a workout lifecycle operation is not currently valid."""


@dataclass(frozen=True)
class CurrentWorkoutState:
    plan: WorkoutPlan
    today: WorkoutDay
    session: WorkoutSession | None


@dataclass(frozen=True)
class WorkoutHistoryState:
    plans: tuple[WorkoutPlan, ...]
    completed_sessions: int
    weekly_adherence_percentage: int


class WorkoutService:
    def __init__(
        self,
        store: WorkoutStore,
        assessment: WorkoutAssessmentReader,
        generator: WorkoutGenerator | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.store = store
        self.assessment = assessment
        self.generator = generator or WorkoutGenerator()
        self.clock = clock or (lambda: datetime.now(UTC))

    async def generate_plan(
        self,
        user_id: str,
        available_days: int | None = None,
        session_duration_minutes: int | None = None,
    ) -> WorkoutPlan:
        result = await self.assessment.get_latest_assessment_optional(user_id)
        if not result:
            raise WorkoutAssessmentRequiredError
        if result.user_id != user_id:
            raise WorkoutNotFoundError
        if result.safety_status == SafetyStatus.STOP:
            raise WorkoutSafetyRestrictedError
        inputs = self._inputs(result, available_days, session_duration_minutes)
        current = await self.store.find_current_plan(user_id)
        generation_key = self.generator.generation_key(inputs)
        if current and current.generation_key == generation_key:
            return current
        try:
            plan = self.generator.generate(user_id, inputs)
        except WorkoutGenerationError:
            raise
        return await self.store.create_plan(plan)

    async def get_current(self, user_id: str) -> CurrentWorkoutState:
        plan = await self.store.find_current_plan(user_id)
        if not plan:
            raise WorkoutNotFoundError
        today = self._today(plan)
        session = await self.store.find_session_for_date(
            user_id, plan.id, today.id, self.clock().date()
        )
        return CurrentWorkoutState(plan, today, session)

    async def get_plan(self, user_id: str, plan_id: str) -> WorkoutPlan:
        plan = await self.store.find_plan(plan_id, user_id)
        if not plan:
            raise WorkoutNotFoundError
        return plan

    async def get_history(self, user_id: str) -> WorkoutHistoryState:
        plans = tuple(await self.store.list_plans(user_id))
        since = self.clock() - timedelta(days=7)
        sessions = await self.store.list_sessions_since(user_id, since)
        completed = sum(item.status == WorkoutSessionStatus.COMPLETED for item in sessions)
        scheduled = plans[0].available_days if plans else 0
        adherence = min(100, round(completed / scheduled * 100)) if scheduled else 0
        return WorkoutHistoryState(plans, completed, adherence)

    async def start_session(self, user_id: str, plan_id: str, day_id: str) -> WorkoutSession:
        plan = await self.get_plan(user_id, plan_id)
        day = self._day(plan, day_id)
        existing = await self.store.find_active_session(user_id, plan_id, day_id)
        if existing:
            return existing
        exercise_progress = tuple(
            ExerciseProgress(exercise_id=exercise.exercise_id) for exercise in day.exercises
        )
        progress = self._progress(day, exercise_progress)
        session = WorkoutSession(
            id=uuid4().hex,
            user_id=user_id,
            plan_id=plan_id,
            workout_day_id=day_id,
            scheduled_date=self.clock().date(),
            exercise_progress=exercise_progress,
            progress=progress,
        )
        return await self.store.create_session(session)

    async def update_exercise(
        self,
        user_id: str,
        session_id: str,
        exercise_id: str,
        completed_sets: int,
        skipped: bool,
    ) -> WorkoutSession:
        session = await self._session(user_id, session_id)
        if session.status != WorkoutSessionStatus.IN_PROGRESS:
            raise WorkoutStateError("Only an active workout session can be updated.")
        plan = await self.get_plan(user_id, session.plan_id)
        day = self._day(plan, session.workout_day_id)
        exercise = next((item for item in day.exercises if item.exercise_id == exercise_id), None)
        if not exercise:
            raise WorkoutNotFoundError
        if completed_sets > exercise.sets:
            raise WorkoutStateError("Completed sets cannot exceed the prescribed sets.")
        updated = tuple(
            (
                ExerciseProgress(
                    exercise_id=item.exercise_id,
                    completed_sets=0 if skipped else completed_sets,
                    skipped=skipped,
                )
                if item.exercise_id == exercise_id
                else item
            )
            for item in session.exercise_progress
        )
        progress = self._progress(day, updated)
        saved = await self.store.update_exercise_progress(session, updated, progress)
        if not saved:
            raise WorkoutStateError("The workout session changed. Refresh and try again.")
        return saved

    async def complete_session(self, user_id: str, session_id: str) -> WorkoutSession:
        session = await self._session(user_id, session_id)
        if session.status == WorkoutSessionStatus.COMPLETED:
            return session
        plan = await self.get_plan(user_id, session.plan_id)
        day = self._day(plan, session.workout_day_id)
        by_id = {item.exercise_id: item for item in session.exercise_progress}
        unresolved = [
            exercise.exercise_id
            for exercise in day.exercises
            if not by_id[exercise.exercise_id].skipped
            and by_id[exercise.exercise_id].completed_sets < exercise.sets
        ]
        if unresolved:
            raise WorkoutStateError("Complete or skip every exercise before finishing.")
        progress = self._progress(day, session.exercise_progress)
        completed = await self.store.complete_session(session, progress)
        if not completed:
            raise WorkoutStateError("The workout session changed. Refresh and try again.")
        return completed

    async def get_dashboard_state(self, user_id: str) -> WorkoutDashboardState | None:
        plan = await self.store.find_current_plan(user_id)
        if not plan:
            return None
        day = self._today(plan)
        session = await self.store.find_session_for_date(
            user_id, plan.id, day.id, self.clock().date()
        )
        status = session.status.value if session else "not_started"
        completion = session.progress.completion_percentage if session else 0
        route = f"/workouts/{plan.id}/session/{day.id}"
        return WorkoutDashboardState(
            plan_id=plan.id,
            day_id=day.id,
            title=day.title,
            focus=day.focus,
            status=status,
            completion_percentage=completion,
            destination_route=route,
            last_activity_at=session.updated_at if session else plan.generated_at,
        )

    def _inputs(
        self,
        result: AssessmentResult,
        available_days: int | None,
        session_duration_minutes: int | None,
    ) -> WorkoutGenerationInput:
        values = {
            question_id: value
            for category in result.profile.values()
            for question_id, value in category.items()
        }
        experience_value = values.get("experience")
        try:
            experience = ExperienceLevel(str(experience_value))
        except ValueError as exc:
            raise WorkoutAssessmentRequiredError from exc
        equipment, location = self._equipment(values)
        goal = self._goal(values)
        injuries_value = values.get("injury_area", [])
        injuries = (
            tuple(str(item) for item in injuries_value) if isinstance(injuries_value, list) else ()
        )
        return WorkoutGenerationInput(
            assessment_result_id=result.id,
            goal=goal,
            experience=experience,
            location=location,
            equipment=equipment,
            injuries=injuries,
            available_days=available_days or self.generator.default_days(experience),
            session_duration_minutes=session_duration_minutes or 60,
        )

    @staticmethod
    def _goal(values: Mapping[str, object]) -> TrainingGoal:
        primary = str(values.get("primary_goal", "general_fitness"))
        sports = values.get("sports", [])
        position = values.get("football_position")
        if isinstance(sports, list) and "football" in sports:
            return (
                TrainingGoal.GOALKEEPER_PERFORMANCE
                if position == "goalkeeper"
                else TrainingGoal.FOOTBALL_PERFORMANCE
            )
        if primary == "athletic_performance" and isinstance(sports, list):
            if "strength_sport" in sports:
                return TrainingGoal.STRENGTH
            if "running" in sports:
                return TrainingGoal.ENDURANCE
        return {
            "fat_loss": TrainingGoal.FAT_LOSS,
            "muscle_gain": TrainingGoal.MUSCLE_GAIN,
            "general_fitness": TrainingGoal.GENERAL_FITNESS,
            "athletic_performance": TrainingGoal.GENERAL_FITNESS,
        }.get(primary, TrainingGoal.GENERAL_FITNESS)

    @staticmethod
    def _equipment(
        values: Mapping[str, object],
    ) -> tuple[tuple[Equipment, ...], TrainingLocation]:
        home = values.get("home_training") is True
        raw = values.get("equipment_available" if home else "commercial_gym_equipment", [])
        selected = set(raw) if isinstance(raw, list) else set()
        mapping = {
            "dumbbells": {Equipment.DUMBBELL},
            "bands": {Equipment.RESISTANCE_BAND},
            "free_weights": {Equipment.BARBELL, Equipment.DUMBBELL, Equipment.KETTLEBELL},
            "machines": {Equipment.MACHINE, Equipment.CABLE},
            "functional_area": {Equipment.KETTLEBELL, Equipment.MEDICINE_BALL},
        }
        equipment = {Equipment.BODYWEIGHT}
        for value in selected:
            equipment.update(mapping.get(str(value), set()))
        if home and selected.issubset({"none"}):
            location = TrainingLocation.BODYWEIGHT_ONLY
        else:
            location = TrainingLocation.HOME_GYM if home else TrainingLocation.COMMERCIAL_GYM
        return tuple(sorted(equipment, key=str)), location

    def _today(self, plan: WorkoutPlan) -> WorkoutDay:
        index = (self.clock().date().isoweekday() - 1) % len(plan.days)
        return plan.days[index]

    @staticmethod
    def _day(plan: WorkoutPlan, day_id: str) -> WorkoutDay:
        day = next((item for item in plan.days if item.id == day_id), None)
        if not day:
            raise WorkoutNotFoundError
        return day

    async def _session(self, user_id: str, session_id: str) -> WorkoutSession:
        session = await self.store.find_session(session_id, user_id)
        if not session:
            raise WorkoutNotFoundError
        return session

    @staticmethod
    def _progress(day: WorkoutDay, progress_items: tuple[ExerciseProgress, ...]) -> WorkoutProgress:
        prescriptions = {item.exercise_id: item.sets for item in day.exercises}
        completed_sets = sum(item.completed_sets for item in progress_items)
        total_sets = sum(prescriptions.values())
        completed_exercises = sum(
            item.completed_sets >= prescriptions[item.exercise_id]
            for item in progress_items
            if not item.skipped
        )
        percentage = round(completed_sets / total_sets * 100) if total_sets else 0
        return WorkoutProgress(
            completed_sets=completed_sets,
            total_sets=total_sets,
            completed_exercises=completed_exercises,
            total_exercises=len(day.exercises),
            completion_percentage=percentage,
        )
