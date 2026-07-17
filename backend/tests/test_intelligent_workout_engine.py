from datetime import UTC, date, datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic import ValidationError

from app.ai.providers import MockProvider, MockProviderMode
from app.ai.service import AIService
from app.context import UserIntelligenceContextBuilder
from app.database.indexes import ensure_intelligent_workout_indexes
from app.health.models import (
    ChronicConditionRecord,
    HealthProfile,
    HealthSeverity,
    InjuryRecord,
    MobilityLimitationRecord,
    PainAreaRecord,
)
from app.models.nutrition import ActivityLevel
from app.models.user import User
from app.models.workout import Equipment, ExperienceLevel, TrainingGoal, TrainingLocation
from app.profile.models import (
    BodyProfile,
    Gender,
    GoalsProfile,
    IdentityProfile,
    LifestyleProfile,
    NutritionProfile,
    TrainingProfile,
    UserProfile,
)
from app.readiness.checker import ReadinessChecker
from app.readiness.models import ReadinessStatus
from app.services.ai_safety import AISafetyEngine
from app.users.models import UserIntelligenceSnapshot
from app.workouts.adaptation import AdaptationAction, WorkoutAdaptationEngine
from app.workouts.exceptions import (
    WorkoutExerciseUnavailableError,
    WorkoutPersistenceError,
    WorkoutPlanArchivedError,
    WorkoutProfileIncompleteError,
    WorkoutSessionStateError,
)
from app.workouts.exercises.catalog import ExerciseCatalog
from app.workouts.exercises.models import ExerciseLocation, MovementPattern
from app.workouts.exercises.selector import (
    ExerciseSelector,
    RejectionReason,
    SelectionContext,
)
from app.workouts.generator import WorkoutGenerator
from app.workouts.models import (
    CompletedExercise,
    CompletedSet,
    ExercisePerformance,
    GenerationMode,
    SectionType,
    SessionStatus,
    SetResult,
    WorkoutPlan,
    WorkoutSession,
    WorkoutStatus,
)
from app.workouts.planner import WorkoutPlanner
from app.workouts.repository import MongoWorkoutRepository
from app.workouts.schemas import (
    RecordWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
    WorkoutGenerationRequest,
)
from app.workouts.service import WorkoutService
from app.workouts.validator import WorkoutValidationStatus, WorkoutValidator

NOW = datetime(2026, 7, 16, 12, tzinfo=UTC)


def _snapshot(
    *,
    injury: InjuryRecord | None = None,
    condition: ChronicConditionRecord | None = None,
    pain: PainAreaRecord | None = None,
    mobility: MobilityLimitationRecord | None = None,
    complete: bool = True,
    goal: TrainingGoal = TrainingGoal.MUSCLE_GAIN,
    experience: ExperienceLevel = ExperienceLevel.INTERMEDIATE,
    age: int = 30,
    days: int = 4,
    duration: int = 60,
    equipment: tuple[Equipment, ...] = (Equipment.DUMBBELL, Equipment.BODYWEIGHT),
    location: TrainingLocation = TrainingLocation.HOME_GYM,
    sleep_hours: float = 8.0,
) -> UserIntelligenceSnapshot:
    if not complete:
        return UserIntelligenceSnapshot(user_id="user-1", profile=None, health_profile=None)
    profile = UserProfile(
        id="profile-1",
        user_id="user-1",
        identity=IdentityProfile(
            full_name="Rahfit User", age=age, gender=Gender.MALE, country="EG"
        ),
        body=BodyProfile(height_cm=180.0, weight_kg=80.0, body_fat_percentage=20.0),
        goals=GoalsProfile(
            primary_goal=goal,
            secondary_goal=(
                TrainingGoal.STRENGTH
                if goal == TrainingGoal.GENERAL_FITNESS
                else TrainingGoal.GENERAL_FITNESS
            ),
            target_weight_kg=(75.0 if goal == TrainingGoal.FAT_LOSS else 84.0),
            target_date=date(2027, 7, 16),
        ),
        training=TrainingProfile(
            experience=experience,
            available_days=days,
            session_duration_minutes=duration,
            available_equipment=equipment,
            workout_location=location,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=sleep_hours,
            stress_level=4,
            activity_level=ActivityLevel.MODERATE,
            daily_water_ml=2500,
        ),
        nutrition=NutritionProfile(dietary_preferences=(), allergies=(), dietary_restrictions=()),
    )
    health = HealthProfile(
        id="health-1",
        user_id="user-1",
        injuries=(injury,) if injury else (),
        chronic_conditions=(condition,) if condition else (),
        pain_areas=(pain,) if pain else (),
        mobility_limitations=(mobility,) if mobility else (),
        surgery_history=(),
    )
    return UserIntelligenceSnapshot(user_id="user-1", profile=profile, health_profile=health)


