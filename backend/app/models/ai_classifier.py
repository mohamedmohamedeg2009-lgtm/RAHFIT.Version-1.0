from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.ai_policy import AICapability


class AIClassifierSpecialCapability(StrEnum):
    MEDICAL_RELATED = "medical_related"
    UNSUPPORTED = "unsupported"


type AIClassifiedCapability = AICapability | AIClassifierSpecialCapability


class AIClassificationReasonCode(StrEnum):
    ASSESSMENT_INTENT_MATCHED = "assessment_intent_matched"
    WORKOUT_INTENT_MATCHED = "workout_intent_matched"
    NUTRITION_INTENT_MATCHED = "nutrition_intent_matched"
    PROGRESS_INTENT_MATCHED = "progress_intent_matched"
    MOTIVATION_INTENT_MATCHED = "motivation_intent_matched"
    SUMMARY_INTENT_MATCHED = "summary_intent_matched"
    WORKOUT_ALTERNATIVE_INTENT_MATCHED = "workout_alternative_intent_matched"
    NUTRITION_ALTERNATIVE_INTENT_MATCHED = "nutrition_alternative_intent_matched"
    MEDICAL_INTENT_MATCHED = "medical_intent_matched"
    UNSUPPORTED_TECHNICAL_INTENT = "unsupported_technical_intent"
    UNSUPPORTED_UNRELATED_INTENT = "unsupported_unrelated_intent"
    NO_SUPPORTED_INTENT = "no_supported_intent"


class AIUnsupportedReason(StrEnum):
    PROHIBITED_TECHNICAL_REQUEST = "prohibited_technical_request"
    UNRELATED_REQUEST = "unrelated_request"
    NO_SUPPORTED_INTENT = "no_supported_intent"


class AICapabilityClassificationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    capability: AIClassifiedCapability
    confidence: float = Field(ge=0, le=1)
    matched_rules: tuple[str, ...]
    reason_code: AIClassificationReasonCode
    requires_safety_review: bool
    unsupported_reason: AIUnsupportedReason | None = None

    @model_validator(mode="after")
    def validate_supported_state(self) -> "AICapabilityClassificationResult":
        unsupported = self.capability == AIClassifierSpecialCapability.UNSUPPORTED
        if unsupported != (self.unsupported_reason is not None):
            raise ValueError("Unsupported capability and reason must be provided together.")
        if unsupported and self.requires_safety_review:
            raise ValueError("Unsupported requests do not continue to safety review.")
        if not unsupported and not self.requires_safety_review:
            raise ValueError("Supported classifications must require safety review.")
        return self
