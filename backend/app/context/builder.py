import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, Protocol

from app.ai.context_limits import AI_CONTEXT_LIMITS
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
from app.models.user import User
from app.readiness import ReadinessChecker, ReadinessResult, ReadinessStatus
from app.services.ai_classifier import CapabilityClassifier
from app.users.models import UserIntelligenceSnapshot


class UserIntelligenceSource(Protocol):
    async def get_snapshot(self, user_id: str) -> UserIntelligenceSnapshot: ...


class UserIntelligenceContextError(Exception):
    pass


class UserIntelligenceNotReadyError(UserIntelligenceContextError):
    def __init__(self, readiness: ReadinessResult) -> None:
        super().__init__("user_intelligence_not_ready")
        self.readiness = readiness


class UserIntelligenceContextBuilder:
    """Build a minimum, owner-scoped AIApprovedContext from canonical intelligence."""

    def __init__(
        self,
        intelligence: UserIntelligenceSource,
        readiness: ReadinessChecker,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.intelligence = intelligence
        self.readiness = readiness
        self.clock = clock or (lambda: datetime.now(UTC))

    async def build_context(
        self,
        authenticated_user: User,
        request: AIContextRequest,
    ) -> AIApprovedContext:
        question = CapabilityClassifier.normalize(request.current_user_question or "")
        if not question:
            raise UserIntelligenceContextError("current_user_question_required")
        snapshot = await self.intelligence.get_snapshot(authenticated_user.id)
        if snapshot.user_id != authenticated_user.id:
            raise UserIntelligenceContextError("context_owner_mismatch")
        readiness = self.readiness.check(snapshot)
        if not readiness.ready_for_ai:
            raise UserIntelligenceNotReadyError(readiness)
        profile = snapshot.profile
        health = snapshot.health_profile
        if profile is None or health is None:
            raise UserIntelligenceNotReadyError(readiness)

        selected = self._selected_sections(request)
        sections = [self._safety_section(snapshot, readiness)]
        sections.append(
            self._section(
                AIContextSectionName.REQUEST,
                2,
                {"current_user_question": question, "untrusted_plain_text": True},
                (AIContextSourceType.CURRENT_REQUEST,),
                "The normalized current request is isolated from trusted profile facts.",
            )
        )
        if AIContextSectionName.GOALS in selected:
            sections.append(
                self._section(
                    AIContextSectionName.GOALS,
                    3,
                    {
                        "primary_goal": profile.goals.primary_goal.value,
                        "secondary_goal": (
                            profile.goals.secondary_goal.value
                            if profile.goals.secondary_goal is not None
                            else None
                        ),
                        "target_weight_kg": profile.goals.target_weight_kg,
                        "target_date": (
                            profile.goals.target_date.isoformat()
                            if profile.goals.target_date is not None
                            else None
                        ),
                    },
                    (AIContextSourceType.AUTHENTICATED_USER,),
                    "Only goal facts required for the requested purpose are included.",
                )
            )
        if AIContextSectionName.PROFILE in selected:
            sections.append(
                self._section(
                    AIContextSectionName.PROFILE,
                    4,
                    {
                        "age_group": profile.age_group.value,
                        "bmi": profile.bmi,
                        "body_fat_percentage": profile.body.body_fat_percentage,
                    },
                    (AIContextSourceType.AUTHENTICATED_USER,),
                    "Identity details are excluded; only derived physical context is included.",
                )
            )
        if AIContextSectionName.WORKOUT in selected:
            sections.append(
                self._section(
                    AIContextSectionName.WORKOUT,
                    5,
                    {
                        "experience": profile.training.experience.value,
                        "available_days": profile.training.available_days,
                        "session_duration_minutes": profile.training.session_duration_minutes,
                        "available_equipment": [
                            item.value for item in profile.training.available_equipment
                        ],
                        "workout_location": profile.training.workout_location.value,
                        "active_injury_areas": list(health.active_injury_areas),
                        "mobility_limited_areas": [
                            item.area for item in health.mobility_limitations
                        ],
                    },
                    (AIContextSourceType.AUTHENTICATED_USER,),
                    "Only training constraints needed for workout reasoning are included.",
                )
            )
        if AIContextSectionName.NUTRITION in selected:
            sections.append(
                self._section(
                    AIContextSectionName.NUTRITION,
                    5,
                    {
                        "weight_kg": profile.body.weight_kg,
                        "height_cm": profile.body.height_cm,
                        "bmr_kcal": profile.bmr_kcal,
                        "activity_level": profile.lifestyle.activity_level.value,
                        "sleep_hours": profile.lifestyle.sleep_hours,
                        "daily_water_ml": profile.lifestyle.daily_water_ml,
                        "dietary_preferences": [
                            item.value for item in profile.nutrition.dietary_preferences
                        ],
                        "allergies": [item.value for item in profile.nutrition.allergies],
                        "dietary_restrictions": list(profile.nutrition.dietary_restrictions),
                    },
                    (AIContextSourceType.AUTHENTICATED_USER,),
                    "Only nutrition-relevant measurements and restrictions are included.",
                )
            )
        sections.sort(key=lambda item: (item.priority, item.name.value))
        return self._assemble(
            authenticated_user.id,
            request.purpose,
            question,
            tuple(sections),
        )

    @staticmethod
    def _selected_sections(request: AIContextRequest) -> set[AIContextSectionName]:
        selected = {AIContextSectionName.SAFETY, AIContextSectionName.REQUEST}
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
        alternative_purposes = {
            AIContextPurpose.SUGGEST_APPROVED_WORKOUT_ALTERNATIVE,
            AIContextPurpose.SUGGEST_APPROVED_NUTRITION_ALTERNATIVE,
        }
        if request.purpose in workout_purposes:
            selected.add(AIContextSectionName.WORKOUT)
        if request.purpose in nutrition_purposes:
            selected.add(AIContextSectionName.NUTRITION)
        if request.purpose not in alternative_purposes:
            selected.add(AIContextSectionName.GOALS)
        if request.purpose in {
            AIContextPurpose.EXPLAIN_ASSESSMENT,
            AIContextPurpose.EXPLAIN_WORKOUT_PLAN,
            AIContextPurpose.EXPLAIN_NUTRITION_PLAN,
            AIContextPurpose.GENERAL_FITNESS_QUESTION,
            AIContextPurpose.GENERAL_NUTRITION_QUESTION,
            AIContextPurpose.SAFE_MOTIVATION,
        }:
            selected.add(AIContextSectionName.PROFILE)
        if request.purpose == AIContextPurpose.CLARIFY_RECOMMENDATION:
            selected.add(AIContextSectionName.GOALS)
            if request.recommendation_source == AIRecommendationSource.WORKOUT:
                selected.add(AIContextSectionName.WORKOUT)
            elif request.recommendation_source == AIRecommendationSource.NUTRITION:
                selected.add(AIContextSectionName.NUTRITION)
        return selected

    def _safety_section(
        self,
        snapshot: UserIntelligenceSnapshot,
        readiness: ReadinessResult,
    ) -> AIContextSection:
        profile = snapshot.profile
        health = snapshot.health_profile
        if profile is None or health is None:
            raise UserIntelligenceNotReadyError(readiness)
        safety_status = "caution" if readiness.status == ReadinessStatus.CAUTION else "safe"
        return self._section(
            AIContextSectionName.SAFETY,
            1,
            {
                "assessment_available": True,
                "safety_status": safety_status,
                "risk_level": "medium" if safety_status == "caution" else "low",
                "readiness_score": readiness.completeness_score,
                "safety_explanations": [item.code for item in readiness.issues],
                "confirmed_injuries": list(health.active_injury_areas),
                "minor_status": profile.identity.age < 18,
                "workout_restrictions": list(
                    dict.fromkeys(
                        (
                            *health.active_injury_areas,
                            *(item.area for item in health.mobility_limitations),
                        )
                    )
                ),
                "allergy_restrictions": [item.value for item in profile.nutrition.allergies],
                "dietary_restrictions": list(profile.nutrition.dietary_restrictions),
                "medical_clearance_required": health.requires_medical_clearance,
            },
            (AIContextSourceType.AUTHENTICATED_USER,),
            "Deterministic readiness and health restrictions are always included.",
        )

    def _assemble(
        self,
        owner_reference: str,
        purpose: AIContextPurpose,
        question: str,
        sections: tuple[AIContextSection, ...],
    ) -> AIApprovedContext:
        included = tuple(section.name for section in sections)
        all_names: tuple[AIContextSectionName, ...] = tuple(AIContextSectionName)
        omissions = tuple(
            AIContextOmissionRecord(
                section=name,
                reason_code=AIContextOmissionReason.PURPOSE_MINIMIZATION,
                reason="The section is not required for this context purpose.",
            )
            for name in all_names
            if name not in included
        )
        inclusions = tuple(
            AIContextInclusionRecord(
                section=section.name,
                reason=section.inclusion_reason,
                truncated=False,
            )
            for section in sections
        )
        sources = tuple(dict.fromkeys(source for section in sections for source in section.sources))
        metadata = AIContextBuildMetadata(
            purpose=purpose,
            included_sections=included,
            omitted_sections=tuple(item.section for item in omissions),
            truncated_sections=(),
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
                sections=sections,
                inclusions=inclusions,
                omissions=omissions,
                metadata=metadata,
                size=AIContextSizeMetadata(
                    serialized_size_bytes=size,
                    maximum_serialized_bytes=AI_CONTEXT_LIMITS.maximum_serialized_bytes,
                    question_characters=len(question),
                    conversation_messages=0,
                    conversation_characters=0,
                ),
            )
            measured = len(context.model_dump_json().encode("utf-8"))
            if measured == size:
                break
            size = measured
        if context is None or size > AI_CONTEXT_LIMITS.maximum_serialized_bytes:
            raise UserIntelligenceContextError("approved_context_size_limit_exceeded")
        return context

    @staticmethod
    def _section(
        name: AIContextSectionName,
        priority: int,
        data: dict[str, Any],
        sources: tuple[AIContextSourceType, ...],
        reason: str,
    ) -> AIContextSection:
        return AIContextSection(
            name=name,
            priority=priority,
            sources=sources,
            data=data,
            inclusion_reason=reason,
            serialized_size_bytes=len(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ),
        )