class SnapshotReader:
    def __init__(self, snapshot: UserIntelligenceSnapshot) -> None:
        self.snapshot = snapshot

    async def get_snapshot(self, user_id: str) -> UserIntelligenceSnapshot:
        assert user_id == self.snapshot.user_id
        return self.snapshot


def _generator(
    snapshot: UserIntelligenceSnapshot, ai_service: object | None = None
) -> WorkoutGenerator:
    return WorkoutGenerator(
        intelligence=cast(Any, SnapshotReader(snapshot)),
        readiness=ReadinessChecker(clock=lambda: NOW),
        planner=WorkoutPlanner(),
        catalog=ExerciseCatalog(),
        selector=ExerciseSelector(),
        validator=WorkoutValidator(),
        ai_service=cast(Any, ai_service),
        id_factory=lambda: "plan-1",
        clock=lambda: NOW,
    )


def _user() -> User:
    return User(id="user-1", email="user@example.com", password_hash="hash")


def test_catalog_is_versioned_unique_and_covers_required_patterns() -> None:
    catalog = ExerciseCatalog()
    exercises = catalog.all()
    assert catalog.version == 1
    assert len({item.id for item in exercises}) == len(exercises)
    assert set(MovementPattern).issubset({item.movement_pattern for item in exercises})
    assert all(item.instructions and item.safety_notes for item in exercises)


def test_selector_records_equipment_location_experience_and_injury_rejections() -> None:
    catalog = ExerciseCatalog()
    result = ExerciseSelector().select(
        catalog.all(),
        SelectionContext(
            equipment=frozenset({Equipment.BODYWEIGHT}),
            locations=frozenset({ExerciseLocation.HOME}),
            experience=ExperienceLevel.BEGINNER,
            injury_areas=frozenset({"knee"}),
            remaining_minutes=60,
        ),
        (MovementPattern.SQUAT, MovementPattern.PUSH),
    )
    reasons = {reason for item in result.rejections for reason in item.reasons}
    assert RejectionReason.EQUIPMENT_UNAVAILABLE in reasons
    assert RejectionReason.LOCATION_INCOMPATIBLE in reasons
    assert RejectionReason.EXPERIENCE_TOO_LOW in reasons
    assert RejectionReason.INJURY_CONTRAINDICATION in reasons
    assert all(item.id != "bodyweight_squat" for item in result.selected)


@pytest.mark.asyncio
async def test_generation_is_deterministic_safe_and_validated() -> None:
    snapshot = _snapshot()
    generator = _generator(snapshot)
    first = await generator.generate(_user(), WorkoutGenerationRequest())
    second = await generator.generate(_user(), WorkoutGenerationRequest())

    assert first.metadata.generation_key == second.metadata.generation_key
    assert first.weekly_schedule == second.weekly_schedule
    assert first.training_days_per_week == 4
    assert WorkoutValidator().validate(first, snapshot, ExerciseCatalog()).valid


@pytest.mark.asyncio
async def test_generation_excludes_injury_conflicts() -> None:
    injury = InjuryRecord(
        area="knee",
        description="minor knee irritation",
        severity=HealthSeverity.MILD,
        active=True,
        medically_cleared=True,
    )
    plan = await _generator(_snapshot(injury=injury)).generate(_user(), WorkoutGenerationRequest())
    ids = {
        item.exercise_id
        for day in plan.weekly_schedule
        for section in day.sections
        for item in section.exercises
    }
    assert "bodyweight_squat" not in ids
    assert plan.metadata.rejected_by_reason[RejectionReason.INJURY_CONTRAINDICATION.value] > 0


