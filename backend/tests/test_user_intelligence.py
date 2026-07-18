from datetime import UTC, date, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.context import UserIntelligenceContextBuilder, UserIntelligenceNotReadyError
from app.health import (
    ChronicConditionRecord,
    HealthProfile,
    HealthProfileData,
    HealthSeverity,
    InjuryRecord,
    PainAreaRecord,
    SurgeryRecord,
)
from app.health.repository import HealthProfileRepository
from app.models.ai_classifier import (
    AICapabilityClassificationResult,
    AIClassificationReasonCode,
)
from app.models.ai_context import AIContextPurpose, AIContextRequest, AIContextSectionName
from app.models.ai_policy import AIAction, AICapability
from app.models.ai_safety import AISafetyRequest
from app.models.nutrition import ActivityLevel, Allergy, DietaryPreference
from app.models.user import User
from app.models.workout import Equipment, ExperienceLevel, TrainingGoal, TrainingLocation
from app.profile import (
    AgeGroup,
    BodyProfile,
    Gender,
    GoalsProfile,
    IdentityProfile,
    LifestyleProfile,
    NutritionProfile,
    TrainingProfile,
    UserProfile,
    UserProfileData,
)
from app.profile.repository import UserProfileRepository
from app.readiness import ReadinessChecker, ReadinessStatus
from app.services.ai_classifier import CapabilityClassifier
from app.services.ai_policy import AIPolicyService
from app.services.ai_safety import AISafetyEngine
from app.users import UserIntelligenceService, UserIntelligenceSnapshot

NOW = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)


def profile_data(
    *,
    primary_goal: TrainingGoal = TrainingGoal.FAT_LOSS,
    weight_kg: float = 80.0,
    target_weight_kg: float = 75.0,
    target_date: date = date(2027, 7, 16),
    sleep_hours: float = 8.0,
    stress_level: int = 4,
    activity_level: ActivityLevel = ActivityLevel.MODERATE,
    age: int = 30,
    experience: ExperienceLevel = ExperienceLevel.INTERMEDIATE,
) -> UserProfileData:
    return UserProfileData(
        identity=IdentityProfile(
            full_name="  Rahfit   User  ",
            age=age,
            gender=Gender.MALE,
            country="eg",
        ),
        body=BodyProfile(
            height_cm=180.0,
            weight_kg=weight_kg,
            body_fat_percentage=20.0,
        ),
        goals=GoalsProfile(
            primary_goal=primary_goal,
            secondary_goal=TrainingGoal.GENERAL_FITNESS,
            target_weight_kg=target_weight_kg,
            target_date=target_date,
        ),
        training=TrainingProfile(
            experience=experience,
            available_days=4,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.BODYWEIGHT),
            workout_location=TrainingLocation.HOME_GYM,
        ),
        lifestyle=LifestyleProfile(
            sleep_hours=sleep_hours,
            stress_level=stress_level,
            activity_level=activity_level,
            daily_water_ml=2_500,
        ),
        nutrition=NutritionProfile(
            dietary_preferences=(DietaryPreference.HALAL,),
            allergies=(Allergy.MILK,),
            dietary_restrictions=("No Pork",),
        ),
    )


def user_profile(**overrides: object) -> UserProfile:
    data = profile_data(**overrides)  # type: ignore[arg-type]
    return UserProfile(
        id="profile-1",
        user_id="owner-user",
        **data.model_dump(exclude={"bmi", "bmr_kcal", "age_group"}),
    )


def health_data(
    *,
    injuries: tuple[InjuryRecord, ...] = (),
    conditions: tuple[ChronicConditionRecord, ...] = (),
    pain_areas: tuple[PainAreaRecord, ...] = (),
    surgeries: tuple[SurgeryRecord, ...] = (),
    notes: str | None = "Private health note that must never reach Gemini.",
) -> HealthProfileData:
    return HealthProfileData(
        injuries=injuries,
        chronic_conditions=conditions,
        pain_areas=pain_areas,
        mobility_limitations=(),
        surgery_history=surgeries,
        notes=notes,
    )


