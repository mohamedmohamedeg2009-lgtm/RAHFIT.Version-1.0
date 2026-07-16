from datetime import UTC, date, datetime, timedelta
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from app.ai.context_limits import AIContextLimits
from app.ai.providers import OpenAICompatibleProvider
from app.models.ai_context import (
    AI_CONTEXT_VERSION,
    AIContextOmissionReason,
    AIContextPurpose,
    AIContextRequest,
    AIContextSectionName,
    AIRecommendationSource,
)
from app.models.ai_conversation import (
    AIConversation,
    AIConversationStatus,
    AIMessage,
    AIMessageRole,
    AIMessageSource,
)
from app.models.assessment import (
    AssessmentResult,
    AssessmentSummary,
    QuestionCategory,
    RiskLevel,
    SafetyStatus,
)
from app.models.nutrition import (
    ActivityLevel,
    Allergy,
    DietaryPreference,
    DietType,
    NutritionProgress,
)
from app.models.user import User
from app.models.workout import (
    Equipment,
    ExperienceLevel,
    TrainingGoal,
    TrainingLocation,
    WorkoutGenerationInput,
)
from app.services.ai_context import (
    AIContextBuilder,
    AIContextOwnershipError,
    AIContextRequiredSourceError,
    AIContextResourceNotFoundError,
    AIContextSizeError,
    AIContextValidationError,
)
from app.services.ai_conversation import AIConversationDetail, AIConversationNotFoundError
from app.services.nutrition import NutritionCurrentState, NutritionNotFoundError
from app.services.nutrition_engine import NutritionEngine
from app.services.workout import CurrentWorkoutState, WorkoutNotFoundError
from app.services.workout_generator import WorkoutGenerator

NOW = datetime(2026, 7, 16, 12, 0, tzinfo=UTC)


class FakeAssessmentSource:
    def __init__(self, result: AssessmentResult | None, failure: Exception | None = None) -> None:
        self.result = result
        self.failure = failure
        self.user_ids: list[str] = []

    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None:
        self.user_ids.append(user_id)
        if self.failure:
            raise self.failure
        return self.result


class FakeWorkoutSource:
    def __init__(self, state: CurrentWorkoutState | None, failure: Exception | None = None) -> None:
        self.state = state
        self.failure = failure
        self.user_ids: list[str] = []

    async def get_current(self, user_id: str) -> CurrentWorkoutState:
        self.user_ids.append(user_id)
        if self.failure:
            raise self.failure
        if not self.state:
            raise WorkoutNotFoundError
        return self.state


class FakeNutritionSource:
    def __init__(
        self, state: NutritionCurrentState | None, failure: Exception | None = None
    ) -> None:
        self.state = state
        self.failure = failure
        self.user_ids: list[str] = []

    async def current(self, user_id: str) -> NutritionCurrentState:
        self.user_ids.append(user_id)
        if self.failure:
            raise self.failure
        if not self.state:
            raise NutritionNotFoundError
        return self.state


class FakeConversationSource:
    def __init__(
        self, detail: AIConversationDetail | None, failure: Exception | None = None
    ) -> None:
        self.detail = detail
        self.failure = failure
        self.calls: list[tuple[str, str]] = []

    async def get_conversation(self, user_id: str, conversation_id: str) -> AIConversationDetail:
        self.calls.append((user_id, conversation_id))
        if self.failure:
            raise self.failure
        if not self.detail:
            raise AIConversationNotFoundError
        return self.detail


def user(user_id: str = "owner-user") -> User:
    return User(
        id=user_id,
        email="private-email@example.com",
        password_hash="forbidden-password-hash",
        display_name="Private Name",
        preferred_units="metric",
        token_version=17,
    )


