import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

from app.ai.context_limits import AI_CONTEXT_LIMITS, AIContextLimits
from app.models.ai_context import (
    AI_CONTEXT_VERSION,
    AIApprovedContext,
    AIContextBuildMetadata,
    AIContextInclusionRecord,
    AIContextOmissionReason,
    AIContextOmissionRecord,
    AIContextPurpose,
    AIContextRequest,
    AIContextSection,
    AIContextSectionName,
    AIContextSizeMetadata,
    AIContextSourceType,
    AIRecommendationSource,
)
from app.models.ai_conversation import AIConversationStatus
from app.models.assessment import AssessmentResult
from app.models.user import User
from app.services.ai_conversation import AIConversationDetail, AIConversationNotFoundError
from app.services.nutrition import NutritionCurrentState, NutritionNotFoundError
from app.services.workout import CurrentWorkoutState, WorkoutNotFoundError

_HTML_TAG_PATTERN = re.compile(r"</?[A-Za-z][^>]*>")

_SECTION_PRIORITY: dict[AIContextSectionName, int] = {
    AIContextSectionName.SAFETY: 1,
    AIContextSectionName.REQUEST: 2,
    AIContextSectionName.GOALS: 3,
    AIContextSectionName.WORKOUT: 4,
    AIContextSectionName.NUTRITION: 4,
    AIContextSectionName.ASSESSMENT: 5,
    AIContextSectionName.PROFILE: 5,
    AIContextSectionName.PROGRESS: 6,
    AIContextSectionName.PREFERENCES: 7,
    AIContextSectionName.CONVERSATION: 8,
}
_SECTION_ORDER = tuple(_SECTION_PRIORITY)

_QUESTION_REQUIRED = frozenset(
    {
        AIContextPurpose.EXPLAIN_ASSESSMENT,
        AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
        AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
        AIContextPurpose.GENERAL_FITNESS_QUESTION,
        AIContextPurpose.GENERAL_NUTRITION_QUESTION,
        AIContextPurpose.CLARIFY_RECOMMENDATION,
        AIContextPurpose.SUGGEST_APPROVED_WORKOUT_ALTERNATIVE,
        AIContextPurpose.SUGGEST_APPROVED_NUTRITION_ALTERNATIVE,
    }
)

_PURPOSE_SECTIONS: dict[AIContextPurpose, frozenset[AIContextSectionName]] = {
    AIContextPurpose.EXPLAIN_ASSESSMENT: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.ASSESSMENT,
            AIContextSectionName.PROFILE,
        }
    ),
    AIContextPurpose.EXPLAIN_WORKOUT_PLAN: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.WORKOUT,
            AIContextSectionName.ASSESSMENT,
            AIContextSectionName.PROFILE,
            AIContextSectionName.PROGRESS,
        }
    ),
    AIContextPurpose.EXPLAIN_NUTRITION_PLAN: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.ASSESSMENT,
            AIContextSectionName.PROFILE,
            AIContextSectionName.PROGRESS,
        }
    ),
    AIContextPurpose.GENERAL_FITNESS_QUESTION: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.PROFILE,
        }
    ),
    AIContextPurpose.GENERAL_NUTRITION_QUESTION: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.PROFILE,
        }
    ),
    AIContextPurpose.SAFE_MOTIVATION: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.PROGRESS,
            AIContextSectionName.PREFERENCES,
        }
    ),
    AIContextPurpose.SUMMARIZE_CURRENT_PLAN: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.WORKOUT,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.PROGRESS,
        }
    ),
    AIContextPurpose.SUGGEST_APPROVED_WORKOUT_ALTERNATIVE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.WORKOUT,
            AIContextSectionName.PROFILE,
        }
    ),
    AIContextPurpose.SUGGEST_APPROVED_NUTRITION_ALTERNATIVE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.PROFILE,
        }
    ),
    AIContextPurpose.CLARIFY_RECOMMENDATION: frozenset(),
}