def health_profile(**overrides: object) -> HealthProfile:
    data = health_data(**overrides)  # type: ignore[arg-type]
    return HealthProfile(
        id="health-1",
        user_id="owner-user",
        **data.model_dump(exclude={"active_injury_areas", "requires_medical_clearance"}),
    )


def snapshot(
    profile: UserProfile | None = None,
    health: HealthProfile | None = None,
) -> UserIntelligenceSnapshot:
    return UserIntelligenceSnapshot(
        user_id="owner-user",
        profile=profile,
        health_profile=health,
    )


def checker() -> ReadinessChecker:
    return ReadinessChecker(clock=lambda: NOW)


def auth_user(user_id: str = "owner-user") -> User:
    return User(
        id=user_id,
        email="owner@example.com",
        password_hash="password-hash-never-used-by-context",
    )


class SnapshotSource:
    def __init__(self, value: UserIntelligenceSnapshot) -> None:
        self.value = value
        self.requested_user_ids: list[str] = []

    async def get_snapshot(self, user_id: str) -> UserIntelligenceSnapshot:
        self.requested_user_ids.append(user_id)
        return self.value


class FakeUpsertCollection:
    def __init__(self, identifier: str) -> None:
        self.identifier = identifier
        self.document: dict[str, object] | None = None

    async def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        if self.document is None or self.document.get("user_id") != query.get("user_id"):
            return None
        return dict(self.document)

    async def find_one_and_update(
        self,
        query: dict[str, object],
        update: dict[str, dict[str, object]],
        **options: object,
    ) -> dict[str, object]:
        assert options["upsert"] is True
        if self.document is None:
            self.document = {"_id": self.identifier, **update["$setOnInsert"]}
        self.document.update(update["$set"])
        self.document["user_id"] = query["user_id"]
        return dict(self.document)


class FakeIntelligenceDatabase:
    def __init__(self) -> None:
        self.collections = {
            "user_profiles": FakeUpsertCollection("profile-1"),
            "health_profiles": FakeUpsertCollection("health-1"),
        }

    def __getitem__(self, name: str) -> FakeUpsertCollection:
        return self.collections[name]


def test_profile_computed_fields_and_normalization_are_deterministic() -> None:
    profile = profile_data()

    assert profile.identity.full_name == "Rahfit User"
    assert profile.identity.country == "EG"
    assert profile.bmi == 24.69
    assert profile.bmr_kcal == 1_780
    assert profile.age_group == AgeGroup.YOUNG_ADULT


def test_profile_rejects_coercion_impossible_values_and_conflicts() -> None:
    with pytest.raises(ValidationError):
        BodyProfile(height_cm="180", weight_kg=80.0)
    with pytest.raises(ValidationError):
        BodyProfile(height_cm=90.0, weight_kg=80.0)
    with pytest.raises(ValidationError):
        GoalsProfile(
            primary_goal=TrainingGoal.FAT_LOSS,
            secondary_goal=TrainingGoal.FAT_LOSS,
        )
    with pytest.raises(ValidationError):
        GoalsProfile(
            primary_goal=TrainingGoal.FAT_LOSS,
            target_weight_kg=75.0,
        )
    with pytest.raises(ValidationError):
        TrainingProfile(
            experience=ExperienceLevel.BEGINNER,
            available_days=3,
            session_duration_minutes=60,
            available_equipment=(Equipment.DUMBBELL, Equipment.DUMBBELL),
            workout_location=TrainingLocation.HOME_GYM,
        )


def test_health_profile_requires_explicit_declarations_and_strict_values() -> None:
    with pytest.raises(ValidationError):
        HealthProfileData.model_validate({})
    with pytest.raises(ValidationError):
        PainAreaRecord(area="knee", intensity="8", movement_related=True)
    with pytest.raises(ValidationError):
        SurgeryRecord(
            procedure="Future procedure",
            surgery_date=date.today() + timedelta(days=1),
            medically_cleared=False,
        )