def assessment(user_id: str = "owner-user") -> AssessmentResult:
    return AssessmentResult(
        id="internal-assessment-id",
        user_id=user_id,
        session_id="internal-assessment-session-id",
        assessment_version=3,
        profile={
            "personal_information": {
                "age": 22,
                "height": 178,
                "current_weight": 78,
            },
            "goals": {"primary_goal": "muscle_gain", "target_weight": 82},
            "experience": {"experience": "beginner"},
            "injuries": {"has_injury": True, "injury_area": ["knee"]},
            "equipment": {
                "home_training": True,
                "equipment_available": ["dumbbells", "bands"],
            },
            "private": {
                "access_token": "forbidden-access-token",
                "refresh_token": "forbidden-refresh-token",
                "api_key": "forbidden-api-key",
                "audit_data": "forbidden-audit-data",
            },
        },
        answered_question_ids=("age", "primary_goal", "experience", "injury_area"),
        completed_categories=(
            QuestionCategory.PERSONAL_INFORMATION,
            QuestionCategory.GOALS,
            QuestionCategory.EXPERIENCE,
            QuestionCategory.INJURIES,
        ),
        readiness_score=72,
        safety_status=SafetyStatus.CAUTION,
        risk_level=RiskLevel.MEDIUM,
        safety_explanations=("Use a conservative knee-aware plan.",),
        summary=AssessmentSummary(
            goals=("Primary goal: muscle gain.",),
            lifestyle=("Home training is preferred.",),
            medical_considerations=("A knee limitation was confirmed.",),
            training_readiness="Training is permitted with caution.",
            equipment=("Dumbbells", "Resistance bands"),
            experience="beginner",
        ),
        generated_at=NOW - timedelta(days=1),
    )


def workout_state(user_id: str = "owner-user") -> CurrentWorkoutState:
    inputs = WorkoutGenerationInput(
        assessment_result_id="internal-assessment-id",
        goal=TrainingGoal.MUSCLE_GAIN,
        experience=ExperienceLevel.BEGINNER,
        location=TrainingLocation.HOME_GYM,
        equipment=(Equipment.BODYWEIGHT, Equipment.DUMBBELL, Equipment.RESISTANCE_BAND),
        injuries=("knee",),
        available_days=3,
        session_duration_minutes=60,
    )
    plan = WorkoutGenerator().generate(user_id, inputs)
    return CurrentWorkoutState(plan=plan, today=plan.days[0], session=None)


def nutrition_state(user_id: str = "owner-user") -> NutritionCurrentState:
    engine = NutritionEngine()
    target = engine.targets(
        78,
        178,
        22,
        "male",
        ActivityLevel.MODERATE,
        TrainingGoal.MUSCLE_GAIN,
        3,
    )
    plan = engine.generate(
        user_id=user_id,
        assessment_result_id="internal-assessment-id",
        workout_plan_id=None,
        goal=TrainingGoal.MUSCLE_GAIN,
        diet=DietType.MEDITERRANEAN,
        allergies=(Allergy.MILK,),
        preferences=(DietaryPreference.HALAL,),
        activity=ActivityLevel.MODERATE,
        meal_count=4,
        target=target,
        today=date(2026, 7, 16),
    )
    progress = NutritionProgress(
        date=date(2026, 7, 16),
        calories_consumed=900,
        protein_consumed=55,
        carbohydrates_consumed=100,
        fat_consumed=30,
        water_consumed_ml=1200,
        completed_meal_ids=(plan.meal_plan.meals[0].id,),
        meals_completed=1,
    )
    return NutritionCurrentState(plan=plan, progress=progress)


def conversation_detail(
    user_id: str = "owner-user",
    status: AIConversationStatus = AIConversationStatus.ACTIVE,
    message_count: int = 5,
) -> AIConversationDetail:
    conversation_id = "a" * 32
    conversation = AIConversation(
        id=conversation_id,
        user_id=user_id,
        title="Owned conversation",
        status=status,
        message_count=message_count,
    )
    messages = tuple(
        AIMessage(
            id=f"{index:032x}",
            conversation_id=conversation_id,
            user_id=user_id,
            role=(AIMessageRole.USER if index % 2 else AIMessageRole.ASSISTANT),
            content=f"message-{index}-" + "x" * 20,
            source=(AIMessageSource.USER if index % 2 else AIMessageSource.APPLICATION),
            created_at=NOW + timedelta(seconds=index),
            deleted_at=(NOW if index == 2 else None),
        )
        for index in range(1, message_count + 1)
    )
    return AIConversationDetail(
        conversation=conversation,
        messages=messages,
        message_history_limit=100,
        messages_truncated=False,
    )


