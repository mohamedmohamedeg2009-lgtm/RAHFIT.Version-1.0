from datetime import UTC, datetime

import pytest

from app.models.assessment import AssessmentResult, QuestionCategory, SafetyStatus
from app.models.workout import (
    Equipment,
    ExperienceLevel,
    TrainingGoal,
    TrainingLocation,
    WorkoutGenerationInput,
    WorkoutPlan,
    WorkoutSession,
    WorkoutSessionStatus,
)
from app.services.workout import (
    WorkoutAssessmentRequiredError,
    WorkoutSafetyRestrictedError,
    WorkoutService,
    WorkoutStateError,
)
from app.services.workout_generator import WorkoutGenerator


def generation_input(**updates: object) -> WorkoutGenerationInput:
    values: dict[str, object] = {
        "assessment_result_id": "result-1",
        "goal": TrainingGoal.GENERAL_FITNESS,
        "experience": ExperienceLevel.BEGINNER,
        "location": TrainingLocation.COMMERCIAL_GYM,
        "equipment": tuple(Equipment),
        "available_days": 3,
        "session_duration_minutes": 60,
    }
    values.update(updates)
    return WorkoutGenerationInput.model_validate(values)


@pytest.mark.parametrize(
    ("experience", "days", "focuses"),
    [
        (ExperienceLevel.BEGINNER, 3, ("full_body",) * 3),
        (ExperienceLevel.INTERMEDIATE, 4, ("upper", "lower", "upper", "lower")),
        (ExperienceLevel.ADVANCED, 6, ("push", "pull", "legs") * 2),
    ],
)
def test_generator_uses_deterministic_experience_split(
    experience: ExperienceLevel, days: int, focuses: tuple[str, ...]
) -> None:
    generator = WorkoutGenerator()
    inputs = generation_input(experience=experience, available_days=days)

    first = generator.generate("user-1", inputs)
    second = generator.generate("user-1", inputs)

    assert tuple(day.focus for day in first.days) == focuses
    assert [day.exercises for day in first.days] == [day.exercises for day in second.days]
    assert first.generation_key == second.generation_key


def test_generator_applies_goal_prescription_and_safety_filters() -> None:
    plan = WorkoutGenerator().generate(
        "user-1",
        generation_input(goal=TrainingGoal.STRENGTH, injuries=("knee",)),
    )

    exercises = [exercise for day in plan.days for exercise in day.exercises]
    assert exercises
    assert all(
        exercise.reps == "4-6"
        for exercise in exercises
        if exercise.exercise_id not in {"dead_bug", "side_plank", "farmer_carry"}
    )
    assert all(
        exercise.exercise_id not in {"barbell_back_squat", "lateral_bound_stick"}
        for exercise in exercises
    )


def test_generator_never_uses_unavailable_equipment() -> None:
    available = (Equipment.BODYWEIGHT, Equipment.RESISTANCE_BAND)
    plan = WorkoutGenerator().generate(
        "user-1",
        generation_input(
            equipment=available,
            location=TrainingLocation.HOME_GYM,
            session_duration_minutes=30,
        ),
    )

    assert all(
        set(exercise.equipment).issubset(available)
        for day in plan.days
        for exercise in day.exercises
    )


class FakeAssessmentReader:
    def __init__(self, result: AssessmentResult | None) -> None:
        self.result = result

    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None:
        return self.result


