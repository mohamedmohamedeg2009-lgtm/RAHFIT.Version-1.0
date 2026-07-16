from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.ai_classifier import (
    AICapabilityClassificationResult,
    AIClassifiedCapability,
)
from app.models.ai_context import AIApprovedContext, AIContextSectionName
from app.models.ai_policy import AIPolicyDecision, AIPolicyReasonCode, AIPolicyResult

AI_SAFETY_VERSION = "rahfit-ai-safety-v1"


class AISafetyDecision(StrEnum):
    ALLOW = "allow"
    ALLOW_WITH_CAUTION = "allow_with_caution"
    REFUSE = "refuse"
    PROFESSIONAL_GUIDANCE_REQUIRED = "professional_guidance_required"
    FALLBACK = "fallback"


class AISafetyRuleCategory(StrEnum):
    INPUT_INTEGRITY = "input_integrity"
    PROMPT_SECURITY = "prompt_security"
    POLICY = "policy"
    CLASSIFIER = "classifier"
    MEDICAL = "medical"
    INJURY = "injury"
    NUTRITION = "nutrition"
    WORKOUT = "workout"
    AGE = "age"
    DRUGS_AND_SUPPLEMENTS = "drugs_and_supplements"
    APPROVED_CONTEXT = "approved_context"


class AISafetySeverity(StrEnum):
    INFO = "info"
    CAUTION = "caution"
    HIGH = "high"
    CRITICAL = "critical"


class AISafetyFindingCategory(StrEnum):
    PROMPT_INJECTION_ATTEMPT = "prompt_injection_attempt"
    SECRET_EXTRACTION_ATTEMPT = "secret_extraction_attempt"
    POLICY_DENIED = "policy_denied"
    MEDICAL_DIAGNOSIS_REQUEST = "medical_diagnosis_request"
    MEDICAL_TREATMENT_REQUEST = "medical_treatment_request"
    URGENT_SYMPTOM = "urgent_symptom"
    INJURY_CONFLICT = "injury_conflict"
    ALLERGY_CONFLICT = "allergy_conflict"
    DIETARY_RESTRICTION_CONFLICT = "dietary_restriction_conflict"
    DANGEROUS_CALORIE_REQUEST = "dangerous_calorie_request"
    EATING_DISORDER_ENABLING = "eating_disorder_enabling"
    EXTREME_TRAINING_REQUEST = "extreme_training_request"
    SAFETY_OVERRIDE_ATTEMPT = "safety_override_attempt"
    UNSUPPORTED_REQUEST = "unsupported_request"
    LOW_READINESS = "low_readiness"
    PROFESSIONAL_GUIDANCE_FLAG = "professional_guidance_flag"
    POLICY_LIMITED = "policy_limited"
    DRUG_OR_MEDICATION_REQUEST = "drug_or_medication_request"
    MINOR_RESTRICTION = "minor_restriction"
    CONTEXT_INTEGRITY_FAILURE = "context_integrity_failure"