def builder(
    *,
    assessment_result: AssessmentResult | None = None,
    assessment_failure: Exception | None = None,
    workout: CurrentWorkoutState | None = None,
    workout_failure: Exception | None = None,
    nutrition: NutritionCurrentState | None = None,
    nutrition_failure: Exception | None = None,
    conversation: AIConversationDetail | None = None,
    conversation_failure: Exception | None = None,
    limits: AIContextLimits | None = None,
) -> tuple[
    AIContextBuilder,
    FakeAssessmentSource,
    FakeWorkoutSource,
    FakeNutritionSource,
    FakeConversationSource,
]:
    assessment_source = FakeAssessmentSource(
        assessment_result if assessment_result is not None else assessment(),
        assessment_failure,
    )
    workout_source = FakeWorkoutSource(
        workout if workout is not None else workout_state(), workout_failure
    )
    nutrition_source = FakeNutritionSource(
        nutrition if nutrition is not None else nutrition_state(), nutrition_failure
    )
    conversation_source = FakeConversationSource(
        conversation if conversation is not None else conversation_detail(),
        conversation_failure,
    )
    return (
        AIContextBuilder(
            assessment_source,
            workout_source,
            nutrition_source,
            conversation_source,
            limits=limits or AIContextLimits(),
            clock=lambda: NOW,
        ),
        assessment_source,
        workout_source,
        nutrition_source,
        conversation_source,
    )


def request_for(purpose: AIContextPurpose) -> AIContextRequest:
    values: dict[str, Any] = {
        "purpose": purpose,
        "current_user_question": " Please   explain this safely. ",
    }
    if purpose == AIContextPurpose.CLARIFY_RECOMMENDATION:
        values["recommendation_source"] = AIRecommendationSource.WORKOUT
    return AIContextRequest.model_validate(values)


def section_names(context: object) -> tuple[AIContextSectionName, ...]:
    assert hasattr(context, "sections")
    return tuple(section.name for section in context.sections)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("purpose", "expected"),
    (
        (
            AIContextPurpose.EXPLAIN_ASSESSMENT,
            {"safety", "request", "goals", "assessment", "profile"},
        ),
        (
            AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            {"safety", "request", "goals", "workout", "assessment", "profile", "progress"},
        ),
        (
            AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
            {"safety", "request", "goals", "nutrition", "assessment", "profile", "progress"},
        ),
        (
            AIContextPurpose.GENERAL_FITNESS_QUESTION,
            {"safety", "request", "goals", "profile"},
        ),
        (
            AIContextPurpose.GENERAL_NUTRITION_QUESTION,
            {"safety", "request", "goals", "nutrition", "profile"},
        ),
        (
            AIContextPurpose.SAFE_MOTIVATION,
            {"safety", "request", "goals", "progress", "preferences"},
        ),
        (
            AIContextPurpose.SUMMARIZE_CURRENT_PLAN,
            {"safety", "request", "goals", "workout", "nutrition", "progress"},
        ),
        (
            AIContextPurpose.CLARIFY_RECOMMENDATION,
            {"safety", "request", "goals", "workout"},
        ),
        (
            AIContextPurpose.SUGGEST_APPROVED_WORKOUT_ALTERNATIVE,
            {"safety", "request", "goals", "workout", "profile"},
        ),
        (
            AIContextPurpose.SUGGEST_APPROVED_NUTRITION_ALTERNATIVE,
            {"safety", "request", "goals", "nutrition", "profile"},
        ),
    ),
)
async def test_every_purpose_has_deterministic_minimum_sections(
    purpose: AIContextPurpose, expected: set[str]
) -> None:
    service, *_ = builder()

    context = await service.build_context(user(), request_for(purpose))

    assert {name.value for name in section_names(context)} == expected
    assert context.purpose == purpose
    assert context.context_version == AI_CONTEXT_VERSION


def test_unknown_purpose_mass_assignment_and_unsafe_options_are_rejected() -> None:
    with pytest.raises(ValidationError):
        AIContextRequest.model_validate(
            {
                "purpose": "unknown_purpose",
                "current_user_question": "Question",
            }
        )
    with pytest.raises(ValidationError):
        AIContextRequest.model_validate(
            {
                "purpose": "general_fitness_question",
                "current_user_question": "Question",
                "user_id": "attacker-selected-owner",
            }
        )
    with pytest.raises(ValidationError):
        AIContextRequest(
            purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
            current_user_question="Question",
            include_conversation_context=True,
        )


@pytest.mark.asyncio
async def test_authenticated_owner_is_used_for_every_loaded_source() -> None:
    service, assessment_source, workout_source, nutrition_source, conversation_source = builder()
    request = AIContextRequest(
        purpose=AIContextPurpose.SAFE_MOTIVATION,
        current_user_question="Keep me motivated",
        conversation_id="a" * 32,
        include_conversation_context=True,
    )

    context = await service.build_context(user("owner-user"), request)

    assert assessment_source.user_ids == ["owner-user"]
    assert workout_source.user_ids == ["owner-user"]
    assert nutrition_source.user_ids == ["owner-user"]
    assert conversation_source.calls == [("owner-user", "a" * 32)]
    assert context.owner_reference == "owner-user"