class FakeWorkoutStore:
    def __init__(self) -> None:
        self.plans: dict[str, WorkoutPlan] = {}
        self.sessions: dict[str, WorkoutSession] = {}

    async def find_current_plan(self, user_id: str) -> WorkoutPlan | None:
        return next((plan for plan in self.plans.values() if plan.user_id == user_id), None)

    async def create_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.plans[plan.id] = plan
        return plan

    async def list_plans(self, user_id: str, limit: int = 20) -> list[WorkoutPlan]:
        return [plan for plan in self.plans.values() if plan.user_id == user_id][:limit]

    async def find_plan(self, plan_id: str, user_id: str) -> WorkoutPlan | None:
        plan = self.plans.get(plan_id)
        return plan if plan and plan.user_id == user_id else None

    async def find_session(self, session_id: str, user_id: str) -> WorkoutSession | None:
        session = self.sessions.get(session_id)
        return session if session and session.user_id == user_id else None

    async def find_active_session(
        self, user_id: str, plan_id: str, day_id: str
    ) -> WorkoutSession | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.user_id == user_id
                and session.plan_id == plan_id
                and session.workout_day_id == day_id
                and session.status == WorkoutSessionStatus.IN_PROGRESS
            ),
            None,
        )

    async def find_session_for_date(
        self, user_id: str, plan_id: str, day_id: str, scheduled_date: object
    ) -> WorkoutSession | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.user_id == user_id
                and session.plan_id == plan_id
                and session.workout_day_id == day_id
                and session.scheduled_date == scheduled_date
            ),
            None,
        )

    async def create_session(self, session: WorkoutSession) -> WorkoutSession:
        self.sessions[session.id] = session
        return session

    async def update_exercise_progress(
        self, session: WorkoutSession, exercise_progress: tuple, progress: object
    ) -> WorkoutSession | None:
        saved = session.model_copy(
            update={
                "exercise_progress": exercise_progress,
                "progress": progress,
                "revision": session.revision + 1,
            }
        )
        self.sessions[saved.id] = saved
        return saved

    async def complete_session(
        self, session: WorkoutSession, progress: object
    ) -> WorkoutSession | None:
        saved = session.model_copy(
            update={
                "status": WorkoutSessionStatus.COMPLETED,
                "progress": progress,
                "completed_at": datetime.now(UTC),
                "revision": session.revision + 1,
            }
        )
        self.sessions[saved.id] = saved
        return saved

    async def list_sessions_since(self, user_id: str, since: datetime) -> list[WorkoutSession]:
        return [
            session
            for session in self.sessions.values()
            if session.user_id == user_id and session.started_at >= since
        ]


def assessment_result(safety: SafetyStatus = SafetyStatus.SAFE) -> AssessmentResult:
    return AssessmentResult(
        id="result-1",
        user_id="user-1",
        assessment_version=1,
        session_id="assessment-1",
        profile={
            "goals": {"primary_goal": "muscle_gain"},
            "experience": {"experience": "beginner"},
            "equipment": {
                "home_training": True,
                "equipment_available": ["dumbbells", "bands"],
            },
            "injuries": {"injury_area": ["knee"]},
        },
        answered_question_ids=("primary_goal", "experience"),
        completed_categories=(QuestionCategory.GOALS, QuestionCategory.EXPERIENCE),
        safety_status=safety,
    )


@pytest.mark.asyncio
async def test_service_requires_safe_completed_assessment() -> None:
    store = FakeWorkoutStore()
    missing = WorkoutService(store, FakeAssessmentReader(None))
    stopped = WorkoutService(store, FakeAssessmentReader(assessment_result(SafetyStatus.STOP)))

    with pytest.raises(WorkoutAssessmentRequiredError):
        await missing.generate_plan("user-1")
    with pytest.raises(WorkoutSafetyRestrictedError):
        await stopped.generate_plan("user-1")


@pytest.mark.asyncio
async def test_session_lifecycle_updates_progress_and_adherence() -> None:
    now = datetime(2026, 7, 16, tzinfo=UTC)
    store = FakeWorkoutStore()
    service = WorkoutService(store, FakeAssessmentReader(assessment_result()), clock=lambda: now)
    plan = await service.generate_plan("user-1", available_days=3, session_duration_minutes=30)
    day = service._today(plan)
    session = await service.start_session("user-1", plan.id, day.id)

    with pytest.raises(WorkoutStateError):
        await service.complete_session("user-1", session.id)

    for exercise in day.exercises:
        session = await service.update_exercise(
            "user-1", session.id, exercise.exercise_id, exercise.sets, False
        )
    completed = await service.complete_session("user-1", session.id)
    history = await service.get_history("user-1")

    assert completed.status == WorkoutSessionStatus.COMPLETED
    assert completed.progress.completion_percentage == 100
    assert history.completed_sessions == 1
    assert history.weekly_adherence_percentage == 33