@pytest.mark.asyncio
async def test_incomplete_readiness_fails_closed_without_ai() -> None:
    value = _snapshot(complete=False)
    provider = MockProvider()
    with pytest.raises(WorkoutProfileIncompleteError):
        await _generator(value, _real_ai_service(value, provider)).generate(
            _user(), WorkoutGenerationRequest(use_ai_assistance=True)
        )
    assert provider.requests == []


@pytest.mark.asyncio
async def test_invalid_ai_allow_list_is_rejected_with_deterministic_fallback() -> None:
    value = _snapshot()
    provider = MockProvider(
        structured_payload={
            "approved_exercise_ids": ["invented_exercise"],
            "explanation": {
                "summary": "Invalid exercise payload.",
                "rationale": ["This response must be rejected."],
                "motivation": "Fallback safely.",
                "recovery_reminder": "Follow the deterministic plan.",
            },
        }
    )
    plan = await _generator(value, _real_ai_service(value, provider)).generate(
        _user(), WorkoutGenerationRequest(use_ai_assistance=True)
    )
    assert plan.metadata.fallback_reason == "ai_exercise_allow_list_mismatch"
    assert plan.metadata.mode == GenerationMode.DETERMINISTIC_FALLBACK
    assert all(
        item.exercise_id != "invented_exercise"
        for day in plan.weekly_schedule
        for section in day.sections
        for item in section.exercises
    )
    assert len(provider.requests) == 1


def test_adaptation_is_deterministic_and_never_auto_applies() -> None:
    performance = ExercisePerformance(
        exercise_id="dead_bug",
        sets=(SetResult(set_number=1, reps=8, completed=True, perceived_exertion=5),),
        pain_reported=True,
        pain_area="back",
    )
    session = WorkoutSession(
        session_id="session-1",
        user_id="user-1",
        plan_id="plan-1",
        workout_day_id="day-1",
        day_number=1,
        status=SessionStatus.COMPLETED,
        planned_exercise_ids=("dead_bug",),
        completed_exercises=(performance,),
        completion_percentage=100,
        planned_duration_minutes=40,
    )
    profile = _snapshot().profile
    assert profile is not None
    recommendation = WorkoutAdaptationEngine().evaluate((session,), profile)
    assert recommendation.action == AdaptationAction.BLOCK_TRAINING
    assert not recommendation.automatic_application_allowed


class FakeIndexCollection:
    def __init__(self) -> None:
        self.calls: list[tuple[object, dict[str, object]]] = []
        self.last_query: dict[str, object] | None = None
        self.indexes: dict[str, dict[str, object]] = {}

    async def create_index(self, keys: object, **options: object) -> None:
        self.calls.append((keys, options))
        name = str(options.get("name", ""))
        if name:
            self.indexes[name] = {"key": keys, **options}

    async def index_information(self) -> dict[str, dict[str, object]]:
        return dict(self.indexes)

    async def drop_index(self, name: str) -> None:
        self.indexes.pop(name, None)

    async def find_one(self, query: dict[str, object]) -> None:
        self.last_query = query
        return None


class FakeWorkoutDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, FakeIndexCollection] = {}

    def __getitem__(self, name: str) -> FakeIndexCollection:
        return self.collections.setdefault(name, FakeIndexCollection())


@pytest.mark.asyncio
async def test_workout_indexes_include_unique_active_owner_and_history() -> None:
    database = FakeWorkoutDatabase()
    await ensure_intelligent_workout_indexes(database)
    plan_calls = database["intelligent_workout_plans"].calls
    session_calls = database["intelligent_workout_sessions"].calls

    assert len(plan_calls) == 5
    assert len(session_calls) == 3
    assert plan_calls[1][1]["unique"] is True
    assert plan_calls[1][1]["partialFilterExpression"] == {"status": "active"}


@pytest.mark.asyncio
async def test_repository_plan_lookup_is_owner_scoped() -> None:
    database = FakeWorkoutDatabase()
    repository = MongoWorkoutRepository(cast(Any, database))

    assert await repository.get_plan("owner-1", "plan-1") is None
    assert database["intelligent_workout_plans"].last_query == {
        "plan_id": "plan-1",
        "user_id": "owner-1",
    }

    assert await repository.get_session("owner-1", "session-1") is None
    assert database["intelligent_workout_sessions"].last_query == {
        "session_id": "session-1",
        "user_id": "owner-1",
    }