@pytest.mark.asyncio
@pytest.mark.parametrize("source", ("assessment", "workout", "nutrition", "conversation"))
async def test_cross_user_sources_fail_closed(source: str) -> None:
    overrides: dict[str, Any] = {}
    request = request_for(AIContextPurpose.EXPLAIN_ASSESSMENT)
    if source == "assessment":
        overrides["assessment_result"] = assessment("different-user")
    elif source == "workout":
        request = request_for(AIContextPurpose.EXPLAIN_WORKOUT_PLAN)
        overrides["workout"] = workout_state("different-user")
    elif source == "nutrition":
        request = request_for(AIContextPurpose.EXPLAIN_NUTRITION_PLAN)
        overrides["nutrition"] = nutrition_state("different-user")
    else:
        request = AIContextRequest(
            purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
            current_user_question="Question",
            conversation_id="a" * 32,
            include_conversation_context=True,
        )
        overrides["conversation"] = conversation_detail("different-user")
    service, *_ = builder(**overrides)

    with pytest.raises(AIContextOwnershipError):
        await service.build_context(user(), request)


@pytest.mark.asyncio
async def test_latest_assessment_safety_readiness_and_goals_are_transported_not_recalculated() -> (
    None
):
    result = assessment()
    service, assessment_source, *_ = builder(assessment_result=result)

    context = await service.build_context(user(), request_for(AIContextPurpose.EXPLAIN_ASSESSMENT))
    safety = next(item for item in context.sections if item.name == AIContextSectionName.SAFETY)
    assessment_section = next(
        item for item in context.sections if item.name == AIContextSectionName.ASSESSMENT
    )

    assert assessment_source.user_ids == ["owner-user"]
    assert safety.data["safety_status"] == "caution"
    assert safety.data["risk_level"] == "medium"
    assert safety.data["readiness_score"] == 72
    assert assessment_section.data["readiness_score"] == 72


@pytest.mark.asyncio
async def test_missing_assessment_produces_explicit_limited_safety_context() -> None:
    service, *_ = builder()
    service.assessment = FakeAssessmentSource(None)

    context = await service.build_context(
        user(), request_for(AIContextPurpose.GENERAL_FITNESS_QUESTION)
    )
    safety = context.sections[0]

    assert safety.name == AIContextSectionName.SAFETY
    assert safety.data["assessment_available"] is False
    assert safety.data["safety_status"] == "not_assessed"
    assert AIContextSectionName.GOALS in context.metadata.omitted_sections


@pytest.mark.asyncio
async def test_missing_optional_plans_are_omitted_without_build_failure() -> None:
    service, *_ = builder()
    service.workout = FakeWorkoutSource(None)
    service.nutrition = FakeNutritionSource(None)

    context = await service.build_context(
        user(), request_for(AIContextPurpose.SUMMARIZE_CURRENT_PLAN)
    )
    reasons = {item.section: item.reason_code for item in context.omissions}

    assert AIContextSectionName.SAFETY in section_names(context)
    assert reasons[AIContextSectionName.WORKOUT] == AIContextOmissionReason.SOURCE_MISSING
    assert reasons[AIContextSectionName.NUTRITION] == AIContextOmissionReason.SOURCE_MISSING


@pytest.mark.asyncio
async def test_purpose_minimization_does_not_load_unrelated_product_sources() -> None:
    service, _, workout_source, nutrition_source, _ = builder()

    await service.build_context(user(), request_for(AIContextPurpose.GENERAL_FITNESS_QUESTION))
    assert workout_source.user_ids == []
    assert nutrition_source.user_ids == []

    await service.build_context(user(), request_for(AIContextPurpose.EXPLAIN_WORKOUT_PLAN))
    assert workout_source.user_ids == ["owner-user"]
    assert nutrition_source.user_ids == []

    service, _, workout_source, nutrition_source, _ = builder()
    await service.build_context(user(), request_for(AIContextPurpose.EXPLAIN_NUTRITION_PLAN))
    assert workout_source.user_ids == []
    assert nutrition_source.user_ids == ["owner-user"]