def test_health_computed_restrictions_are_deterministic() -> None:
    health = health_data(
        injuries=(
            InjuryRecord(
                area="knee",
                description="Limited flexion",
                severity=HealthSeverity.MODERATE,
                active=True,
                medically_cleared=False,
            ),
        )
    )

    assert health.active_injury_areas == ("knee",)
    assert health.requires_medical_clearance is True


@pytest.mark.asyncio
async def test_profile_and_health_repositories_upsert_owner_scoped_documents() -> None:
    database = FakeIntelligenceDatabase()
    profile_repository = UserProfileRepository(database)  # type: ignore[arg-type]
    health_repository = HealthProfileRepository(database)  # type: ignore[arg-type]
    surgery = SurgeryRecord(
        procedure="Knee repair",
        surgery_date=date(2025, 1, 10),
        medically_cleared=True,
    )

    saved_profile = await profile_repository.save("owner-user", profile_data())
    saved_health = await health_repository.save(
        "owner-user",
        health_data(surgeries=(surgery,)),
    )

    profile_document = database.collections["user_profiles"].document
    health_document = database.collections["health_profiles"].document
    assert saved_profile.user_id == saved_health.user_id == "owner-user"
    assert profile_document is not None
    assert health_document is not None
    assert profile_document["goals"]["target_date"] == "2027-07-16"  # type: ignore[index]
    assert health_document["surgery_history"][0]["surgery_date"] == "2025-01-10"  # type: ignore[index]
    assert "bmi" not in profile_document
    assert "requires_medical_clearance" not in health_document

    assert await profile_repository.get_by_user_id("other-user") is None
    assert await health_repository.get_by_user_id("other-user") is None


def test_readiness_reports_every_missing_required_group() -> None:
    result = checker().check(snapshot())

    assert result.status == ReadinessStatus.NEEDS_INFORMATION
    assert result.ready_for_ai is False
    assert result.completeness_score == 0
    assert "profile.identity.full_name" in result.missing_fields
    assert "health_profile.injuries" in result.missing_fields


def test_complete_safe_intelligence_is_ready_for_ai() -> None:
    result = checker().check(snapshot(user_profile(), health_profile()))

    assert result.status == ReadinessStatus.READY
    assert result.ready_for_ai is True
    assert result.completeness_score == 100
    assert result.missing_fields == ()
    assert result.issues == ()


def test_readiness_blocks_incompatible_goal_direction() -> None:
    profile = user_profile(target_weight_kg=85.0)

    result = checker().check(snapshot(profile, health_profile()))

    assert result.status == ReadinessStatus.BLOCKED
    assert "goal.fat_loss_target_direction" in {item.code for item in result.issues}


def test_readiness_blocks_dangerous_health_and_recovery_combinations() -> None:
    severe_injury = InjuryRecord(
        area="knee",
        description="Acute severe injury",
        severity=HealthSeverity.SEVERE,
        active=True,
        medically_cleared=False,
    )
    dangerous_health = health_profile(injuries=(severe_injury,))
    dangerous_lifestyle = user_profile(
        sleep_hours=3.0,
        stress_level=9,
        activity_level=ActivityLevel.EXTRA_ACTIVE,
    )

    result = checker().check(snapshot(dangerous_lifestyle, dangerous_health))

    codes = {item.code for item in result.issues}
    assert result.status == ReadinessStatus.BLOCKED
    assert "health.severe_active_injury" in codes
    assert "lifestyle.recovery_risk" in codes
    assert all(
        item.requires_professional_guidance
        for item in result.issues
        if item.code in {"health.severe_active_injury", "lifestyle.recovery_risk"}
    )


def test_readiness_keeps_old_uncleared_surgery_in_caution_state() -> None:
    surgery = SurgeryRecord(
        procedure="Shoulder repair",
        surgery_date=date(2025, 1, 1),
        medically_cleared=False,
    )

    result = checker().check(snapshot(user_profile(), health_profile(surgeries=(surgery,))))

    assert result.status == ReadinessStatus.CAUTION
    assert result.ready_for_ai is True
    assert {item.code for item in result.issues} == {"health.surgery_not_cleared"}