class FailingPlanReplacementCollection:
    def __init__(self, plan: WorkoutPlan) -> None:
        self.document = plan.model_dump(mode="python", exclude_computed_fields=True)

    async def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        return (
            dict(self.document)
            if all(self.document.get(key) == value for key, value in query.items())
            else None
        )

    async def update_many(
        self, query: dict[str, object], update: dict[str, dict[str, object]]
    ) -> None:
        if all(self.document.get(key) == value for key, value in query.items()):
            self.document.update(update["$set"])

    async def insert_one(self, _document: dict[str, object]) -> None:
        raise RuntimeError("simulated insert failure")

    async def update_one(
        self, query: dict[str, object], update: dict[str, dict[str, object]]
    ) -> SimpleNamespace:
        matched = all(self.document.get(key) == value for key, value in query.items())
        if matched:
            self.document.update(update["$set"])
        return SimpleNamespace(matched_count=int(matched))


class FailingPlanReplacementDatabase:
    def __init__(self, plan: WorkoutPlan) -> None:
        self.plans = FailingPlanReplacementCollection(plan)
        self.sessions = FakeIndexCollection()

    def __getitem__(self, name: str) -> object:
        return self.plans if name == "intelligent_workout_plans" else self.sessions


@pytest.mark.asyncio
async def test_repository_compensates_when_active_plan_replacement_insert_fails() -> None:
    current = await _generator(_snapshot()).generate(_user(), WorkoutGenerationRequest())
    database = FailingPlanReplacementDatabase(current)
    repository = MongoWorkoutRepository(cast(Any, database))
    replacement = current.model_copy(update={"plan_id": "plan-2"})

    with pytest.raises(WorkoutPersistenceError) as caught:
        await repository.replace_active_plan(replacement)

    assert caught.value.compensation_succeeded
    assert database.plans.document["plan_id"] == current.plan_id
    assert database.plans.document["status"] == WorkoutStatus.ACTIVE.value


def test_catalog_rejects_duplicates_and_invalid_required_metadata() -> None:
    catalog = ExerciseCatalog()
    with pytest.raises(ValueError, match="unique"):
        ExerciseCatalog(catalog.all() + (catalog.all()[0],))

    payload = catalog.all()[0].model_dump()
    payload["instructions"] = ()
    with pytest.raises(ValidationError):
        type(catalog.all()[0]).model_validate(payload)
    payload = catalog.all()[0].model_dump()
    payload["default_rep_range"] = (12, 8)
    with pytest.raises(ValidationError):
        type(catalog.all()[0]).model_validate(payload)


def test_catalog_supports_required_equipment_locations_and_conditioning() -> None:
    catalog = ExerciseCatalog().all()
    equipment = {item for exercise in catalog for item in exercise.equipment}
    locations = {item for exercise in catalog for item in exercise.suitable_locations}
    required_equipment = {
        Equipment.BODYWEIGHT,
        Equipment.DUMBBELL,
        Equipment.BARBELL,
        Equipment.RESISTANCE_BAND,
        Equipment.CABLE,
        Equipment.MACHINE,
        Equipment.BENCH,
        Equipment.PULL_UP_BAR,
        Equipment.KETTLEBELL,
        Equipment.CARDIO_MACHINE,
    }
    assert required_equipment.issubset(equipment)
    assert set(ExerciseLocation).issubset(locations)
    assert any(item.movement_pattern == MovementPattern.CONDITIONING for item in catalog)


@pytest.mark.parametrize(
    ("context_updates", "expected"),
    [
        ({"pain_areas": frozenset({"knee"})}, RejectionReason.PAIN_AREA_CONFLICT),
        (
            {"mobility_limitations": frozenset({"hip"})},
            RejectionReason.INSUFFICIENT_MOBILITY,
        ),
        (
            {"chronic_conditions": frozenset({"heart disease"})},
            RejectionReason.CHRONIC_CONDITION_CONFLICT,
        ),
        ({"medically_cleared": False}, RejectionReason.CLEARANCE_RESTRICTION),
    ],
)
def test_selector_emits_health_and_clearance_rejection_codes(
    context_updates: dict[str, object], expected: RejectionReason
) -> None:
    values: dict[str, object] = {
        "equipment": frozenset(Equipment),
        "locations": frozenset(ExerciseLocation),
        "experience": ExperienceLevel.ADVANCED,
        "remaining_minutes": 120,
    }
    values.update(context_updates)
    context = SelectionContext.model_validate(values)
    result = ExerciseSelector().select(ExerciseCatalog().all(), context, tuple(MovementPattern))
    assert expected in {reason for item in result.rejections for reason in item.reasons}