_CONVERSATION_PURPOSES = frozenset(
    {
        AIContextPurpose.GENERAL_FITNESS_QUESTION,
        AIContextPurpose.GENERAL_NUTRITION_QUESTION,
        AIContextPurpose.SAFE_MOTIVATION,
        AIContextPurpose.CLARIFY_RECOMMENDATION,
    }
)


class AIContextValidationError(Exception):
    """Raised when the internal context request violates a stable rule."""


class AIContextOwnershipError(Exception):
    """Raised when an injected source violates owner isolation."""


class AIContextResourceNotFoundError(Exception):
    """Safe missing-or-unauthorized error for explicitly requested context."""


class AIContextRequiredSourceError(Exception):
    """Raised when required safety context cannot be loaded reliably."""


class AIContextSizeError(Exception):
    """Raised when mandatory safety and request context exceed the hard limit."""


class AssessmentContextSource(Protocol):
    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None: ...


class WorkoutContextSource(Protocol):
    async def get_current(self, user_id: str) -> CurrentWorkoutState: ...


class NutritionContextSource(Protocol):
    async def current(self, user_id: str) -> NutritionCurrentState: ...


class ConversationContextSource(Protocol):
    async def get_conversation(
        self, user_id: str, conversation_id: str
    ) -> AIConversationDetail: ...


@dataclass(frozen=True)
class _SourceSnapshot:
    assessment: AssessmentResult | None
    workout: CurrentWorkoutState | None
    nutrition: NutritionCurrentState | None
    conversation: AIConversationDetail | None
    failures: Mapping[AIContextSectionName, AIContextOmissionReason]