@pytest.mark.asyncio
async def test_user_intelligence_service_enforces_owner_scoped_reads() -> None:
    class Reader:
        def __init__(self, value: object) -> None:
            self.value = value

        async def get_by_user_id(self, user_id: str) -> object:
            assert user_id == "owner-user"
            return self.value

    service = UserIntelligenceService(
        Reader(user_profile()),  # type: ignore[arg-type]
        Reader(health_profile()),  # type: ignore[arg-type]
    )

    result = await service.get_snapshot(" owner-user ")

    assert result.user_id == "owner-user"
    assert result.profile is not None
    assert result.health_profile is not None


@pytest.mark.asyncio
async def test_context_builder_minimizes_workout_context_and_excludes_identity() -> None:
    source = SnapshotSource(snapshot(user_profile(), health_profile()))
    builder = UserIntelligenceContextBuilder(source, checker(), clock=lambda: NOW)

    context = await builder.build_context(
        auth_user(),
        AIContextRequest(
            purpose=AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            current_user_question=" Explain   my workout ",
        ),
    )

    names = tuple(section.name for section in context.sections)
    serialized = context.model_dump_json()
    assert names == (
        AIContextSectionName.SAFETY,
        AIContextSectionName.REQUEST,
        AIContextSectionName.GOALS,
        AIContextSectionName.PROFILE,
        AIContextSectionName.WORKOUT,
    )
    assert AIContextSectionName.NUTRITION not in names
    assert "Rahfit User" not in serialized
    assert "owner@example.com" not in serialized
    assert "Private health note" not in serialized
    assert "password-hash-never-used-by-context" not in serialized
    assert source.requested_user_ids == ["owner-user"]


@pytest.mark.asyncio
async def test_context_builder_selects_nutrition_data_only_for_nutrition_purpose() -> None:
    builder = UserIntelligenceContextBuilder(
        SnapshotSource(snapshot(user_profile(), health_profile())),
        checker(),
        clock=lambda: NOW,
    )

    context = await builder.build_context(
        auth_user(),
        AIContextRequest(
            purpose=AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
            current_user_question="explain my nutrition",
        ),
    )

    names = {section.name for section in context.sections}
    assert AIContextSectionName.NUTRITION in names
    assert AIContextSectionName.WORKOUT not in names
    assert context.size.serialized_size_bytes <= context.size.maximum_serialized_bytes


@pytest.mark.asyncio
async def test_context_builder_output_is_accepted_by_existing_safety_engine() -> None:
    builder = UserIntelligenceContextBuilder(
        SnapshotSource(snapshot(user_profile(), health_profile())),
        checker(),
        clock=lambda: NOW,
    )
    context = await builder.build_context(
        auth_user(),
        AIContextRequest(
            purpose=AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            current_user_question="explain my workout",
        ),
    )
    capability = AICapability.EXPLAIN_WORKOUT
    classification = AICapabilityClassificationResult(
        capability=capability,
        confidence=0.95,
        matched_rules=("workout_explanation",),
        reason_code=AIClassificationReasonCode.WORKOUT_INTENT_MATCHED,
        requires_safety_review=True,
    )
    policy = AIPolicyService().evaluate(capability, AIAction.EXPLAIN)

    result = AISafetyEngine(clock=lambda: NOW).evaluate_safety(
        auth_user(),
        AISafetyRequest(
            authenticated_owner_reference="owner-user",
            normalized_user_message=CapabilityClassifier.normalize("explain my workout"),
            classification=classification,
            policy=policy,
            approved_context=context,
        ),
    )

    assert result.requires_provider is True


@pytest.mark.asyncio
async def test_context_builder_stops_before_context_when_readiness_fails() -> None:
    builder = UserIntelligenceContextBuilder(
        SnapshotSource(snapshot()),
        checker(),
        clock=lambda: NOW,
    )

    with pytest.raises(UserIntelligenceNotReadyError) as captured:
        await builder.build_context(
            auth_user(),
            AIContextRequest(
                purpose=AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
                current_user_question="explain my workout",
            ),
        )

    assert captured.value.readiness.status == ReadinessStatus.NEEDS_INFORMATION