def test_selector_is_deterministic_and_returns_approved_alternatives() -> None:
    context = SelectionContext(
        equipment=frozenset(Equipment),
        locations=frozenset(ExerciseLocation),
        experience=ExperienceLevel.ADVANCED,
        remaining_minutes=120,
    )
    selector = ExerciseSelector()
    patterns = (MovementPattern.PUSH, MovementPattern.PULL, MovementPattern.CORE)
    first = selector.select(ExerciseCatalog().all(), context, patterns)
    second = selector.select(ExerciseCatalog().all(), context, patterns)
    assert first == second
    assert first.metadata.selected_count == 3
    assert all(
        ExerciseCatalog().get(alternative_id) is not None
        for item in first.alternatives
        for alternative_id in item.approved_alternative_ids
    )


@pytest.mark.parametrize(
    ("goal", "expected_reps", "expected_rest"),
    [
        (TrainingGoal.STRENGTH, (4, 6), 120),
        (TrainingGoal.FAT_LOSS, (10, 15), 45),
        (TrainingGoal.MUSCLE_GAIN, (8, 12), 75),
        (TrainingGoal.FOOTBALL_PERFORMANCE, (6, 10), 75),
    ],
)
def test_planner_owns_goal_prescriptions(
    goal: TrainingGoal, expected_reps: tuple[int, int], expected_rest: int
) -> None:
    value = _snapshot(goal=goal)
    readiness = ReadinessChecker(clock=lambda: NOW).check(value)
    constraints = WorkoutPlanner().create_constraints(value, readiness)
    assert (constraints.prescription.min_reps, constraints.prescription.max_reps) == expected_reps
    assert constraints.prescription.rest_seconds == expected_rest


@pytest.mark.asyncio
async def test_generated_schedule_enforces_recovery_sections_and_volume() -> None:
    value = _snapshot(days=6, experience=ExperienceLevel.ADVANCED)
    plan = await _generator(value).generate(_user(), WorkoutGenerationRequest())
    weekdays = tuple(day.weekday for day in plan.weekly_schedule)
    assert weekdays == (1, 2, 4, 5, 7)
    assert all(
        {SectionType.WARMUP, SectionType.MAIN, SectionType.COOLDOWN}.issubset(
            {section.section_type for section in day.sections}
        )
        for day in plan.weekly_schedule
    )
    assert all(
        4 <= sum(len(section.exercises) for section in day.sections) <= 8
        for day in plan.weekly_schedule
    )


@pytest.mark.asyncio
async def test_caution_readiness_continues_with_warning_and_conservative_plan() -> None:
    injury = InjuryRecord(
        area="shoulder",
        description="minor irritation",
        severity=HealthSeverity.MILD,
        active=True,
        medically_cleared=False,
    )
    value = _snapshot(injury=injury, experience=ExperienceLevel.ADVANCED, days=6)
    plan = await _generator(value).generate(_user(), WorkoutGenerationRequest())
    assert plan.metadata.readiness_status.value == "caution"
    assert plan.training_days_per_week == 4
    assert any(item.professional_guidance for item in plan.warnings)


def _approved_ids(plan: object) -> tuple[str, ...]:
    assert hasattr(plan, "weekly_schedule")
    return tuple(
        item.exercise_id
        for day in plan.weekly_schedule
        for section in day.sections
        for item in section.exercises
    )


def _real_ai_service(
    snapshot_value: UserIntelligenceSnapshot,
    provider: MockProvider,
) -> AIService:
    source = SnapshotReader(snapshot_value)
    readiness = ReadinessChecker(clock=lambda: NOW)
    return AIService(
        provider=provider,
        context_builder=UserIntelligenceContextBuilder(source, readiness, clock=lambda: NOW),
        safety_engine=AISafetyEngine(clock=lambda: NOW),
    )


