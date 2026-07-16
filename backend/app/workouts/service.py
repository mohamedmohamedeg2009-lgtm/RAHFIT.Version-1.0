from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

import structlog

from app.models.user import User
from app.readiness.checker import ReadinessChecker
from app.users.service import UserIntelligenceService
from app.workouts.adaptation import WorkoutAdaptationEngine
from app.workouts.exceptions import (
    WorkoutExerciseUnavailableError,
    WorkoutGenerationError,
    WorkoutPlanArchivedError,
    WorkoutPlanNotFoundError,
    WorkoutSessionNotFoundError,
    WorkoutSessionStateError,
)
from app.workouts.generator import WorkoutGenerator
from app.workouts.models import (
    CompletedExercise,
    PlannedExercise,
    SessionStatus,
    WorkoutSession,
    WorkoutStatus,
)
from app.workouts.repository import WorkoutRepositoryProtocol
from app.workouts.schemas import (
    RecordWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
    WorkoutAdaptationResponse,
    WorkoutGenerationRequest,
    WorkoutPlanResponse,
    WorkoutSessionResponse,
)


class WorkoutService:
    """Only public application boundary for workout plans, sessions, and adaptation."""

    def __init__(
        self,
        repository: WorkoutRepositoryProtocol,
        generator: WorkoutGenerator,
        *,
        adaptation_engine: WorkoutAdaptationEngine | None = None,
        intelligence: UserIntelligenceService | None = None,
        readiness: ReadinessChecker | None = None,
        id_factory: Callable[[], str] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.repository = repository
        self.generator = generator
        self.adaptation_engine = adaptation_engine or WorkoutAdaptationEngine()
        self.intelligence = intelligence
        self.readiness = readiness
        self.id_factory = id_factory or (lambda: str(uuid4()))
        self.clock = clock or (lambda: datetime.now(UTC))
        self.logger = structlog.get_logger("app.workouts.service")

    async def generate_plan(
        self, user: User, request: WorkoutGenerationRequest
    ) -> WorkoutPlanResponse:
        plan = await self.generator.generate(user, request)
        saved = await self.repository.replace_active_plan(plan)
        return WorkoutPlanResponse.from_domain(saved)

    async def get_active_plan(self, user: User) -> WorkoutPlanResponse:
        plan = await self.repository.get_active_plan(user.id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        return WorkoutPlanResponse.from_domain(plan)

    async def get_plan(self, user: User, plan_id: str) -> WorkoutPlanResponse:
        plan = await self.repository.get_by_id(user.id, plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        return WorkoutPlanResponse.from_domain(plan)

    async def list_plans(
        self, user: User, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutPlanResponse, ...]:
        plans = await self.repository.list_user_plans(user.id, limit, offset)
        return tuple(WorkoutPlanResponse.from_domain(plan) for plan in plans)

    async def activate_plan(self, user: User, plan_id: str) -> WorkoutPlanResponse:
        plan = await self.repository.activate_plan(user.id, plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        return WorkoutPlanResponse.from_domain(plan)

    async def archive_plan(self, user: User, plan_id: str) -> None:
        plan = await self.repository.get_by_id(user.id, plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        if plan.status == WorkoutStatus.ARCHIVED:
            raise WorkoutPlanArchivedError()
        if not await self.repository.archive_plan(user.id, plan_id):
            raise WorkoutPlanNotFoundError()

    async def record_session(
        self, user: User, request: RecordWorkoutSessionRequest
    ) -> WorkoutSessionResponse:
        plan = await self.repository.get_by_id(user.id, request.plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        if plan.status != WorkoutStatus.ACTIVE:
            raise WorkoutPlanArchivedError()
        day = next(
            (item for item in plan.weekly_schedule if item.day_number == request.day_number), None
        )
        if day is None:
            raise WorkoutExerciseUnavailableError("workout_day_not_found")
        planned = {item.exercise_id: item for section in day.sections for item in section.exercises}
        completion_percentage, skipped_ids, adaptation_flags = self._session_progress(
            planned, request.completed_exercises, request.status
        )
        now = self.clock()
        session = WorkoutSession(
            session_id=self.id_factory(),
            user_id=user.id,
            plan_id=plan.plan_id,
            workout_day_id=f"day-{day.day_number}",
            day_number=day.day_number,
            status=request.status,
            planned_exercise_ids=tuple(planned),
            completed_exercises=request.completed_exercises,
            skipped_exercise_ids=skipped_ids,
            completion_percentage=completion_percentage,
            planned_duration_minutes=day.estimated_duration_minutes,
            actual_duration_minutes=request.actual_duration_minutes,
            notes=request.notes,
            adaptation_flags=adaptation_flags,
            started_at=now,
            completed_at=now if request.status != SessionStatus.IN_PROGRESS else None,
            created_at=now,
            updated_at=now,
        )
        saved = await self.repository.save_session(session)
        self.logger.info(
            "workout_session_recorded",
            user_id=user.id,
            plan_id=plan.plan_id,
            session_id=saved.session_id,
            completion_percentage=saved.completion_percentage,
            adaptation_flags=saved.adaptation_flags,
        )
        return WorkoutSessionResponse.from_domain(saved)

    async def get_session(self, user: User, session_id: str) -> WorkoutSessionResponse:
        session = await self.repository.get_session(user.id, session_id)
        if session is None:
            raise WorkoutSessionNotFoundError()
        return WorkoutSessionResponse.from_domain(session)

    async def update_session(
        self,
        user: User,
        session_id: str,
        request: UpdateWorkoutSessionRequest,
    ) -> WorkoutSessionResponse:
        session = await self.repository.get_session(user.id, session_id)
        if session is None:
            raise WorkoutSessionNotFoundError()
        if session.status != SessionStatus.IN_PROGRESS:
            raise WorkoutSessionStateError()
        plan = await self.repository.get_by_id(user.id, session.plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        if plan.status != WorkoutStatus.ACTIVE:
            raise WorkoutPlanArchivedError()
        day = next(
            (item for item in plan.weekly_schedule if item.day_number == session.day_number), None
        )
        if day is None:
            raise WorkoutExerciseUnavailableError("workout_day_not_found")

        completed = (
            request.completed_exercises
            if "completed_exercises" in request.model_fields_set
            and request.completed_exercises is not None
            else session.completed_exercises
        )
        next_status = request.status or session.status
        planned = {item.exercise_id: item for section in day.sections for item in section.exercises}
        completion_percentage, skipped_ids, adaptation_flags = self._session_progress(
            planned, completed, next_status
        )
        now = self.clock()
        updated = session.model_copy(
            update={
                "status": next_status,
                "completed_exercises": completed,
                "completion_percentage": completion_percentage,
                "skipped_exercise_ids": skipped_ids,
                "adaptation_flags": adaptation_flags,
                "actual_duration_minutes": (
                    request.actual_duration_minutes
                    if "actual_duration_minutes" in request.model_fields_set
                    else session.actual_duration_minutes
                ),
                "notes": (request.notes if "notes" in request.model_fields_set else session.notes),
                "completed_at": now if next_status != SessionStatus.IN_PROGRESS else None,
                "updated_at": now,
            }
        )
        saved = await self.repository.update_session(updated)
        if saved is None:
            raise WorkoutSessionNotFoundError()
        return WorkoutSessionResponse.from_domain(saved)

    async def list_sessions(
        self,
        user: User,
        plan_id: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[WorkoutSessionResponse, ...]:
        sessions = await self.repository.list_sessions(user.id, plan_id, limit, offset)
        return tuple(WorkoutSessionResponse.from_domain(session) for session in sessions)

    async def analyze_adaptation(self, user: User, plan_id: str) -> WorkoutAdaptationResponse:
        plan = await self.repository.get_by_id(user.id, plan_id)
        if plan is None:
            raise WorkoutPlanNotFoundError()
        if self.intelligence is None or self.readiness is None:
            raise WorkoutGenerationError("workout_adaptation_dependencies_unavailable")
        snapshot = await self.intelligence.get_snapshot(user.id)
        if snapshot.profile is None:
            raise WorkoutGenerationError("workout_adaptation_profile_incomplete")
        readiness = self.readiness.check(snapshot)
        sessions = await self.repository.list_sessions(user.id, plan_id, 5)
        recommendation = self.adaptation_engine.evaluate(
            sessions, snapshot.profile, (readiness.status,)
        )
        self.logger.info(
            "workout_adaptation_analyzed",
            user_id=user.id,
            plan_id=plan_id,
            adaptation_recommendation_code=recommendation.recommendation_code,
        )
        return WorkoutAdaptationResponse.model_validate(recommendation.model_dump())

    @staticmethod
    def _session_progress(
        planned: dict[str, PlannedExercise],
        completed_exercises: tuple[CompletedExercise, ...],
        status: SessionStatus,
    ) -> tuple[int, tuple[str, ...], tuple[str, ...]]:
        submitted_ids = tuple(item.exercise_id for item in completed_exercises)
        if len(submitted_ids) != len(set(submitted_ids)) or not set(submitted_ids).issubset(
            planned
        ):
            raise WorkoutExerciseUnavailableError("workout_session_exercise_invalid")
        for exercise in completed_exercises:
            completed_set_numbers = tuple(item.set_number for item in exercise.completed_sets)
            if (
                len(completed_set_numbers) != len(set(completed_set_numbers))
                or len(completed_set_numbers) > planned[exercise.exercise_id].prescription.sets
            ):
                raise WorkoutExerciseUnavailableError("workout_session_sets_invalid")

        completed_ids = {
            item.exercise_id
            for item in completed_exercises
            if not item.skipped
            and any(completed_set.completed for completed_set in item.completed_sets)
        }
        approved_ids = set(planned)
        explicitly_skipped = {item.exercise_id for item in completed_exercises if item.skipped}
        skipped_ids = (
            tuple(sorted(explicitly_skipped))
            if status == SessionStatus.IN_PROGRESS
            else tuple(sorted(approved_ids - completed_ids))
        )
        completion_percentage = round(100 * len(completed_ids) / len(approved_ids))
        adaptation_flags = (
            ("pain_requires_review",)
            if any(item.pain_reported for item in completed_exercises)
            else ()
        )
        return completion_percentage, skipped_ids, adaptation_flags
