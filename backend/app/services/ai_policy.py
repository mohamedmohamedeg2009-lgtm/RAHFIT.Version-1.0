from app.models.ai_policy import (
    AIAction,
    AICapability,
    AIForbiddenAction,
    AIPolicyDecision,
    AIPolicyReasonCode,
    AIPolicyResult,
    AIRequestedAction,
)

type PolicyRule = tuple[AIPolicyDecision, AIPolicyReasonCode]

_ALLOW = AIPolicyDecision.ALLOW
_LIMIT = AIPolicyDecision.ALLOW_WITH_LIMITS
_DENY = AIPolicyDecision.DENY
_PROFESSIONAL = AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED

_CAPABILITY_RULES: dict[AICapability, dict[AIAction, PolicyRule]] = {
    AICapability.EXPLAIN_ASSESSMENT: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.ASSESSMENT_EXPLANATION_ALLOWED),
        AIAction.EXPLAIN: (_ALLOW, AIPolicyReasonCode.ASSESSMENT_EXPLANATION_ALLOWED),
    },
    AICapability.EXPLAIN_WORKOUT: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.WORKOUT_EXPLANATION_ALLOWED),
        AIAction.EXPLAIN: (_ALLOW, AIPolicyReasonCode.WORKOUT_EXPLANATION_ALLOWED),
    },
    AICapability.EXPLAIN_NUTRITION: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.NUTRITION_EXPLANATION_ALLOWED),
        AIAction.EXPLAIN: (_ALLOW, AIPolicyReasonCode.NUTRITION_EXPLANATION_ALLOWED),
    },
    AICapability.EXPLAIN_PROGRESS: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.PROGRESS_EXPLANATION_ALLOWED),
        AIAction.EXPLAIN: (_ALLOW, AIPolicyReasonCode.PROGRESS_EXPLANATION_ALLOWED),
        AIAction.SUMMARIZE: (_ALLOW, AIPolicyReasonCode.PROGRESS_EXPLANATION_ALLOWED),
    },
    AICapability.MOTIVATE: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.MOTIVATION_ALLOWED),
        AIAction.ENCOURAGE: (_ALLOW, AIPolicyReasonCode.MOTIVATION_ALLOWED),
    },
    AICapability.SUMMARIZE: {
        AIAction.READ: (_ALLOW, AIPolicyReasonCode.SUMMARY_ALLOWED),
        AIAction.SUMMARIZE: (_ALLOW, AIPolicyReasonCode.SUMMARY_ALLOWED),
    },
    AICapability.SUGGEST_WORKOUT_ALTERNATIVE: {
        AIAction.READ: (
            _LIMIT,
            AIPolicyReasonCode.WORKOUT_ALTERNATIVE_APPROVED_ONLY,
        ),
        AIAction.RECOMMEND: (
            _LIMIT,
            AIPolicyReasonCode.WORKOUT_ALTERNATIVE_APPROVED_ONLY,
        ),
    },
    AICapability.SUGGEST_NUTRITION_ALTERNATIVE: {
        AIAction.READ: (
            _LIMIT,
            AIPolicyReasonCode.NUTRITION_ALTERNATIVE_APPROVED_ONLY,
        ),
        AIAction.RECOMMEND: (
            _LIMIT,
            AIPolicyReasonCode.NUTRITION_ALTERNATIVE_APPROVED_ONLY,
        ),
    },
}

_FORBIDDEN_RULES: dict[AIForbiddenAction, PolicyRule] = {
    AIForbiddenAction.DIAGNOSE_MEDICAL_CONDITION: (
        _PROFESSIONAL,
        AIPolicyReasonCode.MEDICAL_DIAGNOSIS_REQUIRES_PROFESSIONAL,
    ),
    AIForbiddenAction.PRESCRIBE_MEDICATION: (
        _DENY,
        AIPolicyReasonCode.MEDICATION_PRESCRIPTION_FORBIDDEN,
    ),
    AIForbiddenAction.OVERRIDE_WORKOUT_ENGINE: (
        _DENY,
        AIPolicyReasonCode.WORKOUT_ENGINE_OVERRIDE_FORBIDDEN,
    ),
    AIForbiddenAction.OVERRIDE_NUTRITION_ENGINE: (
        _DENY,
        AIPolicyReasonCode.NUTRITION_ENGINE_OVERRIDE_FORBIDDEN,
    ),
    AIForbiddenAction.IGNORE_SAFETY_RESTRICTIONS: (
        _DENY,
        AIPolicyReasonCode.SAFETY_OVERRIDE_FORBIDDEN,
    ),
    AIForbiddenAction.REVEAL_SYSTEM_PROMPT: (
        _DENY,
        AIPolicyReasonCode.SYSTEM_PROMPT_DISCLOSURE_FORBIDDEN,
    ),
    AIForbiddenAction.REVEAL_INTERNAL_CONTEXT: (
        _DENY,
        AIPolicyReasonCode.INTERNAL_CONTEXT_DISCLOSURE_FORBIDDEN,
    ),
    AIForbiddenAction.REVEAL_SECRETS: (
        _DENY,
        AIPolicyReasonCode.SECRET_DISCLOSURE_FORBIDDEN,
    ),
    AIForbiddenAction.ACCESS_DATABASE: (
        _DENY,
        AIPolicyReasonCode.DATABASE_ACCESS_FORBIDDEN,
    ),
    AIForbiddenAction.EXECUTE_CODE: (
        _DENY,
        AIPolicyReasonCode.CODE_EXECUTION_FORBIDDEN,
    ),
    AIForbiddenAction.INTERNET_BROWSING: (
        _DENY,
        AIPolicyReasonCode.INTERNET_BROWSING_FORBIDDEN,
    ),
}


class AIPolicyService:
    """Pure deterministic permission evaluation with no I/O dependencies."""

    def evaluate(
        self,
        capability: AICapability,
        requested_action: AIRequestedAction,
    ) -> AIPolicyResult:
        if isinstance(requested_action, AIForbiddenAction):
            decision, reason_code = _FORBIDDEN_RULES[requested_action]
            return AIPolicyResult(decision=decision, reason_code=reason_code)

        rule = _CAPABILITY_RULES[capability].get(requested_action)
        if not rule:
            return AIPolicyResult(
                decision=AIPolicyDecision.DENY,
                reason_code=AIPolicyReasonCode.ACTION_NOT_PERMITTED_FOR_CAPABILITY,
            )
        decision, reason_code = rule
        return AIPolicyResult(decision=decision, reason_code=reason_code)