@pytest.mark.asyncio
async def test_ai_assistance_uses_mock_provider_after_valid_base_plan() -> None:
    value = _snapshot()
    base = await _generator(value).generate(_user(), WorkoutGenerationRequest())
    provider = MockProvider(
        structured_payload={
            "approved_exercise_ids": list(_approved_ids(base)),
            "explanation": {
                "summary": "Your validated plan balances training and recovery.",
                "rationale": ["All exercise IDs were pre-approved by deterministic rules."],
                "motivation": "Build consistency one safe session at a time.",
                "recovery_reminder": "Respect the planned recovery days.",
            },
        }
    )
    plan = await _generator(value, _real_ai_service(value, provider)).generate(
        _user(), WorkoutGenerationRequest(use_ai_assistance=True)
    )
    assert plan.metadata.mode == GenerationMode.AI_ASSISTED
    assert plan.explanation.summary.startswith("Your validated")
    assert len(provider.requests) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode",
    [MockProviderMode.TIMEOUT, MockProviderMode.RATE_LIMITED, MockProviderMode.UNAVAILABLE],
)
async def test_provider_failures_use_valid_deterministic_fallback(mode: MockProviderMode) -> None:
    value = _snapshot()
    provider = MockProvider(mode=mode)
    plan = await _generator(value, _real_ai_service(value, provider)).generate(
        _user(), WorkoutGenerationRequest(use_ai_assistance=True)
    )
    assert plan.metadata.mode == GenerationMode.DETERMINISTIC_FALLBACK
    assert WorkoutValidator().validate(plan, value, ExerciseCatalog()).valid


@pytest.mark.asyncio
async def test_invalid_mock_provider_json_falls_back_without_persisting_raw_output() -> None:
    value = _snapshot()
    provider = MockProvider(structured_payload={"unknown": "value"})
    plan = await _generator(value, _real_ai_service(value, provider)).generate(
        _user(), WorkoutGenerationRequest(use_ai_assistance=True)
    )
    assert plan.metadata.mode == GenerationMode.DETERMINISTIC_FALLBACK
    assert plan.metadata.fallback_reason == "AIValidationError"


@pytest.mark.asyncio
async def test_validator_rejects_unknown_exercise_duplicate_and_unsafe_progression() -> None:
    value = _snapshot()
    plan = await _generator(value).generate(_user(), WorkoutGenerationRequest())
    day = plan.weekly_schedule[0]
    main = day.section(SectionType.MAIN)
    assert main is not None
    unsafe = main.exercises[0].model_copy(
        update={
            "exercise_id": "unknown_ai_exercise",
            "prescription": main.exercises[0].prescription.model_copy(
                update={"progression_limit_percentage": 50.0}
            ),
        }
    )
    changed_main = main.model_copy(update={"exercises": (unsafe, unsafe) + main.exercises[1:]})
    changed_sections = tuple(
        changed_main if section.section_type == SectionType.MAIN else section
        for section in day.sections
    )
    changed_day = day.model_copy(update={"sections": changed_sections})
    changed_plan = plan.model_copy(
        update={"weekly_schedule": (changed_day,) + plan.weekly_schedule[1:]}
    )
    result = WorkoutValidator().validate(changed_plan, value, ExerciseCatalog())
    assert result.status == WorkoutValidationStatus.INVALID
    assert {item.code for item in result.errors}.issuperset(
        {"exercise.unknown", "exercise.duplicate"}
    )


