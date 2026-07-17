from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.ai.decision_rules import (
    calculate_data_quality_score,
    calculate_decision_confidence,
    calculate_fatigue_score,
    calculate_injury_risk_score,
    calculate_nutrition_adherence_score,
    calculate_overall_health_score,
    calculate_progress_score,
    calculate_readiness_score,
    calculate_recovery_score,
    calculate_workout_adherence_score,
)
from app.health.models import (
    ChronicConditionRecord,
    HealthProfile,
    HealthSeverity,
    InjuryRecord,
    PainAreaRecord,
)
from app.models.ai_decision import (
    DailyDecision,
    DecisionMetadata,
    DecisionStatus,
    InjuryDecision,
    NutritionDecision,
    RecoveryDecision,
    TrainingDecision,
)
from app.models.nutrition import (
    ActivityLevel,
    NutritionProgress,
)
from app.models.user import User
from app.models.workout import (
    Equipment,
    ExperienceLevel,
    TrainingGoal,
    TrainingLocation,
)
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
from app.repositories.ai_decisions import AIDecisionRepository
from app.services.ai_decision import AIDecisionEngineService

# --- UNIT TESTS FOR scoring rules ---


def test_calculate_readiness_score() -> None:
    # Ideal conditions: 8h sleep, stress=1, fatigue=1, soreness=1, adherence=100
    # Penalty calculation: no sleep penalty (sleep>=7), no stress penalty (stress<=4),
    # no fatigue penalty (fatigue<=3), no soreness penalty (soreness<=3), no adherence penalty.
    score = calculate_readiness_score(8.0, 1, 1, 1, 100.0)
    assert score == 100

    # Test sleep penalties
    # Sleep 6h: -10 * (7-6) = -10. Score = 90
    score = calculate_readiness_score(6.0, 1, 1, 1, 100.0)
    assert score == 90

    # Sleep 4.5h: -10 * (7-4.5) = -25, and extra -15 for < 5h = -40. Score = 60
    score = calculate_readiness_score(4.5, 1, 1, 1, 100.0)
    assert score == 60

    # Test stress penalties
    # Stress 6 (stress > 4): -5 * (6-4) = -10. Score = 90
    score = calculate_readiness_score(8.0, 6, 1, 1, 100.0)
    assert score == 90

    # Test fatigue penalties
    # Fatigue 6 (fatigue > 3): -8 * (6-3) = -24. Score = 76
    score = calculate_readiness_score(8.0, 1, 6, 1, 100.0)
    assert score == 76

    # Test soreness penalties
    # Soreness 6 (soreness > 3): -6 * (6-3) = -18. Score = 82
    score = calculate_readiness_score(8.0, 1, 1, 6, 100.0)
    assert score == 82

    # Test adherence penalties
    # Adherence 40% (<50%): -15. Score = 85
    score = calculate_readiness_score(8.0, 1, 1, 1, 40.0)
    assert score == 85

    # Test cumulative penalties clamped to 0
    score = calculate_readiness_score(3.0, 10, 10, 10, 10.0)
    assert score == 0


def test_calculate_recovery_score() -> None:
    # Baseline 80. sleep_quality=8 -> +20. fatigue=2 -> -10. soreness=2 -> -8. stress=2 -> -4.
    # Score = 80 + 20 - 10 - 8 - 4 = 78
    score = calculate_recovery_score(8.0, 8, 2, 2, 2)
    assert score == 78

    # Quality = 3 -> -20. fatigue=5 -> -25. soreness=5 -> -20. stress=5 -> -10.
    # Score = 80 - 20 - 25 - 20 - 10 = 5
    score = calculate_recovery_score(6.0, 3, 5, 5, 5)
    assert score == 5

    # Clamping
    score = calculate_recovery_score(5.0, 1, 10, 10, 10)
    assert score == 0


def test_calculate_nutrition_adherence_score() -> None:
    # Exact match: 100
    score = calculate_nutrition_adherence_score(2000, 2000, 150.0, 150.0)
    assert score == 100

    # 10% calorie deviation (200 cal), 20% protein deviation (30g)
    # CalorieDev = 10%, ProteinDev = 20%
    # Penalty = 0.5 * 10 + 0.5 * 20 = 15. Score = 85
    score = calculate_nutrition_adherence_score(2000, 1800, 150.0, 120.0)
    assert score == 85

    # Zero targets
    assert calculate_nutrition_adherence_score(0, 2000, 150.0, 150.0) == 0