@pytest.mark.asyncio
async def test_progress_and_preference_limits_are_explicit() -> None:
    service, *_ = builder(
        limits=AIContextLimits(maximum_progress_records=1, maximum_preference_fields=1)
    )

    context = await service.build_context(user(), request_for(AIContextPurpose.SAFE_MOTIVATION))
    progress = next(item for item in context.sections if item.name == AIContextSectionName.PROGRESS)
    preferences = next(
        item for item in context.sections if item.name == AIContextSectionName.PREFERENCES
    )

    assert len(progress.data["current_progress"]) == 1
    assert progress.truncated is True
    assert len(preferences.data) == 1
    assert preferences.truncated is True


@pytest.mark.asyncio
async def test_optional_source_failure_is_recorded_but_required_safety_failure_stops() -> None:
    service, *_ = builder(workout_failure=RuntimeError("database unavailable"))
    context = await service.build_context(
        user(), request_for(AIContextPurpose.EXPLAIN_WORKOUT_PLAN)
    )
    reasons = {item.section: item.reason_code for item in context.omissions}
    assert reasons[AIContextSectionName.WORKOUT] == AIContextOmissionReason.SOURCE_UNAVAILABLE

    failed, *_ = builder(assessment_failure=RuntimeError("database unavailable"))
    with pytest.raises(AIContextRequiredSourceError):
        await failed.build_context(user(), request_for(AIContextPurpose.EXPLAIN_ASSESSMENT))


@pytest.mark.asyncio
async def test_question_normalization_required_length_and_plain_text_rules() -> None:
    service, *_ = builder(limits=AIContextLimits(maximum_question_characters=20))
    context = await service.build_context(
        user(),
        AIContextRequest(
            purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
            current_user_question="  Is   this safe?  ",
        ),
    )
    request_section = next(
        item for item in context.sections if item.name == AIContextSectionName.REQUEST
    )
    assert request_section.data["current_user_question"] == "Is this safe?"

    with pytest.raises(AIContextValidationError):
        await service.build_context(
            user(),
            AIContextRequest(
                purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
                current_user_question="   ",
            ),
        )
    with pytest.raises(AIContextValidationError):
        await service.build_context(
            user(),
            AIContextRequest(
                purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
                current_user_question="x" * 21,
            ),
        )
    with pytest.raises(AIContextValidationError):
        await service.build_context(
            user(),
            AIContextRequest(
                purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
                current_user_question="<script>unsafe</script>",
            ),
        )


@pytest.mark.asyncio
async def test_forbidden_and_unnecessary_fields_never_appear_in_serialized_context() -> None:
    service, *_ = builder()
    context = await service.build_context(
        user(), request_for(AIContextPurpose.SUMMARIZE_CURRENT_PLAN)
    )
    serialized = context.model_dump_json()

    forbidden = (
        "password_hash",
        "forbidden-password-hash",
        "private-email@example.com",
        "access_token",
        "forbidden-access-token",
        "refresh_token",
        "forbidden-refresh-token",
        "api_key",
        "forbidden-api-key",
        "audit_data",
        "forbidden-audit-data",
        "internal-assessment-id",
        "internal-assessment-session-id",
        "generation_key",
        "system_instructions",
        "prompt",
    )
    assert all(value not in serialized for value in forbidden)


@pytest.mark.asyncio
async def test_conversation_is_explicit_owner_scoped_bounded_and_chronological() -> None:
    limits = AIContextLimits(
        maximum_conversation_messages=3,
        maximum_conversation_characters=75,
        maximum_text_field_characters=75,
    )
    service, *_ = builder(limits=limits)
    request = AIContextRequest(
        purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
        current_user_question="Continue our discussion",
        conversation_id="a" * 32,
        include_conversation_context=True,
    )

    context = await service.build_context(user(), request)
    section = next(
        item for item in context.sections if item.name == AIContextSectionName.CONVERSATION
    )
    messages = section.data["messages"]

    assert isinstance(messages, list)
    assert [item["content"].split("-")[1] for item in messages] == ["4", "5"]
    assert all("message-2" not in item["content"] for item in messages)
    assert len(messages) <= 3
    assert sum(len(item["content"]) for item in messages) <= 75
    assert section.truncated is True
    assert context.size.conversation_messages == len(messages)


@pytest.mark.asyncio
async def test_deleted_or_cross_user_conversation_has_same_safe_failure() -> None:
    deleted, *_ = builder(conversation=conversation_detail(status=AIConversationStatus.DELETED))
    missing, *_ = builder(conversation_failure=AIConversationNotFoundError())
    request = AIContextRequest(
        purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
        current_user_question="Question",
        conversation_id="a" * 32,
        include_conversation_context=True,
    )

    with pytest.raises(AIContextResourceNotFoundError):
        await deleted.build_context(user(), request)
    with pytest.raises(AIContextResourceNotFoundError):
        await missing.build_context(user(), request)