class InMemoryWorkoutRepository:
    def __init__(self, plan: WorkoutPlan) -> None:
        self.plan = plan
        self.sessions: list[WorkoutSession] = []

    async def create(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.plan = plan
        return plan

    async def replace_active_plan(self, plan: WorkoutPlan) -> WorkoutPlan:
        self.plan = plan
        return plan

    async def get_active_plan(self, user_id: str) -> WorkoutPlan | None:
        return (
            self.plan
            if self.plan.user_id == user_id and self.plan.status == WorkoutStatus.ACTIVE
            else None
        )

    async def get_by_id(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        return self.plan if self.plan.user_id == user_id and self.plan.plan_id == plan_id else None

    async def list_user_plans(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutPlan, ...]:
        return (self.plan,) if self.plan.user_id == user_id else ()

    async def activate_plan(self, user_id: str, plan_id: str) -> WorkoutPlan | None:
        plan = await self.get_by_id(user_id, plan_id)
        if plan is not None:
            self.plan = plan.model_copy(
                update={"status": WorkoutStatus.ACTIVE, "archived_at": None}
            )
        return plan

    async def archive_plan(self, user_id: str, plan_id: str) -> bool:
        plan = await self.get_by_id(user_id, plan_id)
        if plan is None:
            return False
        self.plan = plan.model_copy(update={"status": WorkoutStatus.ARCHIVED, "archived_at": NOW})
        return True

    async def get_version_history(
        self, user_id: str, generation_key: str
    ) -> tuple[WorkoutPlan, ...]:
        return (
            (self.plan,)
            if self.plan.user_id == user_id
            and self.plan.generation_metadata.generation_key == generation_key
            else ()
        )

    async def save_session(self, session: WorkoutSession) -> WorkoutSession:
        self.sessions.append(session)
        return session

    async def update_session(self, session: WorkoutSession) -> WorkoutSession | None:
        for index, item in enumerate(self.sessions):
            if item.user_id == session.user_id and item.session_id == session.session_id:
                self.sessions[index] = session
                return session
        return None

    async def get_session(self, user_id: str, session_id: str) -> WorkoutSession | None:
        return next(
            (
                item
                for item in self.sessions
                if item.user_id == user_id and item.session_id == session_id
            ),
            None,
        )

    async def list_sessions(
        self, user_id: str, plan_id: str | None = None, limit: int = 20, offset: int = 0
    ) -> tuple[WorkoutSession, ...]:
        return tuple(
            item
            for item in self.sessions
            if item.user_id == user_id and (plan_id is None or item.plan_id == plan_id)
        )[offset : offset + limit]


@pytest.mark.asyncio
async def test_service_calculates_progress_and_flags_pain_instead_of_trusting_client() -> None:
    plan = await _generator(_snapshot()).generate(_user(), WorkoutGenerationRequest())
    repository = InMemoryWorkoutRepository(plan)
    service = WorkoutService(
        repository,
        cast(Any, None),
        id_factory=lambda: "session-1",
        clock=lambda: NOW,
    )
    first = plan.weekly_schedule[0].sections[0].exercises[0]
    response = await service.record_session(
        _user(),
        RecordWorkoutSessionRequest(
            plan_id=plan.plan_id,
            day_number=1,
            status=SessionStatus.COMPLETED,
            completed_exercises=(
                CompletedExercise(
                    exercise_id=first.exercise_id,
                    completed_sets=(
                        CompletedSet(
                            set_number=1,
                            actual_reps=8,
                            perceived_exertion=6,
                            completed=True,
                        ),
                    ),
                    pain_reported=True,
                    pain_area="shoulder",
                ),
            ),
        ),
    )
    assert 0 < response.completion_percentage < 100
    assert response.adaptation_flags == ("pain_requires_review",)
    assert response.skipped_exercise_ids
    assert (await service.get_session(_user(), "session-1")).session_id == "session-1"


@pytest.mark.asyncio
async def test_service_updates_in_progress_session_and_prevents_terminal_reopen() -> None:
    plan = await _generator(_snapshot()).generate(_user(), WorkoutGenerationRequest())
    repository = InMemoryWorkoutRepository(plan)
    service = WorkoutService(
        repository,
        cast(Any, None),
        id_factory=lambda: "session-1",
        clock=lambda: NOW,
    )
    exercise = plan.weekly_schedule[0].sections[0].exercises[0]
    await service.record_session(
        _user(),
        RecordWorkoutSessionRequest(
            plan_id=plan.plan_id,
            day_number=1,
            status=SessionStatus.IN_PROGRESS,
            completed_exercises=(),
        ),
    )
    assert repository.sessions[0].skipped_exercise_ids == ()

    completed = await service.update_session(
        _user(),
        "session-1",
        UpdateWorkoutSessionRequest(
            status=SessionStatus.COMPLETED,
            completed_exercises=(
                CompletedExercise(
                    exercise_id=exercise.exercise_id,
                    completed_sets=(CompletedSet(set_number=1, completed=True),),
                ),
            ),
            actual_duration_minutes=30,
        ),
    )
    assert completed.status == SessionStatus.COMPLETED
    assert completed.completed_at == NOW
    with pytest.raises(WorkoutSessionStateError):
        await service.update_session(
            _user(),
            "session-1",
            UpdateWorkoutSessionRequest(status=SessionStatus.IN_PROGRESS),
        )


@pytest.mark.asyncio
async def test_service_rejects_excess_sets_unknown_exercises_and_archived_plans() -> None:
    plan = await _generator(_snapshot()).generate(_user(), WorkoutGenerationRequest())
    repository = InMemoryWorkoutRepository(plan)
    service = WorkoutService(repository, cast(Any, None))
    exercise = plan.weekly_schedule[0].sections[0].exercises[0]
    too_many_sets = tuple(
        CompletedSet(set_number=index, actual_reps=5, completed=True)
        for index in range(1, exercise.prescription.sets + 2)
    )
    with pytest.raises(WorkoutExerciseUnavailableError):
        await service.record_session(
            _user(),
            RecordWorkoutSessionRequest(
                plan_id=plan.plan_id,
                day_number=1,
                status=SessionStatus.COMPLETED,
                completed_exercises=(
                    CompletedExercise(
                        exercise_id=exercise.exercise_id,
                        completed_sets=too_many_sets,
                    ),
                ),
            ),
        )
    repository.plan = plan.model_copy(update={"status": WorkoutStatus.ARCHIVED, "archived_at": NOW})
    with pytest.raises(WorkoutPlanArchivedError):
        await service.record_session(
            _user(),
            RecordWorkoutSessionRequest(
                plan_id=plan.plan_id,
                day_number=1,
                status=SessionStatus.COMPLETED,
                completed_exercises=(),
            ),
        )


def _adaptation_session(
    identifier: str,
    *,
    completion: int = 100,
    status: SessionStatus = SessionStatus.COMPLETED,
    rpe: int = 6,
    duration: int = 40,
    skipped: tuple[str, ...] = (),
) -> WorkoutSession:
    return WorkoutSession(
        session_id=identifier,
        user_id="user-1",
        plan_id="plan-1",
        workout_day_id="day-1",
        day_number=1,
        status=status,
        planned_exercise_ids=("dead_bug",),
        completed_exercises=(
            CompletedExercise(
                exercise_id="dead_bug",
                completed_sets=(
                    CompletedSet(
                        set_number=1,
                        actual_reps=8,
                        perceived_exertion=rpe,
                        completed=True,
                    ),
                ),
            ),
        ),
        skipped_exercise_ids=skipped,
        completion_percentage=completion,
        planned_duration_minutes=40,
        actual_duration_minutes=duration,
    )


@pytest.mark.parametrize(
    ("sessions", "readiness", "expected"),
    [
        (
            (_adaptation_session("1", rpe=9), _adaptation_session("2", rpe=9)),
            (),
            AdaptationAction.REDUCE_INTENSITY,
        ),
        (
            (_adaptation_session("1", completion=20), _adaptation_session("2", completion=40)),
            (),
            AdaptationAction.REDUCE_VOLUME,
        ),
        (
            (
                _adaptation_session("1", status=SessionStatus.ABANDONED),
                _adaptation_session("2", status=SessionStatus.ABANDONED),
            ),
            (),
            AdaptationAction.ADD_RECOVERY_DAY,
        ),
        (
            (_adaptation_session("1", duration=60), _adaptation_session("2", duration=60)),
            (),
            AdaptationAction.SHORTEN_SESSION,
        ),
        (
            (
                _adaptation_session("1", skipped=("dead_bug",)),
                _adaptation_session("2", skipped=("dead_bug",)),
            ),
            (),
            AdaptationAction.REPLACE_EXERCISE,
        ),
        (
            (_adaptation_session("1"),),
            (ReadinessStatus.BLOCKED,),
            AdaptationAction.BLOCK_TRAINING,
        ),
        (
            (_adaptation_session("1"),),
            (),
            AdaptationAction.MAINTAIN_PLAN,
        ),
    ],
)
def test_adaptation_signals_are_deterministic_and_auditable(
    sessions: tuple[WorkoutSession, ...],
    readiness: tuple[ReadinessStatus, ...],
    expected: AdaptationAction,
) -> None:
    profile = _snapshot().profile
    assert profile is not None
    recommendation = WorkoutAdaptationEngine().evaluate(sessions, profile, readiness)
    assert recommendation.action == expected
    assert recommendation.reason_code
    assert recommendation.evidence_summary
    if expected in {AdaptationAction.BLOCK_TRAINING, AdaptationAction.REQUIRE_REVIEW}:
        assert not recommendation.automatic_application_allowed