class AISafetyReasonCode(StrEnum):
    REQUEST_ALLOWED = "request_allowed"
    PROMPT_INJECTION_BLOCKED = "prompt_injection_blocked"
    SECRET_EXTRACTION_BLOCKED = "secret_extraction_blocked"
    SAFETY_BYPASS_BLOCKED = "safety_bypass_blocked"
    PROHIBITED_TECHNICAL_REQUEST = "prohibited_technical_request"
    POLICY_DENIED = "policy_denied"
    POLICY_PROFESSIONAL_GUIDANCE = "policy_professional_guidance"
    POLICY_LIMITED = "policy_limited"
    URGENT_SYMPTOM = "urgent_symptom_requires_professional_guidance"
    MEDICAL_DIAGNOSIS = "medical_diagnosis_requires_professional_guidance"
    MEDICAL_TREATMENT = "medical_treatment_requires_professional_guidance"
    MEDICATION_OR_DOSAGE = "medication_or_dosage_request_refused"
    MEDICAL_REQUEST_REQUIRES_GUIDANCE = "medical_request_requires_professional_guidance"
    INJURY_RESTRICTION_CONFLICT = "injury_restriction_conflict"
    ASSESSMENT_STOP_STATUS = "assessment_stop_requires_professional_guidance"
    ALLERGY_RESTRICTION_CONFLICT = "allergy_restriction_conflict"
    DIETARY_RESTRICTION_CONFLICT = "dietary_restriction_conflict"
    EXTREME_CALORIE_RESTRICTION = "extreme_calorie_restriction"
    LOW_CALORIE_REQUEST = "low_calorie_request_requires_guidance"
    DANGEROUS_FASTING = "dangerous_fasting_request"
    EATING_DISORDER_ENABLING = "eating_disorder_enabling_request"
    EXTREME_WEIGHT_LOSS = "extreme_rapid_weight_loss_request"
    AMBIGUOUS_AGGRESSIVE_DIETING = "ambiguous_aggressive_dieting_request"
    EXTREME_TRAINING = "extreme_training_request"
    TRAINING_THROUGH_SEVERE_PAIN = "training_through_severe_pain"
    DANGEROUS_HEAT_OR_DEHYDRATION = "dangerous_heat_or_dehydration_request"
    UNSAFE_PROGRESSION = "unsafe_training_progression"
    DRUG_OR_PERFORMANCE_ENHANCER = "drug_or_performance_enhancer_request"
    SUPPLEMENT_EDUCATION_CAUTION = "supplement_education_requires_caution"
    MINOR_AGGRESSIVE_DIETING = "minor_aggressive_dieting_requires_guidance"
    MINOR_SUPPLEMENT_OR_EXTREME_TRAINING = "minor_supplement_or_extreme_training_requires_guidance"
    UNSUPPORTED_REQUEST = "unsupported_request"
    LOW_CONFIDENCE_CLASSIFICATION = "low_confidence_classification"
    LOW_READINESS = "low_readiness_requires_caution"
    CONTEXT_CAUTION_STATUS = "approved_context_requires_caution"
    CONTEXT_NOT_ASSESSED = "approved_context_not_assessed"
    MISSING_CLASSIFIER_RESULT = "missing_classifier_result"
    MISSING_POLICY_RESULT = "missing_policy_result"
    MISSING_APPROVED_CONTEXT = "missing_approved_context"
    OWNER_MISMATCH = "approved_context_owner_mismatch"
    INPUT_NOT_NORMALIZED = "safety_input_not_normalized"
    INCONSISTENT_CLASSIFIER_POLICY = "inconsistent_classifier_policy"
    MISSING_SAFETY_SECTION = "missing_mandatory_safety_section"
    MALFORMED_SAFETY_CONTEXT = "malformed_safety_context"
    MISSING_REQUIRED_RESTRICTIONS = "missing_required_restriction_context"
    INTERNAL_EVALUATION_FAILURE = "internal_safety_evaluation_failure"


class AISafetyRuntimeMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    request_id: str | None = Field(default=None, max_length=128)
    locale: str | None = Field(default=None, max_length=16)


class AISafetyRequest(BaseModel):
    """Trusted internal request. No public payload is mapped to this contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    authenticated_owner_reference: str = Field(min_length=1, max_length=256)
    normalized_user_message: str = Field(min_length=1, max_length=4_000)
    classification: AICapabilityClassificationResult | None
    policy: AIPolicyResult | None
    approved_context: AIApprovedContext | None
    runtime: AISafetyRuntimeMetadata | None = None


class AISafetyFinding(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    category: AISafetyFindingCategory
    severity: AISafetySeverity
    reason_code: AISafetyReasonCode
    source_category: AISafetyRuleCategory
    metadata: dict[str, bool | int | float | str] = Field(default_factory=dict)


class AISafetyWarning(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: AISafetySeverity
    reason_code: AISafetyReasonCode
    source_category: AISafetyRuleCategory


class AISafetyEvaluationMetadata(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    evaluation_version: str = AI_SAFETY_VERSION
    evaluated_at: datetime
    classifier_reason_code: str | None
    policy_reason_code: AIPolicyReasonCode | None
    context_version: str | None
    matched_rule_ids: tuple[str, ...]


class AISafetyResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    final_decision: AISafetyDecision
    reason_code: AISafetyReasonCode
    classified_capability: AIClassifiedCapability | None
    policy_decision: AIPolicyDecision | None
    findings: tuple[AISafetyFinding, ...]
    warnings: tuple[AISafetyWarning, ...]
    requires_provider: bool
    requires_professional_guidance: bool
    allowed_context_sections: tuple[AIContextSectionName, ...]
    blocked_context_sections: tuple[AIContextSectionName, ...]
    metadata: AISafetyEvaluationMetadata

    @model_validator(mode="after")
    def validate_provider_eligibility(self) -> "AISafetyResult":
        provider_allowed = self.final_decision in {
            AISafetyDecision.ALLOW,
            AISafetyDecision.ALLOW_WITH_CAUTION,
        }
        if self.requires_provider != provider_allowed:
            raise ValueError("Provider eligibility must match the final safety decision.")
        guidance_required = self.final_decision == AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED
        if self.requires_professional_guidance != guidance_required:
            raise ValueError("Professional-guidance state must match the final decision.")
        return self


def safe_finding_metadata(**values: Any) -> dict[str, bool | int | float | str]:
    """Narrow metadata to non-sensitive scalar values at the domain boundary."""

    return {
        key: value for key, value in values.items() if isinstance(value, bool | int | float | str)
    }
