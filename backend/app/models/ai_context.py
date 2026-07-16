from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.ai.context_limits import AI_CONTEXT_LIMITS
from app.models.ai_conversation import CONVERSATION_ID_PATTERN

AI_CONTEXT_VERSION = "rahfit-ai-context-v1"


class AIContextPurpose(StrEnum):
    EXPLAIN_ASSESSMENT = "explain_assessment"
    EXPLAIN_WORKOUT_PLAN = "explain_workout_plan"
    EXPLAIN_NUTRITION_PLAN = "explain_nutrition_plan"
    GENERAL_FITNESS_QUESTION = "general_fitness_question"
    GENERAL_NUTRITION_QUESTION = "general_nutrition_question"
    SAFE_MOTIVATION = "safe_motivation"
    SUMMARIZE_CURRENT_PLAN = "summarize_current_plan"
    CLARIFY_RECOMMENDATION = "clarify_recommendation"
    SUGGEST_APPROVED_WORKOUT_ALTERNATIVE = "suggest_approved_workout_alternative"
    SUGGEST_APPROVED_NUTRITION_ALTERNATIVE = "suggest_approved_nutrition_alternative"


class AIRecommendationSource(StrEnum):
    ASSESSMENT = "assessment"
    WORKOUT = "workout"
    NUTRITION = "nutrition"


class AIContextSectionName(StrEnum):
    SAFETY = "safety"
    REQUEST = "request"
    PROFILE = "profile"
    GOALS = "goals"
    ASSESSMENT = "assessment"
    WORKOUT = "workout"
    NUTRITION = "nutrition"
    PROGRESS = "progress"
    PREFERENCES = "preferences"
    CONVERSATION = "conversation"


class AIContextSourceType(StrEnum):
    AUTHENTICATED_USER = "authenticated_user"
    CURRENT_REQUEST = "current_request"
    ASSESSMENT_SERVICE = "assessment_service"
    WORKOUT_SERVICE = "workout_service"
    NUTRITION_SERVICE = "nutrition_service"
    CONVERSATION_SERVICE = "conversation_service"


class AIContextOmissionReason(StrEnum):
    PURPOSE_MINIMIZATION = "purpose_minimization"
    NOT_REQUESTED = "not_requested"
    PURPOSE_NOT_APPROVED = "purpose_not_approved"
    SOURCE_MISSING = "source_missing"
    SOURCE_UNAVAILABLE = "source_unavailable"
    NO_APPROVED_DATA = "no_approved_data"
    SIZE_LIMIT = "size_limit"


class AIContextRequest(BaseModel):
    """Internal request contract; authenticated ownership is intentionally absent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    purpose: AIContextPurpose
    current_user_question: str | None = Field(
        default=None, max_length=AI_CONTEXT_LIMITS.maximum_question_characters
    )
    conversation_id: str | None = Field(default=None, pattern=CONVERSATION_ID_PATTERN)
    include_conversation_context: bool = False
    recommendation_source: AIRecommendationSource | None = None

    @model_validator(mode="after")
    def validate_trusted_options(self) -> "AIContextRequest":
        if self.include_conversation_context and not self.conversation_id:
            raise ValueError("Conversation context requires a conversation ID.")
        if (
            self.purpose == AIContextPurpose.CLARIFY_RECOMMENDATION
            and self.recommendation_source is None
        ):
            raise ValueError("Clarification context requires a recommendation source.")
        if (
            self.purpose != AIContextPurpose.CLARIFY_RECOMMENDATION
            and self.recommendation_source is not None
        ):
            raise ValueError("Recommendation source is valid only for clarification context.")
        return self


class AIContextSection(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: AIContextSectionName
    priority: int = Field(ge=1, le=8)
    sources: tuple[AIContextSourceType, ...]
    data: dict[str, Any]
    inclusion_reason: str
    serialized_size_bytes: int = Field(ge=0)
    truncated: bool = False


class AIContextInclusionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    section: AIContextSectionName
    reason: str
    truncated: bool


class AIContextOmissionRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    section: AIContextSectionName
    reason_code: AIContextOmissionReason
    reason: str


class AIContextSizeMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    serialized_size_bytes: int = Field(ge=0)
    maximum_serialized_bytes: int = Field(gt=0)
    question_characters: int = Field(ge=0)
    conversation_messages: int = Field(ge=0)
    conversation_characters: int = Field(ge=0)


class AIContextBuildMetadata(BaseModel):
    model_config = ConfigDict(frozen=True)

    context_version: str = AI_CONTEXT_VERSION
    purpose: AIContextPurpose
    included_sections: tuple[AIContextSectionName, ...]
    omitted_sections: tuple[AIContextSectionName, ...]
    truncated_sections: tuple[AIContextSectionName, ...]
    data_sources_used: tuple[AIContextSourceType, ...]
    generated_at: datetime


class AIApprovedContext(BaseModel):
    """Structured context approved for future safety and orchestration stages."""

    model_config = ConfigDict(frozen=True)

    context_version: str = AI_CONTEXT_VERSION
    owner_reference: str = Field(min_length=1)
    purpose: AIContextPurpose
    sections: tuple[AIContextSection, ...]
    inclusions: tuple[AIContextInclusionRecord, ...]
    omissions: tuple[AIContextOmissionRecord, ...]
    metadata: AIContextBuildMetadata
    size: AIContextSizeMetadata