def test_calculate_workout_adherence_score() -> None:
    assert calculate_workout_adherence_score([100.0, 80.0, 0.0]) == 60
    assert calculate_workout_adherence_score([]) == 0


def test_calculate_injury_risk_score() -> None:
    # No pain, no injuries, no limits
    score = calculate_injury_risk_score({}, [], 0)
    assert score == 0

    # Pain area 6 (moderate, >=5): +20
    # Pain area 9 (severe, >=8): +50
    # Uncleared injury: +35
    # Cleared injury: +10
    # Mobility limit: +10
    score = calculate_injury_risk_score(
        {"knee": 6, "shoulder": 9},
        [{"active": True, "medically_cleared": False}, {"active": True, "medically_cleared": True}],
        2,
    )
    # Expected: 20 (knee pain) + 50 (shoulder pain) + 35 (uncleared) + 10 (cleared) + 2 * 10 (mobility) = 135 -> clamp 100
    assert score == 100


def test_calculate_fatigue_score() -> None:
    # Fatigue 5, sleep 8 (no penalty), stress 4 (no penalty)
    assert calculate_fatigue_score(5, 8.0, 4) == 50

    # Fatigue 7, sleep 4.5 (+20), stress 8 (+15)
    assert calculate_fatigue_score(7, 4.5, 8) == 100  # -> clamp 100
    assert calculate_fatigue_score(7, 4.5, 8) == 100


def test_calculate_progress_score() -> None:
    # Fat loss weight down
    assert calculate_progress_score(-1.5, "fat_loss") == 100
    # Fat loss weight up (2% weight gain) -> penalty 2 * 50 = 100 -> score 0
    assert calculate_progress_score(2.0, "fat_loss") == 0

    # Muscle gain weight up
    assert calculate_progress_score(1.0, "muscle_gain") == 100
    # Muscle gain weight down
    assert calculate_progress_score(-1.0, "muscle_gain") == 50


def test_calculate_overall_health_score() -> None:
    # readiness=80, recovery=80, adherence=80, injury=20
    score = calculate_overall_health_score(80, 80, 80, 80, 20)
    # 0.3*80 + 0.2*80 + 0.2*80 + 0.15*80 + 0.15*80 = 80
    assert score == 80


def test_calculate_data_quality_score() -> None:
    assert calculate_data_quality_score(100, True, True, True) == 100
    assert calculate_data_quality_score(50, False, False, False) == 20


def test_calculate_decision_confidence() -> None:
    assert calculate_decision_confidence(90, 80, False) == 90
    assert calculate_decision_confidence(90, 30, True) == 60  # 90 - 20 - 10


# --- BUSINESS SERVICE TESTS ORCHESTRATION ---


@pytest.mark.asyncio
async def test_generate_decision_needs_info_when_profile_missing() -> None:
    # Setup mocks
    decision_repo = MagicMock(spec=AIDecisionRepository)
    profile_repo = MagicMock()
    health_repo = MagicMock()
    workout_repo = MagicMock()
    nutrition_repo = MagicMock()

    # Empty user profiles
    profile_repo.get_by_user_id = AsyncMock(return_value=None)
    health_repo.get_by_user_id = AsyncMock(return_value=None)
    workout_repo.get_active_plan = AsyncMock(return_value=None)
    workout_repo.list_sessions = AsyncMock(return_value=())
    nutrition_repo.get_progress = AsyncMock(
        side_effect=lambda user_id, day: NutritionProgress(
            date=day,
            calories_consumed=0,
            protein_consumed=0,
            carbohydrates_consumed=0,
            fat_consumed=0,
            water_consumed_ml=0,
            meals_completed=0,
        )
    )

    service = AIDecisionEngineService(
        decision_repo=decision_repo,
        profile_repo=profile_repo,
        health_repo=health_repo,
        workout_repo=workout_repo,
        nutrition_repo=nutrition_repo,
    )

    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="***",
        is_active=True,
        token_version=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    decision_repo.find_active_by_date = AsyncMock(return_value=None)
    decision_repo.supersede_previous_decisions = AsyncMock()
    decision_repo.save = AsyncMock(side_effect=lambda d: d)

    decision = await service.get_or_generate_decision(user, date.today())

    assert decision.status == DecisionStatus.NEEDS_INFO
    assert "profile" in decision.metadata.missing_inputs
    assert "health_profile" in decision.metadata.missing_inputs
    assert "personalization" in decision.human_readable_explanation_en