class AIContextBuilder:
    """Build minimum-necessary, owner-scoped context without prompts or providers."""

    def __init__(
        self,
        assessment: AssessmentContextSource,
        workout: WorkoutContextSource | None = None,
        nutrition: NutritionContextSource | None = None,
        conversation: ConversationContextSource | None = None,
        limits: AIContextLimits = AI_CONTEXT_LIMITS,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.assessment = assessment
        self.workout = workout
        self.nutrition = nutrition
        self.conversation = conversation
        self.limits = limits
        self.clock = clock or (lambda: datetime.now(UTC))

    async def build_context(
        self, authenticated_user: User, request: AIContextRequest
    ) -> AIApprovedContext:
        question = self._normalize_question(request)
        selected = self._selected_sections(request)
        snapshot = await self._load_sources(authenticated_user, request, selected)
        omissions = self._purpose_omissions(selected, request)
        sections: list[AIContextSection] = []

        safety = self._safety_section(snapshot)
        sections.append(safety)
        if question is not None:
            sections.append(
                self._section(
                    AIContextSectionName.REQUEST,
                    (AIContextSourceType.CURRENT_REQUEST,),
                    {"current_user_question": question, "untrusted_plain_text": True},
                    "The current user question is isolated from trusted application facts.",
                )
            )
        elif AIContextSectionName.REQUEST in selected:
            omissions[AIContextSectionName.REQUEST] = self._omission(
                AIContextSectionName.REQUEST,
                AIContextOmissionReason.NO_APPROVED_DATA,
                "No current question was supplied for this optional request section.",
            )

        builders: dict[AIContextSectionName, Callable[[], AIContextSection | None]] = {
            AIContextSectionName.GOALS: lambda: self._goals_section(snapshot.assessment),
            AIContextSectionName.WORKOUT: lambda: self._workout_section(snapshot.workout),
            AIContextSectionName.NUTRITION: lambda: self._nutrition_section(snapshot.nutrition),
            AIContextSectionName.ASSESSMENT: lambda: self._assessment_section(snapshot.assessment),
            AIContextSectionName.PROFILE: lambda: self._profile_section(
                authenticated_user, request.purpose, snapshot
            ),
            AIContextSectionName.PROGRESS: lambda: self._progress_section(snapshot),
            AIContextSectionName.PREFERENCES: lambda: self._preferences_section(
                authenticated_user, snapshot.nutrition
            ),
            AIContextSectionName.CONVERSATION: lambda: self._conversation_section(
                snapshot.conversation
            ),
        }
        for name in _SECTION_ORDER:
            if name in {AIContextSectionName.SAFETY, AIContextSectionName.REQUEST}:
                continue
            if name not in selected:
                continue
            failure = snapshot.failures.get(name)
            if failure:
                omissions[name] = self._omission(
                    name,
                    failure,
                    "The optional approved source is not currently available.",
                )
                continue
            section = builders[name]()
            if section:
                sections.append(section)
            else:
                omissions[name] = self._omission(
                    name,
                    AIContextOmissionReason.SOURCE_MISSING,
                    "No approved current data exists for this section.",
                )

        sections.sort(
            key=lambda item: (_SECTION_PRIORITY[item.name], _SECTION_ORDER.index(item.name))
        )
        return self._fit_context(
            authenticated_user.id,
            request.purpose,
            sections,
            omissions,
            len(question) if question else 0,
        )

    def _selected_sections(self, request: AIContextRequest) -> set[AIContextSectionName]:
        if request.purpose == AIContextPurpose.CLARIFY_RECOMMENDATION:
            if request.recommendation_source is None:
                raise AIContextValidationError("recommendation_source_required")
            selected = {
                AIContextSectionName.SAFETY,
                AIContextSectionName.REQUEST,
                AIContextSectionName.GOALS,
            }
            selected.add(
                {
                    AIRecommendationSource.ASSESSMENT: AIContextSectionName.ASSESSMENT,
                    AIRecommendationSource.WORKOUT: AIContextSectionName.WORKOUT,
                    AIRecommendationSource.NUTRITION: AIContextSectionName.NUTRITION,
                }[request.recommendation_source]
            )
        else:
            selected = set(_PURPOSE_SECTIONS[request.purpose])
        if request.include_conversation_context and request.purpose in _CONVERSATION_PURPOSES:
            selected.add(AIContextSectionName.CONVERSATION)
        return selected

    async def _load_sources(
        self,
        user: User,
        request: AIContextRequest,
        selected: set[AIContextSectionName],
    ) -> _SourceSnapshot:
        try:
            assessment = await self.assessment.get_latest_assessment_optional(user.id)
        except Exception as exc:
            raise AIContextRequiredSourceError("assessment_source_unavailable") from exc
        if assessment and assessment.user_id != user.id:
            raise AIContextOwnershipError

        failures: dict[AIContextSectionName, AIContextOmissionReason] = {}
        workout: CurrentWorkoutState | None = None
        needs_workout_progress = request.purpose in {
            AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            AIContextPurpose.SAFE_MOTIVATION,
            AIContextPurpose.SUMMARIZE_CURRENT_PLAN,
        }
        needs_workout = AIContextSectionName.WORKOUT in selected or (
            AIContextSectionName.PROGRESS in selected and needs_workout_progress
        )
        if needs_workout:
            if not self.workout:
                failures[AIContextSectionName.WORKOUT] = AIContextOmissionReason.SOURCE_UNAVAILABLE
            else:
                try:
                    workout = await self.workout.get_current(user.id)
                except WorkoutNotFoundError:
                    pass
                except Exception:
                    failures[AIContextSectionName.WORKOUT] = (
                        AIContextOmissionReason.SOURCE_UNAVAILABLE
                    )
                if workout and (
                    workout.plan.user_id != user.id
                    or (workout.session and workout.session.user_id != user.id)
                ):
                    raise AIContextOwnershipError

        nutrition: NutritionCurrentState | None = None
        needs_nutrition_progress = request.purpose in {
            AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
            AIContextPurpose.SAFE_MOTIVATION,
            AIContextPurpose.SUMMARIZE_CURRENT_PLAN,
        }
        needs_nutrition = AIContextSectionName.NUTRITION in selected or (
            AIContextSectionName.PROGRESS in selected and needs_nutrition_progress
        )
        if needs_nutrition:
            if not self.nutrition:
                failures[AIContextSectionName.NUTRITION] = (
                    AIContextOmissionReason.SOURCE_UNAVAILABLE
                )
            else:
                try:
                    nutrition = await self.nutrition.current(user.id)
                except NutritionNotFoundError:
                    pass
                except Exception:
                    failures[AIContextSectionName.NUTRITION] = (
                        AIContextOmissionReason.SOURCE_UNAVAILABLE
                    )
                if nutrition and nutrition.plan.user_id != user.id:
                    raise AIContextOwnershipError

        conversation: AIConversationDetail | None = None
        conversation_approved = (
            request.include_conversation_context and request.purpose in _CONVERSATION_PURPOSES
        )
        if conversation_approved:
            if not self.conversation or not request.conversation_id:
                raise AIContextResourceNotFoundError
            try:
                conversation = await self.conversation.get_conversation(
                    user.id, request.conversation_id
                )
            except AIConversationNotFoundError as exc:
                raise AIContextResourceNotFoundError from exc
            except AIContextResourceNotFoundError:
                raise
            except Exception as exc:
                raise AIContextRequiredSourceError("conversation_source_unavailable") from exc
            if conversation.conversation.user_id != user.id:
                raise AIContextOwnershipError
            if conversation.conversation.status == AIConversationStatus.DELETED:
                raise AIContextResourceNotFoundError

        return _SourceSnapshot(assessment, workout, nutrition, conversation, failures)

    def _safety_section(self, snapshot: _SourceSnapshot) -> AIContextSection:
        result = snapshot.assessment
        sources = [AIContextSourceType.ASSESSMENT_SERVICE]
        data: dict[str, Any]
        truncated = False
        if result:
            values = self._assessment_values(result)
            explanations = [self._bound_text(item) for item in result.safety_explanations]
            if len(explanations) > self.limits.maximum_safety_explanations:
                explanations = explanations[: self.limits.maximum_safety_explanations]
                truncated = True
            injuries = self._string_list(values.get("injury_area"))
            age = self._integer(values.get("age"))
            data = {
                "assessment_available": True,
                "safety_status": result.safety_status.value,
                "risk_level": result.risk_level.value,
                "readiness_score": result.readiness_score,
                "safety_explanations": explanations,
                "confirmed_injuries": list(injuries),
                "minor_status": age < 18 if age is not None else None,
            }
        else:
            data = {
                "assessment_available": False,
                "safety_status": "not_assessed",
                "risk_level": "unknown",
                "readiness_score": None,
                "safety_explanations": [
                    "No completed assessment is available; personalized safety context is limited."
                ],
                "confirmed_injuries": [],
                "minor_status": None,
            }
        if snapshot.workout:
            data["workout_restrictions"] = list(snapshot.workout.plan.injuries)
            sources.append(AIContextSourceType.WORKOUT_SERVICE)
        if snapshot.nutrition:
            data["allergy_restrictions"] = [str(item) for item in snapshot.nutrition.plan.allergies]
            data["dietary_restrictions"] = [
                str(item) for item in snapshot.nutrition.plan.preferences
            ]
            sources.append(AIContextSourceType.NUTRITION_SERVICE)
        return self._section(
            AIContextSectionName.SAFETY,
            tuple(sources),
            data,
            "Existing deterministic safety and restriction outputs always have first priority.",
            truncated,
        )

    def _goals_section(self, result: AssessmentResult | None) -> AIContextSection | None:
        if not result:
            return None
        values = self._assessment_values(result)
        goal = values.get("primary_goal")
        if not isinstance(goal, str):
            return None
        data: dict[str, Any] = {"primary_goal": goal}
        target_weight = self._number(values.get("target_weight"))
        if target_weight is not None:
            data["target_weight"] = target_weight
        return self._section(
            AIContextSectionName.GOALS,
            (AIContextSourceType.ASSESSMENT_SERVICE,),
            data,
            "Current confirmed goals are relevant to this context purpose.",
        )

    def _assessment_section(self, result: AssessmentResult | None) -> AIContextSection | None:
        if not result:
            return None
        data: dict[str, Any] = {
            "assessment_version": result.assessment_version,
            "assessment_completeness": result.assessment_completeness,
            "readiness_score": result.readiness_score,
            "risk_level": result.risk_level.value,
            "safety_status": result.safety_status.value,
            "goals_summary": list(result.summary.goals),
            "lifestyle_summary": list(result.summary.lifestyle),
            "medical_considerations": list(result.summary.medical_considerations),
            "training_readiness": self._bound_text(result.summary.training_readiness),
            "equipment_summary": list(result.summary.equipment),
            "experience": result.summary.experience,
        }
        return self._section(
            AIContextSectionName.ASSESSMENT,
            (AIContextSourceType.ASSESSMENT_SERVICE,),
            data,
            "The latest completed deterministic assessment supports this purpose.",
        )

    def _profile_section(
        self, user: User, purpose: AIContextPurpose, snapshot: _SourceSnapshot
    ) -> AIContextSection | None:
        values = self._assessment_values(snapshot.assessment) if snapshot.assessment else {}
        data: dict[str, Any] = {"preferred_units": user.preferred_units or "metric"}
        workout_purposes = {
            AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            AIContextPurpose.GENERAL_FITNESS_QUESTION,
            AIContextPurpose.SUGGEST_APPROVED_WORKOUT_ALTERNATIVE,
        }
        nutrition_purposes = {
            AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
            AIContextPurpose.GENERAL_NUTRITION_QUESTION,
            AIContextPurpose.SUGGEST_APPROVED_NUTRITION_ALTERNATIVE,
        }
        if purpose in workout_purposes:
            experience = values.get("experience")
            if isinstance(experience, str):
                data["experience"] = experience
            equipment_key = (
                "equipment_available"
                if values.get("home_training") is True
                else "commercial_gym_equipment"
            )
            data["equipment"] = list(self._string_list(values.get(equipment_key)))
            data["training_at_home"] = (
                values.get("home_training")
                if isinstance(values.get("home_training"), bool)
                else None
            )
        if purpose in nutrition_purposes:
            for source_key, target_key in (
                ("age", "age"),
                ("height", "height_cm"),
                ("current_weight", "weight_kg"),
            ):
                value = self._number(values.get(source_key))
                if value is not None:
                    data[target_key] = value
        if len(data) == 1 and user.preferred_units is None:
            return None
        return self._section(
            AIContextSectionName.PROFILE,
            (AIContextSourceType.AUTHENTICATED_USER, AIContextSourceType.ASSESSMENT_SERVICE),
            data,
            "Only purpose-required profile fields and approved units are included.",
        )

    def _workout_section(self, state: CurrentWorkoutState | None) -> AIContextSection | None:
        if not state:
            return None
        plan = state.plan
        exercises = list(state.today.exercises[: self.limits.maximum_workout_items])
        truncated = len(state.today.exercises) > len(exercises)
        data: dict[str, Any] = {
            "goal": plan.goal.value,
            "experience": plan.experience.value,
            "location": plan.location.value,
            "equipment": [item.value for item in plan.equipment],
            "injuries": list(plan.injuries),
            "available_days": plan.available_days,
            "session_duration_minutes": plan.session_duration_minutes,
            "plan_version": plan.version,
            "current_day": {
                "title": state.today.title,
                "focus": state.today.focus,
                "estimated_duration_minutes": state.today.estimated_duration_minutes,
                "exercises": [
                    {
                        "name": item.name,
                        "sets": item.sets,
                        "reps": item.reps,
                        "rest_seconds": item.rest_seconds,
                    }
                    for item in exercises
                ],
            },
        }
        return self._section(
            AIContextSectionName.WORKOUT,
            (AIContextSourceType.WORKOUT_SERVICE,),
            data,
            "A bounded summary of the active deterministic workout plan is relevant.",
            truncated,
        )

    def _nutrition_section(self, state: NutritionCurrentState | None) -> AIContextSection | None:
        if not state:
            return None
        plan = state.plan
        meals = list(plan.meal_plan.meals[: self.limits.maximum_nutrition_items])
        truncated = len(plan.meal_plan.meals) > len(meals)
        data: dict[str, Any] = {
            "goal": plan.goal.value,
            "diet_type": plan.diet_type.value,
            "allergies": [item.value for item in plan.allergies],
            "dietary_preferences": [item.value for item in plan.preferences],
            "activity_level": plan.activity_level.value,
            "meal_count": plan.meal_count,
            "plan_version": plan.version,
            "targets": {
                "calories": plan.target.calories,
                "protein_grams": plan.target.protein_grams,
                "carbohydrate_grams": plan.target.carbohydrate_grams,
                "fat_grams": plan.target.fat_grams,
                "fiber_grams": plan.target.fiber_grams,
                "hydration_ml": plan.target.hydration.milliliters,
            },
            "approved_meals": [
                {
                    "name": meal.name,
                    "meal_type": meal.meal_type.value,
                    "calories": meal.calories,
                    "food_names": [
                        serving.food_name
                        for serving in meal.servings[: self.limits.maximum_nutrition_items]
                    ],
                }
                for meal in meals
            ],
        }
        return self._section(
            AIContextSectionName.NUTRITION,
            (AIContextSourceType.NUTRITION_SERVICE,),
            data,
            "A bounded summary of the active deterministic nutrition plan is relevant.",
            truncated,
        )

    def _progress_section(self, snapshot: _SourceSnapshot) -> AIContextSection | None:
        records: list[dict[str, Any]] = []
        sources: list[AIContextSourceType] = []
        if snapshot.workout:
            session = snapshot.workout.session
            records.append(
                {
                    "category": "current_workout",
                    "status": session.status.value if session else "not_started",
                    "completion_percentage": (
                        session.progress.completion_percentage if session else 0
                    ),
                }
            )
            sources.append(AIContextSourceType.WORKOUT_SERVICE)
        if snapshot.nutrition:
            progress = snapshot.nutrition.progress
            records.append(
                {
                    "category": "current_nutrition",
                    "calories_consumed": progress.calories_consumed,
                    "water_consumed_ml": progress.water_consumed_ml,
                    "meals_completed": progress.meals_completed,
                }
            )
            sources.append(AIContextSourceType.NUTRITION_SERVICE)
        if not records:
            return None
        limited = records[: self.limits.maximum_progress_records]
        return self._section(
            AIContextSectionName.PROGRESS,
            tuple(sources),
            {"current_progress": limited},
            "Only current user-approved product progress is included.",
            len(records) > len(limited),
        )

    def _preferences_section(
        self, user: User, nutrition: NutritionCurrentState | None
    ) -> AIContextSection | None:
        data: dict[str, Any] = {"preferred_units": user.preferred_units or "metric"}
        sources = [AIContextSourceType.AUTHENTICATED_USER]
        if nutrition:
            data["diet_type"] = nutrition.plan.diet_type.value
            data["dietary_preferences"] = [item.value for item in nutrition.plan.preferences]
            sources.append(AIContextSourceType.NUTRITION_SERVICE)
        limited = dict(list(data.items())[: self.limits.maximum_preference_fields])
        return self._section(
            AIContextSectionName.PREFERENCES,
            tuple(sources),
            limited,
            "Only explicitly stored presentation and dietary preferences are included.",
            len(data) > len(limited),
        )

    def _conversation_section(self, detail: AIConversationDetail | None) -> AIContextSection | None:
        if not detail:
            return None
        approved_messages = [item for item in detail.messages if item.deleted_at is None]
        messages = list(approved_messages[-self.limits.maximum_conversation_messages :])
        truncated = len(detail.messages) > len(messages)
        while (
            len(messages) > 1
            and sum(len(item.content) for item in messages)
            > self.limits.maximum_conversation_characters
        ):
            messages.pop(0)
            truncated = True
        remaining_characters = self.limits.maximum_conversation_characters
        serialized_messages: list[dict[str, str]] = []
        for message in messages:
            maximum = min(
                remaining_characters,
                self.limits.maximum_text_field_characters,
            )
            content = message.content[:maximum]
            truncated = truncated or len(content) < len(message.content)
            serialized_messages.append({"role": message.role.value, "content": content})
            remaining_characters -= len(content)
        data: dict[str, Any] = {
            "messages": serialized_messages,
        }
        return self._section(
            AIContextSectionName.CONVERSATION,
            (AIContextSourceType.CONVERSATION_SERVICE,),
            data,
            "A trusted caller explicitly requested bounded immediate conversation continuity.",
            truncated or detail.messages_truncated,
        )

    def _fit_context(
        self,
        owner_reference: str,
        purpose: AIContextPurpose,
        sections: list[AIContextSection],
        omissions: dict[AIContextSectionName, AIContextOmissionRecord],
        question_characters: int,
    ) -> AIApprovedContext:
        mandatory = {AIContextSectionName.SAFETY}
        if any(section.name == AIContextSectionName.REQUEST for section in sections):
            mandatory.add(AIContextSectionName.REQUEST)
        while True:
            context = self._assemble(
                owner_reference, purpose, sections, omissions, question_characters
            )
            if context.size.serialized_size_bytes <= self.limits.maximum_serialized_bytes:
                return context
            removable = [section for section in sections if section.name not in mandatory]
            if not removable:
                raise AIContextSizeError("mandatory_context_exceeds_limit")
            removed = max(
                removable,
                key=lambda item: (_SECTION_PRIORITY[item.name], _SECTION_ORDER.index(item.name)),
            )
            sections.remove(removed)
            omissions[removed.name] = self._omission(
                removed.name,
                AIContextOmissionReason.SIZE_LIMIT,
                (
                    "The section was omitted to preserve higher-priority context "
                    "within the hard limit."
                ),
            )

    def _assemble(
        self,
        owner_reference: str,
        purpose: AIContextPurpose,
        sections: list[AIContextSection],
        omissions: Mapping[AIContextSectionName, AIContextOmissionRecord],
        question_characters: int,
    ) -> AIApprovedContext:
        inclusion_records = tuple(
            AIContextInclusionRecord(
                section=section.name,
                reason=section.inclusion_reason,
                truncated=section.truncated,
            )
            for section in sections
        )
        omission_records = tuple(omissions[name] for name in _SECTION_ORDER if name in omissions)
        sources = tuple(dict.fromkeys(source for section in sections for source in section.sources))
        conversation_section = next(
            (item for item in sections if item.name == AIContextSectionName.CONVERSATION), None
        )
        conversation_messages = 0
        conversation_characters = 0
        if conversation_section:
            raw_messages = conversation_section.data.get("messages", [])
            if isinstance(raw_messages, list):
                conversation_messages = len(raw_messages)
                conversation_characters = sum(
                    len(str(item.get("content", "")))
                    for item in raw_messages
                    if isinstance(item, dict)
                )
        metadata = AIContextBuildMetadata(
            purpose=purpose,
            included_sections=tuple(section.name for section in sections),
            omitted_sections=tuple(record.section for record in omission_records),
            truncated_sections=tuple(section.name for section in sections if section.truncated),
            data_sources_used=sources,
            generated_at=self.clock(),
        )
        size = 0
        context: AIApprovedContext | None = None
        for _ in range(8):
            context = AIApprovedContext(
                context_version=AI_CONTEXT_VERSION,
                owner_reference=owner_reference,
                purpose=purpose,
                sections=tuple(sections),
                inclusions=inclusion_records,
                omissions=omission_records,
                metadata=metadata,
                size=AIContextSizeMetadata(
                    serialized_size_bytes=size,
                    maximum_serialized_bytes=self.limits.maximum_serialized_bytes,
                    question_characters=question_characters,
                    conversation_messages=conversation_messages,
                    conversation_characters=conversation_characters,
                ),
            )
            measured = len(context.model_dump_json().encode("utf-8"))
            if measured == size:
                break
            size = measured
        if context is None:
            raise AIContextSizeError("context_measurement_failed")
        return context

    def _purpose_omissions(
        self, selected: set[AIContextSectionName], request: AIContextRequest
    ) -> dict[AIContextSectionName, AIContextOmissionRecord]:
        omissions = {
            name: self._omission(
                name,
                AIContextOmissionReason.PURPOSE_MINIMIZATION,
                "This section is not approved for the requested context purpose.",
            )
            for name in _SECTION_ORDER
            if name not in selected
        }
        if not request.include_conversation_context:
            omissions[AIContextSectionName.CONVERSATION] = self._omission(
                AIContextSectionName.CONVERSATION,
                AIContextOmissionReason.NOT_REQUESTED,
                "Conversation continuity was not explicitly requested.",
            )
        elif request.purpose not in _CONVERSATION_PURPOSES:
            omissions[AIContextSectionName.CONVERSATION] = self._omission(
                AIContextSectionName.CONVERSATION,
                AIContextOmissionReason.PURPOSE_NOT_APPROVED,
                "Conversation continuity is not approved for this context purpose.",
            )
        return omissions

    def _normalize_question(self, request: AIContextRequest) -> str | None:
        normalized = re.sub(r"\s+", " ", request.current_user_question or "").strip()
        if not normalized:
            if request.purpose in _QUESTION_REQUIRED:
                raise AIContextValidationError("current_user_question_required")
            return None
        if len(normalized) > self.limits.maximum_question_characters:
            raise AIContextValidationError("current_user_question_too_long")
        if _HTML_TAG_PATTERN.search(normalized):
            raise AIContextValidationError("current_user_question_must_be_plain_text")
        return normalized

    def _section(
        self,
        name: AIContextSectionName,
        sources: tuple[AIContextSourceType, ...],
        data: dict[str, Any],
        reason: str,
        truncated: bool = False,
    ) -> AIContextSection:
        return AIContextSection(
            name=name,
            priority=_SECTION_PRIORITY[name],
            sources=tuple(dict.fromkeys(sources)),
            data=data,
            inclusion_reason=reason,
            serialized_size_bytes=self._serialized_size(data),
            truncated=truncated,
        )

    @staticmethod
    def _omission(
        section: AIContextSectionName,
        reason_code: AIContextOmissionReason,
        reason: str,
    ) -> AIContextOmissionRecord:
        return AIContextOmissionRecord(section=section, reason_code=reason_code, reason=reason)

    @staticmethod
    def _assessment_values(result: AssessmentResult) -> dict[str, object]:
        return {
            question_id: value
            for category in result.profile.values()
            for question_id, value in category.items()
        }

    def _bound_text(self, value: str) -> str:
        return value[: self.limits.maximum_text_field_characters]

    @staticmethod
    def _string_list(value: object) -> tuple[str, ...]:
        if not isinstance(value, list):
            return ()
        return tuple(str(item) for item in value if isinstance(item, str))

    @staticmethod
    def _number(value: object) -> int | float | None:
        if isinstance(value, bool) or not isinstance(value, int | float):
            return None
        return value

    @staticmethod
    def _integer(value: object) -> int | None:
        return value if isinstance(value, int) and not isinstance(value, bool) else None

    @staticmethod
    def _serialized_size(value: object) -> int:
        return len(
            json.dumps(
                value,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
