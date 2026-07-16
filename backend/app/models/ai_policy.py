from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class AICapability(StrEnum):
    EXPLAIN_ASSESSMENT = "explain_assessment"
    EXPLAIN_WORKOUT = "explain_workout"
    EXPLAIN_NUTRITION = "explain_nutrition"
    EXPLAIN_PROGRESS = "explain_progress"
    MOTIVATE = "motivate"
    SUMMARIZE = "summarize"
    SUGGEST_WORKOUT_ALTERNATIVE = "suggest_workout_alternative"
    SUGGEST_NUTRITION_ALTERNATIVE = "suggest_nutrition_alternative"


class AIAction(StrEnum):
    READ = "read"
    EXPLAIN = "explain"
    SUMMARIZE = "summarize"
    RECOMMEND = "recommend"
    ENCOURAGE = "encourage"


class AIForbiddenAction(StrEnum):
    DIAGNOSE_MEDICAL_CONDITION = "diagnose_medical_condition"
    PRESCRIBE_MEDICATION = "prescribe_medication"
    OVERRIDE_WORKOUT_ENGINE = "override_workout_engine"
    OVERRIDE_NUTRITION_ENGINE = "override_nutrition_engine"
    IGNORE_SAFETY_RESTRICTIONS = "ignore_safety_restrictions"
    REVEAL_SYSTEM_PROMPT = "reveal_system_prompt"
    REVEAL_INTERNAL_CONTEXT = "reveal_internal_context"
    REVEAL_SECRETS = "reveal_secrets"
    ACCESS_DATABASE = "access_database"
    EXECUTE_CODE = "execute_code"
    INTERNET_BROWSING = "internet_browsing"


type AIRequestedAction = AIAction | AIForbiddenAction


class AIPolicyDecision(StrEnum):
    ALLOW = "allow"
    ALLOW_WITH_LIMITS = "allow_with_limits"
    DENY = "deny"
    PROFESSIONAL_GUIDANCE_REQUIRED = "professional_guidance_required"


class AIPolicyReasonCode(StrEnum):
    ASSESSMENT_EXPLANATION_ALLOWED = "assessment_explanation_allowed"
    WORKOUT_EXPLANATION_ALLOWED = "workout_explanation_allowed"
    NUTRITION_EXPLANATION_ALLOWED = "nutrition_explanation_allowed"
    PROGRESS_EXPLANATION_ALLOWED = "progress_explanation_allowed"
    MOTIVATION_ALLOWED = "motivation_allowed"
    SUMMARY_ALLOWED = "summary_allowed"
    WORKOUT_ALTERNATIVE_APPROVED_ONLY = "workout_alternative_approved_only"
    NUTRITION_ALTERNATIVE_APPROVED_ONLY = "nutrition_alternative_approved_only"
    ACTION_NOT_PERMITTED_FOR_CAPABILITY = "action_not_permitted_for_capability"
    MEDICAL_DIAGNOSIS_REQUIRES_PROFESSIONAL = "medical_diagnosis_requires_professional_guidance"
    MEDICATION_PRESCRIPTION_FORBIDDEN = "medication_prescription_forbidden"
    WORKOUT_ENGINE_OVERRIDE_FORBIDDEN = "workout_engine_override_forbidden"
    NUTRITION_ENGINE_OVERRIDE_FORBIDDEN = "nutrition_engine_override_forbidden"
    SAFETY_OVERRIDE_FORBIDDEN = "safety_override_forbidden"
    SYSTEM_PROMPT_DISCLOSURE_FORBIDDEN = "system_prompt_disclosure_forbidden"
    INTERNAL_CONTEXT_DISCLOSURE_FORBIDDEN = "internal_context_disclosure_forbidden"
    SECRET_DISCLOSURE_FORBIDDEN = "secret_disclosure_forbidden"
    DATABASE_ACCESS_FORBIDDEN = "database_access_forbidden"
    CODE_EXECUTION_FORBIDDEN = "code_execution_forbidden"
    INTERNET_BROWSING_FORBIDDEN = "internet_browsing_forbidden"


class AIPolicyRequest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    capability: AICapability
    requested_action: AIRequestedAction


class AIPolicyResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    decision: AIPolicyDecision
    reason_code: AIPolicyReasonCode