@pytest.mark.asyncio
async def test_conversation_is_not_loaded_for_unapproved_purpose() -> None:
    service, *_, conversation_source = builder()
    request = AIContextRequest(
        purpose=AIContextPurpose.EXPLAIN_ASSESSMENT,
        current_user_question="Explain",
        conversation_id="a" * 32,
        include_conversation_context=True,
    )

    context = await service.build_context(user(), request)
    reasons = {item.section: item.reason_code for item in context.omissions}

    assert conversation_source.calls == []
    assert reasons[AIContextSectionName.CONVERSATION] == (
        AIContextOmissionReason.PURPOSE_NOT_APPROVED
    )


@pytest.mark.asyncio
async def test_size_pressure_removes_lower_priority_sections_but_never_safety() -> None:
    baseline, *_ = builder()
    full = await baseline.build_context(
        user(), request_for(AIContextPurpose.SUMMARIZE_CURRENT_PLAN)
    )
    constrained_limit = max(2500, full.size.serialized_size_bytes - 1000)
    constrained, *_ = builder(limits=AIContextLimits(maximum_serialized_bytes=constrained_limit))

    context = await constrained.build_context(
        user(), request_for(AIContextPurpose.SUMMARIZE_CURRENT_PLAN)
    )

    assert context.sections[0].name == AIContextSectionName.SAFETY
    assert context.size.serialized_size_bytes <= constrained_limit
    size_omissions = [
        item for item in context.omissions if item.reason_code == AIContextOmissionReason.SIZE_LIMIT
    ]
    assert size_omissions
    assert all(item.section != AIContextSectionName.SAFETY for item in size_omissions)


@pytest.mark.asyncio
async def test_mandatory_context_overflow_fails_safely() -> None:
    service, *_ = builder(limits=AIContextLimits(maximum_serialized_bytes=200))

    with pytest.raises(AIContextSizeError):
        await service.build_context(user(), request_for(AIContextPurpose.GENERAL_FITNESS_QUESTION))


@pytest.mark.asyncio
async def test_size_and_explainability_metadata_are_complete_and_exact() -> None:
    service, *_ = builder(limits=AIContextLimits(maximum_workout_items=1))

    context = await service.build_context(
        user(), request_for(AIContextPurpose.EXPLAIN_WORKOUT_PLAN)
    )

    assert context.metadata.context_version == AI_CONTEXT_VERSION
    assert context.metadata.purpose == AIContextPurpose.EXPLAIN_WORKOUT_PLAN
    assert context.metadata.included_sections == section_names(context)
    assert set(context.metadata.omitted_sections) == {item.section for item in context.omissions}
    assert AIContextSectionName.WORKOUT in context.metadata.truncated_sections
    assert len(context.model_dump_json().encode("utf-8")) == context.size.serialized_size_bytes
    assert context.size.serialized_size_bytes <= context.size.maximum_serialized_bytes
    assert all(item.reason for item in context.inclusions)
    assert all(item.reason for item in context.omissions)


@pytest.mark.asyncio
async def test_repeated_build_is_deterministic_and_does_not_persist_context() -> None:
    service, _, _, _, conversation_source = builder()
    request = AIContextRequest(
        purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
        current_user_question="Question",
        conversation_id="a" * 32,
        include_conversation_context=True,
    )

    first = await service.build_context(user(), request)
    second = await service.build_context(user(), request)

    assert first == second
    assert conversation_source.calls == [
        ("owner-user", "a" * 32),
        ("owner-user", "a" * 32),
    ]
    assert not hasattr(service, "save_context")


@pytest.mark.asyncio
async def test_builder_makes_no_provider_call_and_logs_no_question_or_context(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    async def forbidden_generate(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Context building must not call an AI provider.")

    async def forbidden_network(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Context building must not make a network request.")

    monkeypatch.setattr(OpenAICompatibleProvider, "generate", forbidden_generate)
    monkeypatch.setattr(httpx.AsyncClient, "request", forbidden_network)
    service, *_ = builder()
    private_question = "private-current-question-not-for-logs"

    context = await service.build_context(
        user(),
        AIContextRequest(
            purpose=AIContextPurpose.GENERAL_FITNESS_QUESTION,
            current_user_question=private_question,
        ),
    )

    assert private_question not in caplog.text
    assert context.model_dump_json() not in caplog.text