@pytest.mark.asyncio
async def test_generate_decision_blocked_on_urgent_pain() -> None:
    # Setup mocks
    decision_repo = MagicMock(spec=AIDecisionRepository)
    profile_repo = MagicMock()
    health_repo = MagicMock()
    workout_repo = MagicMock()
    nutrition_repo = MagicMock()

    # User profile Mock
    profile = UserProfile(
        id="prof_1",
        user_id="test_user_123",
        identity=IdentityProfile(full_name="John Doe", age=30, gender=Gender.MALE, country="US"),
        body=BodyProfile(height_cm=180.0, weight_kg=80.0),
        goals=GoalsProfile(primary_goal=TrainingGoal.FAT_LOSS),
        training=TrainingProfile(
            experience=ExperienceLevel.BEGINNER,
            available_days=3,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.BODYWEIGHT),
            workout_location=TrainingLocation.HOME_GYM,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=8.0,
            stress_level=2,
            activity_level=ActivityLevel.MODERATE,
            daily_water_ml=2000,
        ),
        nutrition=NutritionProfile(dietary_preferences=(), allergies=(), dietary_restrictions=()),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Health profile containing severe pain (intensity = 9)
    health = HealthProfile(
        id="h_1",
        user_id="test_user_123",
        injuries=(),
        chronic_conditions=(),
        pain_areas=(PainAreaRecord(area="chest", intensity=9, movement_related=False),),
        mobility_limitations=(),
        surgery_history=(),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    profile_repo.get_by_user_id = AsyncMock(return_value=profile)
    health_repo.get_by_user_id = AsyncMock(return_value=health)
    workout_repo.get_active_plan = AsyncMock(return_value=None)
    workout_repo.list_sessions = AsyncMock(return_value=())
    nutrition_repo.get_progress = AsyncMock(
        side_effect=lambda user_id, day: NutritionProgress(
            date=day,
            calories_consumed=0,
            protein_consumed=0,
            carbohydrates_consumed=0,
            fat_consumed=0,
            water_consumed_ml=0,
            meals_completed=0,
        )
    )

    service = AIDecisionEngineService(
        decision_repo=decision_repo,
        profile_repo=profile_repo,
        health_repo=health_repo,
        workout_repo=workout_repo,
        nutrition_repo=nutrition_repo,
    )

    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="***",
        is_active=True,
        token_version=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    decision_repo.find_active_by_date = AsyncMock(return_value=None)
    decision_repo.supersede_previous_decisions = AsyncMock()
    decision_repo.save = AsyncMock(side_effect=lambda d: d)

    decision = await service.get_or_generate_decision(user, date.today())

    assert decision.status == DecisionStatus.BLOCKED
    assert decision.training.action == "block_training"
    assert decision.training.volume_multiplier == 0.0
    assert "Urgent physical symptoms" in decision.reason_codes[0].message_en
    assert "أعراض جسدية حرجة" in decision.reason_codes[0].message_ar


@pytest.mark.asyncio
async def test_generate_decision_restricted_on_injury() -> None:
    # Setup mocks
    decision_repo = MagicMock(spec=AIDecisionRepository)
    profile_repo = MagicMock()
    health_repo = MagicMock()
    workout_repo = MagicMock()
    nutrition_repo = MagicMock()

    profile = UserProfile(
        id="prof_1",
        user_id="test_user_123",
        identity=IdentityProfile(full_name="John Doe", age=30, gender=Gender.MALE, country="US"),
        body=BodyProfile(height_cm=180.0, weight_kg=80.0),
        goals=GoalsProfile(primary_goal=TrainingGoal.FAT_LOSS),
        training=TrainingProfile(
            experience=ExperienceLevel.BEGINNER,
            available_days=3,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.BODYWEIGHT),
            workout_location=TrainingLocation.HOME_GYM,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=8.0,
            stress_level=2,
            activity_level=ActivityLevel.MODERATE,
            daily_water_ml=2000,
        ),
        nutrition=NutritionProfile(dietary_preferences=(), allergies=(), dietary_restrictions=()),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Health profile containing active uncleared knee injury
    health = HealthProfile(
        id="h_1",
        user_id="test_user_123",
        injuries=(
            InjuryRecord(
                area="knee",
                description="Knee sprain",
                active=True,
                medically_cleared=True,
                severity=HealthSeverity.MODERATE,
            ),
        ),
        chronic_conditions=(),
        pain_areas=(),
        mobility_limitations=(),
        surgery_history=(),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    profile_repo.get_by_user_id = AsyncMock(return_value=profile)
    health_repo.get_by_user_id = AsyncMock(return_value=health)
    workout_repo.get_active_plan = AsyncMock(return_value=None)
    workout_repo.list_sessions = AsyncMock(return_value=())
    nutrition_repo.get_progress = AsyncMock(
        side_effect=lambda user_id, day: NutritionProgress(
            date=day,
            calories_consumed=0,
            protein_consumed=0,
            carbohydrates_consumed=0,
            fat_consumed=0,
            water_consumed_ml=0,
            meals_completed=0,
        )
    )

    service = AIDecisionEngineService(
        decision_repo=decision_repo,
        profile_repo=profile_repo,
        health_repo=health_repo,
        workout_repo=workout_repo,
        nutrition_repo=nutrition_repo,
    )

    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="***",
        is_active=True,
        token_version=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    decision_repo.find_active_by_date = AsyncMock(return_value=None)
    decision_repo.supersede_previous_decisions = AsyncMock()
    decision_repo.save = AsyncMock(side_effect=lambda d: d)

    decision = await service.get_or_generate_decision(user, date.today())

    assert decision.status == DecisionStatus.RESTRICTED
    assert "knee" in decision.injury.blocked_movements
    assert decision.training.action == "replace_exercise"


@pytest.mark.asyncio
async def test_generate_decision_idempotency_check() -> None:
    decision_repo = MagicMock(spec=AIDecisionRepository)
    profile_repo = MagicMock()
    health_repo = MagicMock()
    workout_repo = MagicMock()
    nutrition_repo = MagicMock()

    profile = UserProfile(
        id="prof_1",
        user_id="test_user_123",
        identity=IdentityProfile(full_name="John Doe", age=30, gender=Gender.MALE, country="US"),
        body=BodyProfile(height_cm=180.0, weight_kg=80.0),
        goals=GoalsProfile(primary_goal=TrainingGoal.FAT_LOSS),
        training=TrainingProfile(
            experience=ExperienceLevel.BEGINNER,
            available_days=3,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.BODYWEIGHT),
            workout_location=TrainingLocation.HOME_GYM,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=8.0,
            stress_level=2,
            activity_level=ActivityLevel.MODERATE,
            daily_water_ml=2000,
        ),
        nutrition=NutritionProfile(dietary_preferences=(), allergies=(), dietary_restrictions=()),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    health = HealthProfile(
        id="h_1",
        user_id="test_user_123",
        injuries=(),
        chronic_conditions=(),
        pain_areas=(),
        mobility_limitations=(),
        surgery_history=(),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    profile_repo.get_by_user_id = AsyncMock(return_value=profile)
    health_repo.get_by_user_id = AsyncMock(return_value=health)
    workout_repo.get_active_plan = AsyncMock(return_value=None)
    workout_repo.list_sessions = AsyncMock(return_value=())
    nutrition_repo.get_progress = AsyncMock(
        side_effect=lambda user_id, day: NutritionProgress(
            date=day,
            calories_consumed=0,
            protein_consumed=0,
            carbohydrates_consumed=0,
            fat_consumed=0,
            water_consumed_ml=0,
            meals_completed=0,
        )
    )

    service = AIDecisionEngineService(
        decision_repo=decision_repo,
        profile_repo=profile_repo,
        health_repo=health_repo,
        workout_repo=workout_repo,
        nutrition_repo=nutrition_repo,
    )

    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="***",
        is_active=True,
        token_version=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Existing decision cache HIT mock
    cached_decision = DailyDecision(
        id="cached_id",
        user_id="test_user_123",
        effective_date=date.today(),
        status=DecisionStatus.APPROVED,
        human_readable_explanation_en="Stables.",
        human_readable_explanation_ar="مستقر.",
        training=TrainingDecision(
            action="continue_plan", safety_justification="Safe", confidence=100
        ),
        nutrition=NutritionDecision(action="keep_targets", explanation="Safe"),
        recovery=RecoveryDecision(guidance="normal_recovery"),
        injury=InjuryDecision(),
        metadata=DecisionMetadata(
            effective_date=date.today(), data_quality_score=100, confidence_score=100
        ),
        input_snapshot_hash="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  # dummy correct hash
    )

    # Injecting the correct hash to mock
    # Calculate what hash service expects
    expect_hash = service._calculate_snapshot_hash(
        profile,
        health,
        None,
        (),
        [
            NutritionProgress(
                date=date.today() - timedelta(days=1),
                calories_consumed=0,
                protein_consumed=0,
                carbohydrates_consumed=0,
                fat_consumed=0,
                water_consumed_ml=0,
                meals_completed=0,
            ),
            NutritionProgress(
                date=date.today() - timedelta(days=2),
                calories_consumed=0,
                protein_consumed=0,
                carbohydrates_consumed=0,
                fat_consumed=0,
                water_consumed_ml=0,
                meals_completed=0,
            ),
            NutritionProgress(
                date=date.today() - timedelta(days=3),
                calories_consumed=0,
                protein_consumed=0,
                carbohydrates_consumed=0,
                fat_consumed=0,
                water_consumed_ml=0,
                meals_completed=0,
            ),
        ],
    )
    cached_decision = cached_decision.model_copy(update={"input_snapshot_hash": expect_hash})

    decision_repo.find_active_by_date = AsyncMock(return_value=cached_decision)
    decision = await service.get_or_generate_decision(user, date.today(), force_regenerate=False)

    assert decision.id == "cached_id"
    decision_repo.save.assert_not_called()


@pytest.mark.asyncio
async def test_generate_decision_with_chronic_condition() -> None:
    decision_repo = MagicMock(spec=AIDecisionRepository)
    profile_repo = MagicMock()
    health_repo = MagicMock()
    workout_repo = MagicMock()
    nutrition_repo = MagicMock()

    profile = UserProfile(
        id="prof_1",
        user_id="test_user_123",
        identity=IdentityProfile(full_name="John Doe", age=30, gender=Gender.MALE, country="US"),
        body=BodyProfile(height_cm=180.0, weight_kg=80.0),
        goals=GoalsProfile(primary_goal=TrainingGoal.FAT_LOSS),
        training=TrainingProfile(
            experience=ExperienceLevel.BEGINNER,
            available_days=3,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.BODYWEIGHT),
            workout_location=TrainingLocation.HOME_GYM,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=8.0,
            stress_level=2,
            activity_level=ActivityLevel.MODERATE,
            daily_water_ml=2000,
        ),
        nutrition=NutritionProfile(dietary_preferences=(), allergies=(), dietary_restrictions=()),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # Health profile containing controlled hypertension
    health = HealthProfile(
        id="h_1",
        user_id="test_user_123",
        injuries=(),
        chronic_conditions=(
            ChronicConditionRecord(name="Hypertension", controlled=True, medically_cleared=True),
        ),
        pain_areas=(),
        mobility_limitations=(),
        surgery_history=(),
        schema_version=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    profile_repo.get_by_user_id = AsyncMock(return_value=profile)
    health_repo.get_by_user_id = AsyncMock(return_value=health)
    workout_repo.get_active_plan = AsyncMock(return_value=None)
    workout_repo.list_sessions = AsyncMock(return_value=())
    nutrition_repo.get_progress = AsyncMock(
        side_effect=lambda user_id, day: NutritionProgress(
            date=day,
            calories_consumed=0,
            protein_consumed=0,
            carbohydrates_consumed=0,
            fat_consumed=0,
            water_consumed_ml=0,
            meals_completed=0,
        )
    )

    service = AIDecisionEngineService(
        decision_repo=decision_repo,
        profile_repo=profile_repo,
        health_repo=health_repo,
        workout_repo=workout_repo,
        nutrition_repo=nutrition_repo,
    )

    user = User(
        id="test_user_123",
        email="test@example.com",
        password_hash="***",
        is_active=True,
        token_version=0,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    decision_repo.find_active_by_date = AsyncMock(return_value=None)
    decision_repo.supersede_previous_decisions = AsyncMock()
    decision_repo.save = AsyncMock(side_effect=lambda d: d)

    decision = await service.get_or_generate_decision(user, date.today())

    # Should apply hypertension protocol (max intensity 0.7) and add warning/reason codes
    assert decision.training.intensity_multiplier == 0.7
    assert any("medical.hypertension" in w.code for w in decision.warnings)
    assert any("medical.hypertension" in r.code for r in decision.reason_codes)
