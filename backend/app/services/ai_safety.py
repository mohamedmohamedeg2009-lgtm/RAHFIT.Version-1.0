import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.ai.safety_rules import (
    AGGRESSIVE_DIET_PHRASES,
    AI_SAFETY_THRESHOLDS,
    ALLERGY_OVERRIDE_PHRASES,
    BENIGN_SECURITY_EDUCATION,
    CALORIE_PATTERN,
    CONSUMPTION_INTENT_WORDS,
    DANGEROUS_HEAT_PHRASES,
    DIAGNOSIS_PHRASES,
    DIETARY_CONFLICT_TERMS,
    DRUG_AND_PED_PHRASES,
    DURATION_PATTERN,
    EATING_DISORDER_PHRASES,
    FASTING_WORDS,
    INTENTIONAL_INJURY_PHRASES,
    MEDICATION_OR_DOSAGE_PHRASES,
    NO_REST_PHRASES,
    PROHIBITED_TECHNICAL_PHRASES,
    REPETITION_PATTERN,
    RESTRICTION_OVERRIDE_PHRASES,
    SAFETY_BYPASS_PHRASES,
    SECRET_EXTRACTION_PHRASES,
    SESSION_PATTERN,
    SEVERE_PAIN_TRAINING_PHRASES,
    STARVATION_PHRASES,
    SUPPLEMENT_TERMS,
    TRAINING_WORDS,
    TREATMENT_PHRASES,
    UNSAFE_PROGRESSION_PHRASES,
    URGENT_SYMPTOM_PHRASES,
    WEIGHT_LOSS_PATTERN,
    AISafetyThresholds,
)
from app.models.ai_classifier import AIClassifierSpecialCapability
from app.models.ai_context import AIApprovedContext, AIContextSectionName
from app.models.ai_policy import (
    AICapability,
    AIPolicyDecision,
    AIPolicyReasonCode,
)
from app.models.ai_safety import (
    AI_SAFETY_VERSION,
    AISafetyDecision,
    AISafetyEvaluationMetadata,
    AISafetyFinding,
    AISafetyFindingCategory,
    AISafetyReasonCode,
    AISafetyRequest,
    AISafetyResult,
    AISafetyRuleCategory,
    AISafetySeverity,
    AISafetyWarning,
    safe_finding_metadata,
)
from app.models.user import User
from app.services.ai_classifier import CapabilityClassifier

_LOGGER = logging.getLogger(__name__)

_EXPECTED_POLICY_REASONS: dict[AICapability, AIPolicyReasonCode] = {
    AICapability.EXPLAIN_ASSESSMENT: AIPolicyReasonCode.ASSESSMENT_EXPLANATION_ALLOWED,
    AICapability.EXPLAIN_WORKOUT: AIPolicyReasonCode.WORKOUT_EXPLANATION_ALLOWED,
    AICapability.EXPLAIN_NUTRITION: AIPolicyReasonCode.NUTRITION_EXPLANATION_ALLOWED,
    AICapability.EXPLAIN_PROGRESS: AIPolicyReasonCode.PROGRESS_EXPLANATION_ALLOWED,
    AICapability.MOTIVATE: AIPolicyReasonCode.MOTIVATION_ALLOWED,
    AICapability.SUMMARIZE: AIPolicyReasonCode.SUMMARY_ALLOWED,
    AICapability.SUGGEST_WORKOUT_ALTERNATIVE: (
        AIPolicyReasonCode.WORKOUT_ALTERNATIVE_APPROVED_ONLY
    ),
    AICapability.SUGGEST_NUTRITION_ALTERNATIVE: (
        AIPolicyReasonCode.NUTRITION_ALTERNATIVE_APPROVED_ONLY
    ),
}

_CAPABILITY_CONTEXT: dict[AICapability, frozenset[AIContextSectionName]] = {
    AICapability.EXPLAIN_ASSESSMENT: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.ASSESSMENT,
            AIContextSectionName.PROFILE,
        }
    ),
    AICapability.EXPLAIN_WORKOUT: frozenset(
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
    AICapability.EXPLAIN_NUTRITION: frozenset(
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
    AICapability.EXPLAIN_PROGRESS: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.PROGRESS,
            AIContextSectionName.ASSESSMENT,
        }
    ),
    AICapability.MOTIVATE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.PROGRESS,
            AIContextSectionName.PREFERENCES,
        }
    ),
    AICapability.SUMMARIZE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.GOALS,
            AIContextSectionName.WORKOUT,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.PROGRESS,
        }
    ),
    AICapability.SUGGEST_WORKOUT_ALTERNATIVE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.WORKOUT,
            AIContextSectionName.ASSESSMENT,
        }
    ),
    AICapability.SUGGEST_NUTRITION_ALTERNATIVE: frozenset(
        {
            AIContextSectionName.SAFETY,
            AIContextSectionName.REQUEST,
            AIContextSectionName.NUTRITION,
            AIContextSectionName.ASSESSMENT,
        }
    ),
}


@dataclass(frozen=True)
class _SafetyCandidate:
    priority: int
    decision: AISafetyDecision
    reason_code: AISafetyReasonCode
    rule_id: str
    finding_category: AISafetyFindingCategory
    source_category: AISafetyRuleCategory
    severity: AISafetySeverity
    metadata: dict[str, bool | int | float | str] | None = None


class AISafetyEngine:
    """Pure pre-generation safety evaluation; it owns no I/O or generation behavior."""

    def __init__(
        self,
        *,
        thresholds: AISafetyThresholds = AI_SAFETY_THRESHOLDS,
        clock: Callable[[], datetime] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.thresholds = thresholds
        self.clock = clock or (lambda: datetime.now(UTC))
        self.logger = logger or _LOGGER

    def evaluate_safety(
        self,
        authenticated_user: User,
        request: AISafetyRequest,
    ) -> AISafetyResult:
        try:
            validation_failure = self._validate_integrity(authenticated_user, request)
            if validation_failure:
                return self._fallback(request, validation_failure[0], validation_failure[1])

            context = request.approved_context
            classification = request.classification
            policy = request.policy
            if context is None or classification is None or policy is None:
                return self._fallback(
                    request,
                    AISafetyReasonCode.INTERNAL_EVALUATION_FAILURE,
                    "unexpected_missing_trusted_input",
                )
            safety_data = self._safety_data(context)
            if safety_data is None:
                return self._fallback(
                    request,
                    AISafetyReasonCode.MISSING_SAFETY_SECTION,
                    "mandatory_safety_section_missing",
                )
            if not self._valid_safety_data(safety_data):
                return self._fallback(
                    request,
                    AISafetyReasonCode.MALFORMED_SAFETY_CONTEXT,
                    "mandatory_safety_fields_invalid",
                )

            candidates = self._collect_candidates(request, safety_data)
            selected = min(candidates, key=lambda item: item.priority)
            result = self._build_result(request, candidates, selected)
            self._log_result(authenticated_user.id, result)
            return result
        except Exception:
            return self._fallback(
                request,
                AISafetyReasonCode.INTERNAL_EVALUATION_FAILURE,
                "safety_evaluation_failed_closed",
            )

    def _validate_integrity(
        self,
        authenticated_user: User,
        request: AISafetyRequest,
    ) -> tuple[AISafetyReasonCode, str] | None:
        if request.classification is None:
            return AISafetyReasonCode.MISSING_CLASSIFIER_RESULT, "classifier_result_missing"
        if request.policy is None:
            return AISafetyReasonCode.MISSING_POLICY_RESULT, "policy_result_missing"
        if request.approved_context is None:
            return AISafetyReasonCode.MISSING_APPROVED_CONTEXT, "approved_context_missing"
        if (
            request.authenticated_owner_reference != authenticated_user.id
            or request.approved_context.owner_reference != authenticated_user.id
        ):
            return AISafetyReasonCode.OWNER_MISMATCH, "owner_reference_mismatch"
        normalized = CapabilityClassifier.normalize(request.normalized_user_message)
        if not normalized or normalized != request.normalized_user_message:
            return AISafetyReasonCode.INPUT_NOT_NORMALIZED, "normalized_message_invalid"
        if not self._policy_matches_classification(request):
            return (
                AISafetyReasonCode.INCONSISTENT_CLASSIFIER_POLICY,
                "classifier_policy_inconsistent",
            )
        return None

    @staticmethod
    def _policy_matches_classification(request: AISafetyRequest) -> bool:
        classification = request.classification
        policy = request.policy
        if classification is None or policy is None:
            return False
        capability = classification.capability
        if not isinstance(capability, AICapability):
            return True
        if policy.decision not in {
            AIPolicyDecision.ALLOW,
            AIPolicyDecision.ALLOW_WITH_LIMITS,
        }:
            return True
        return policy.reason_code == _EXPECTED_POLICY_REASONS[capability]

    @staticmethod
    def _safety_data(context: AIApprovedContext) -> Mapping[str, Any] | None:
        section = next(
            (item for item in context.sections if item.name == AIContextSectionName.SAFETY),
            None,
        )
        return section.data if section else None

    @staticmethod
    def _valid_safety_data(data: Mapping[str, Any]) -> bool:
        required = {
            "assessment_available",
            "safety_status",
            "risk_level",
            "readiness_score",
            "confirmed_injuries",
            "minor_status",
        }
        if not required.issubset(data):
            return False
        if not isinstance(data["assessment_available"], bool):
            return False
        if not isinstance(data["safety_status"], str) or not isinstance(data["risk_level"], str):
            return False
        if not isinstance(data["confirmed_injuries"], list):
            return False
        readiness = data["readiness_score"]
        minor = data["minor_status"]
        return (readiness is None or isinstance(readiness, int)) and (
            minor is None or isinstance(minor, bool)
        )

    def _collect_candidates(
        self,
        request: AISafetyRequest,
        safety_data: Mapping[str, Any],
    ) -> list[_SafetyCandidate]:
        message = request.normalized_user_message
        candidates: list[_SafetyCandidate] = []
        candidates.extend(self._injection_candidates(message))
        candidates.extend(self._policy_candidates(request))
        candidates.extend(self._medical_candidates(request, message))
        candidates.extend(self._restriction_candidates(request, safety_data, message))
        candidates.extend(self._dangerous_nutrition_candidates(safety_data, message))
        candidates.extend(self._dangerous_workout_candidates(safety_data, message))
        candidates.extend(self._drug_candidates(safety_data, message))
        candidates.extend(self._classifier_candidates(request))
        candidates.extend(self._context_candidates(request, safety_data, message))
        candidates.append(
            _SafetyCandidate(
                priority=11,
                decision=AISafetyDecision.ALLOW,
                reason_code=AISafetyReasonCode.REQUEST_ALLOWED,
                rule_id="request_allowed",
                finding_category=AISafetyFindingCategory.POLICY_LIMITED,
                source_category=AISafetyRuleCategory.POLICY,
                severity=AISafetySeverity.INFO,
            )
        )
        return candidates

    def _injection_candidates(self, message: str) -> list[_SafetyCandidate]:
        if self._contains_any(message, BENIGN_SECURITY_EDUCATION):
            return []
        if self._contains_any(message, SAFETY_BYPASS_PHRASES):
            return [
                self._candidate(
                    1,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.SAFETY_BYPASS_BLOCKED,
                    "prompt_security.safety_bypass",
                    AISafetyFindingCategory.PROMPT_INJECTION_ATTEMPT,
                    AISafetyRuleCategory.PROMPT_SECURITY,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, SECRET_EXTRACTION_PHRASES):
            return [
                self._candidate(
                    1,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.SECRET_EXTRACTION_BLOCKED,
                    "prompt_security.secret_extraction",
                    AISafetyFindingCategory.SECRET_EXTRACTION_ATTEMPT,
                    AISafetyRuleCategory.PROMPT_SECURITY,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, PROHIBITED_TECHNICAL_PHRASES):
            return [
                self._candidate(
                    1,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.PROHIBITED_TECHNICAL_REQUEST,
                    "prompt_security.prohibited_technical_action",
                    AISafetyFindingCategory.PROMPT_INJECTION_ATTEMPT,
                    AISafetyRuleCategory.PROMPT_SECURITY,
                    AISafetySeverity.HIGH,
                )
            ]
        return []

    def _policy_candidates(self, request: AISafetyRequest) -> list[_SafetyCandidate]:
        policy = request.policy
        if policy is None:
            return []
        if policy.decision == AIPolicyDecision.DENY:
            return [
                self._candidate(
                    2,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.POLICY_DENIED,
                    "policy.denied",
                    AISafetyFindingCategory.POLICY_DENIED,
                    AISafetyRuleCategory.POLICY,
                    AISafetySeverity.HIGH,
                )
            ]
        if policy.decision == AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED:
            return [
                self._candidate(
                    3,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.POLICY_PROFESSIONAL_GUIDANCE,
                    "policy.professional_guidance",
                    AISafetyFindingCategory.PROFESSIONAL_GUIDANCE_FLAG,
                    AISafetyRuleCategory.POLICY,
                    AISafetySeverity.HIGH,
                )
            ]
        if policy.decision == AIPolicyDecision.ALLOW_WITH_LIMITS:
            return [
                self._candidate(
                    9,
                    AISafetyDecision.ALLOW_WITH_CAUTION,
                    AISafetyReasonCode.POLICY_LIMITED,
                    "policy.allowed_with_limits",
                    AISafetyFindingCategory.POLICY_LIMITED,
                    AISafetyRuleCategory.POLICY,
                    AISafetySeverity.CAUTION,
                )
            ]
        return []

    def _medical_candidates(
        self,
        request: AISafetyRequest,
        message: str,
    ) -> list[_SafetyCandidate]:
        if self._contains_any(message, URGENT_SYMPTOM_PHRASES):
            return [
                self._candidate(
                    3,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.URGENT_SYMPTOM,
                    "medical.urgent_symptom",
                    AISafetyFindingCategory.URGENT_SYMPTOM,
                    AISafetyRuleCategory.MEDICAL,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, MEDICATION_OR_DOSAGE_PHRASES):
            return [
                self._candidate(
                    4,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.MEDICATION_OR_DOSAGE,
                    "medical.medication_or_dosage",
                    AISafetyFindingCategory.DRUG_OR_MEDICATION_REQUEST,
                    AISafetyRuleCategory.MEDICAL,
                    AISafetySeverity.HIGH,
                )
            ]
        if self._contains_any(message, DIAGNOSIS_PHRASES):
            return [
                self._candidate(
                    4,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.MEDICAL_DIAGNOSIS,
                    "medical.diagnosis_request",
                    AISafetyFindingCategory.MEDICAL_DIAGNOSIS_REQUEST,
                    AISafetyRuleCategory.MEDICAL,
                    AISafetySeverity.HIGH,
                )
            ]
        if self._contains_any(message, TREATMENT_PHRASES):
            return [
                self._candidate(
                    4,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.MEDICAL_TREATMENT,
                    "medical.treatment_request",
                    AISafetyFindingCategory.MEDICAL_TREATMENT_REQUEST,
                    AISafetyRuleCategory.MEDICAL,
                    AISafetySeverity.HIGH,
                )
            ]
        classification = request.classification
        if (
            classification
            and classification.capability == AIClassifierSpecialCapability.MEDICAL_RELATED
        ):
            return [
                self._candidate(
                    4,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.MEDICAL_REQUEST_REQUIRES_GUIDANCE,
                    "medical.classified_medical_request",
                    AISafetyFindingCategory.PROFESSIONAL_GUIDANCE_FLAG,
                    AISafetyRuleCategory.MEDICAL,
                    AISafetySeverity.HIGH,
                )
            ]
        return []

    def _restriction_candidates(
        self,
        request: AISafetyRequest,
        data: Mapping[str, Any],
        message: str,
    ) -> list[_SafetyCandidate]:
        classification = request.classification
        if classification is None:
            return []
        capability = classification.capability
        if (
            capability == AICapability.SUGGEST_WORKOUT_ALTERNATIVE
            and "workout_restrictions" not in data
        ):
            return [self._missing_restriction_candidate("workout")]
        if capability == AICapability.SUGGEST_NUTRITION_ALTERNATIVE and not {
            "allergy_restrictions",
            "dietary_restrictions",
        }.issubset(data):
            return [self._missing_restriction_candidate("nutrition")]

        injuries = self._normalized_strings(
            data.get("confirmed_injuries")
        ) | self._normalized_strings(data.get("workout_restrictions"))
        override = self._contains_any(message, RESTRICTION_OVERRIDE_PHRASES)
        explicit_override = self._has_any_token(
            message, {"ignore", "despite", "override", "تجاهل", "رغم", "الغ"}
        )
        named_injury = any(self._contains_phrase(message, item) for item in injuries)
        if injuries and (override or (explicit_override and named_injury)):
            return [
                self._candidate(
                    5,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.INJURY_RESTRICTION_CONFLICT,
                    "restriction.injury_override",
                    AISafetyFindingCategory.INJURY_CONFLICT,
                    AISafetyRuleCategory.INJURY,
                    AISafetySeverity.HIGH,
                )
            ]

        allergies = self._normalized_strings(data.get("allergy_restrictions"))
        allergy_override = self._contains_any(message, ALLERGY_OVERRIDE_PHRASES)
        consumption_intent = self._has_any_token(message, CONSUMPTION_INTENT_WORDS)
        allergy_named = any(self._contains_phrase(message, item) for item in allergies)
        if allergies and (allergy_override or (allergy_named and consumption_intent)):
            return [
                self._candidate(
                    5,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.ALLERGY_RESTRICTION_CONFLICT,
                    "restriction.confirmed_allergy_conflict",
                    AISafetyFindingCategory.ALLERGY_CONFLICT,
                    AISafetyRuleCategory.NUTRITION,
                    AISafetySeverity.CRITICAL,
                )
            ]

        dietary = self._normalized_strings(data.get("dietary_restrictions"))
        if self._dietary_conflict(message, dietary, consumption_intent, allergy_override):
            return [
                self._candidate(
                    5,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.DIETARY_RESTRICTION_CONFLICT,
                    "restriction.dietary_conflict",
                    AISafetyFindingCategory.DIETARY_RESTRICTION_CONFLICT,
                    AISafetyRuleCategory.NUTRITION,
                    AISafetySeverity.HIGH,
                )
            ]
        return []

    def _dangerous_nutrition_candidates(
        self,
        data: Mapping[str, Any],
        message: str,
    ) -> list[_SafetyCandidate]:
        minor = data.get("minor_status") is True
        if self._contains_any(message, EATING_DISORDER_PHRASES):
            return [
                self._candidate(
                    6,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.EATING_DISORDER_ENABLING,
                    "nutrition.eating_disorder_enabling",
                    AISafetyFindingCategory.EATING_DISORDER_ENABLING,
                    AISafetyRuleCategory.NUTRITION,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, STARVATION_PHRASES):
            return [
                self._candidate(
                    6,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.DANGEROUS_FASTING,
                    "nutrition.starvation_request",
                    AISafetyFindingCategory.EATING_DISORDER_ENABLING,
                    AISafetyRuleCategory.NUTRITION,
                    AISafetySeverity.CRITICAL,
                )
            ]
        calorie_match = CALORIE_PATTERN.search(message)
        if calorie_match:
            calories = int(calorie_match.group(1))
            if calories <= self.thresholds.extreme_daily_calories:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.REFUSE,
                        AISafetyReasonCode.EXTREME_CALORIE_RESTRICTION,
                        "nutrition.extreme_daily_calories",
                        AISafetyFindingCategory.DANGEROUS_CALORIE_REQUEST,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.CRITICAL,
                        threshold=self.thresholds.extreme_daily_calories,
                    )
                ]
            if calories < self.thresholds.low_daily_calories:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                        AISafetyReasonCode.LOW_CALORIE_REQUEST,
                        "nutrition.low_daily_calories",
                        AISafetyFindingCategory.DANGEROUS_CALORIE_REQUEST,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.HIGH,
                        threshold=self.thresholds.low_daily_calories,
                    )
                ]
        fasting_hours = self._duration_minutes(message) // 60
        if self._has_any_phrase(message, FASTING_WORDS) and fasting_hours:
            if fasting_hours >= self.thresholds.dangerous_fasting_hours:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.REFUSE,
                        AISafetyReasonCode.DANGEROUS_FASTING,
                        "nutrition.dangerous_fasting_duration",
                        AISafetyFindingCategory.EATING_DISORDER_ENABLING,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.CRITICAL,
                        threshold_hours=self.thresholds.dangerous_fasting_hours,
                    )
                ]
            if fasting_hours >= self.thresholds.caution_fasting_hours:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.ALLOW_WITH_CAUTION,
                        AISafetyReasonCode.AMBIGUOUS_AGGRESSIVE_DIETING,
                        "nutrition.caution_fasting_duration",
                        AISafetyFindingCategory.DANGEROUS_CALORIE_REQUEST,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.CAUTION,
                    )
                ]
        weight_loss_rate = self._weekly_weight_loss(message)
        if weight_loss_rate is not None:
            if weight_loss_rate >= self.thresholds.extreme_weight_loss_kg_per_week:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.REFUSE,
                        AISafetyReasonCode.EXTREME_WEIGHT_LOSS,
                        "nutrition.extreme_weight_loss_rate",
                        AISafetyFindingCategory.EATING_DISORDER_ENABLING,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.CRITICAL,
                        threshold=self.thresholds.extreme_weight_loss_kg_per_week,
                    )
                ]
            if weight_loss_rate > self.thresholds.caution_weight_loss_kg_per_week:
                return [
                    self._candidate(
                        6,
                        AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                        AISafetyReasonCode.EXTREME_WEIGHT_LOSS,
                        "nutrition.rapid_weight_loss_rate",
                        AISafetyFindingCategory.DANGEROUS_CALORIE_REQUEST,
                        AISafetyRuleCategory.NUTRITION,
                        AISafetySeverity.HIGH,
                    )
                ]
        aggressive = self._contains_any(message, AGGRESSIVE_DIET_PHRASES)
        if minor and (aggressive or calorie_match or fasting_hours):
            return [
                self._candidate(
                    6,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.MINOR_AGGRESSIVE_DIETING,
                    "age.minor_aggressive_dieting",
                    AISafetyFindingCategory.MINOR_RESTRICTION,
                    AISafetyRuleCategory.AGE,
                    AISafetySeverity.HIGH,
                )
            ]
        if aggressive:
            return [
                self._candidate(
                    6,
                    AISafetyDecision.ALLOW_WITH_CAUTION,
                    AISafetyReasonCode.AMBIGUOUS_AGGRESSIVE_DIETING,
                    "nutrition.ambiguous_aggressive_diet",
                    AISafetyFindingCategory.DANGEROUS_CALORIE_REQUEST,
                    AISafetyRuleCategory.NUTRITION,
                    AISafetySeverity.CAUTION,
                )
            ]
        return []

    def _dangerous_workout_candidates(
        self,
        data: Mapping[str, Any],
        message: str,
    ) -> list[_SafetyCandidate]:
        if self._contains_any(message, SEVERE_PAIN_TRAINING_PHRASES):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.TRAINING_THROUGH_SEVERE_PAIN,
                    "workout.training_through_severe_pain",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, INTENTIONAL_INJURY_PHRASES):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.EXTREME_TRAINING,
                    "workout.intentional_injury",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, DANGEROUS_HEAT_PHRASES):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.DANGEROUS_HEAT_OR_DEHYDRATION,
                    "workout.dangerous_heat_or_dehydration",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.CRITICAL,
                )
            ]
        if self._contains_any(message, NO_REST_PHRASES):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.EXTREME_TRAINING,
                    "workout.no_rest_training",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.HIGH,
                )
            ]
        if self._contains_any(message, UNSAFE_PROGRESSION_PHRASES):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.UNSAFE_PROGRESSION,
                    "workout.unsafe_progression",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.HIGH,
                )
            ]
        if self._has_any_phrase(message, TRAINING_WORDS) and "per week" not in message:
            minutes = self._duration_minutes(message)
            if minutes >= self.thresholds.extreme_training_minutes_per_day:
                return [
                    self._candidate(
                        7,
                        AISafetyDecision.REFUSE,
                        AISafetyReasonCode.EXTREME_TRAINING,
                        "workout.extreme_daily_duration",
                        AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                        AISafetyRuleCategory.WORKOUT,
                        AISafetySeverity.HIGH,
                        threshold_minutes=self.thresholds.extreme_training_minutes_per_day,
                    )
                ]
            if minutes >= self.thresholds.caution_training_minutes_per_day:
                return [
                    self._candidate(
                        7,
                        AISafetyDecision.ALLOW_WITH_CAUTION,
                        AISafetyReasonCode.EXTREME_TRAINING,
                        "workout.caution_daily_duration",
                        AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                        AISafetyRuleCategory.WORKOUT,
                        AISafetySeverity.CAUTION,
                    )
                ]
        session_match = SESSION_PATTERN.search(message)
        if (
            session_match
            and self._has_any_token(message, {"daily", "day", "يوم", "يوميا"})
            and int(session_match.group(1)) >= self.thresholds.excessive_sessions_per_day
        ):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.EXTREME_TRAINING,
                    "workout.excessive_daily_sessions",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.HIGH,
                )
            ]
        repetition_match = REPETITION_PATTERN.search(message)
        if (
            repetition_match
            and int(repetition_match.group(1)) >= self.thresholds.excessive_repetitions
        ):
            return [
                self._candidate(
                    7,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.EXTREME_TRAINING,
                    "workout.excessive_repetitions",
                    AISafetyFindingCategory.EXTREME_TRAINING_REQUEST,
                    AISafetyRuleCategory.WORKOUT,
                    AISafetySeverity.HIGH,
                )
            ]
        if data.get("minor_status") is True and self._contains_any(
            message, UNSAFE_PROGRESSION_PHRASES
        ):
            return [self._minor_extreme_candidate()]
        return []

    def _drug_candidates(
        self,
        data: Mapping[str, Any],
        message: str,
    ) -> list[_SafetyCandidate]:
        if self._contains_any(message, DRUG_AND_PED_PHRASES):
            return [
                self._candidate(
                    4,
                    AISafetyDecision.REFUSE,
                    AISafetyReasonCode.DRUG_OR_PERFORMANCE_ENHANCER,
                    "drugs.performance_enhancer",
                    AISafetyFindingCategory.DRUG_OR_MEDICATION_REQUEST,
                    AISafetyRuleCategory.DRUGS_AND_SUPPLEMENTS,
                    AISafetySeverity.HIGH,
                )
            ]
        if self._has_any_phrase(message, SUPPLEMENT_TERMS):
            if data.get("minor_status") is True:
                return [self._minor_extreme_candidate()]
            return [
                self._candidate(
                    10,
                    AISafetyDecision.ALLOW_WITH_CAUTION,
                    AISafetyReasonCode.SUPPLEMENT_EDUCATION_CAUTION,
                    "supplements.general_education",
                    AISafetyFindingCategory.POLICY_LIMITED,
                    AISafetyRuleCategory.DRUGS_AND_SUPPLEMENTS,
                    AISafetySeverity.CAUTION,
                )
            ]
        return []

    def _classifier_candidates(self, request: AISafetyRequest) -> list[_SafetyCandidate]:
        classification = request.classification
        if classification is None:
            return []
        if classification.capability == AIClassifierSpecialCapability.UNSUPPORTED:
            decision = (
                AISafetyDecision.REFUSE
                if classification.unsupported_reason
                and classification.unsupported_reason.value == "prohibited_technical_request"
                else AISafetyDecision.FALLBACK
            )
            return [
                self._candidate(
                    8,
                    decision,
                    AISafetyReasonCode.UNSUPPORTED_REQUEST,
                    "classifier.unsupported",
                    AISafetyFindingCategory.UNSUPPORTED_REQUEST,
                    AISafetyRuleCategory.CLASSIFIER,
                    AISafetySeverity.HIGH,
                )
            ]
        if classification.confidence < self.thresholds.low_confidence:
            return [
                self._candidate(
                    8,
                    AISafetyDecision.FALLBACK,
                    AISafetyReasonCode.LOW_CONFIDENCE_CLASSIFICATION,
                    "classifier.low_confidence",
                    AISafetyFindingCategory.UNSUPPORTED_REQUEST,
                    AISafetyRuleCategory.CLASSIFIER,
                    AISafetySeverity.CAUTION,
                    threshold=self.thresholds.low_confidence,
                )
            ]
        return []

    def _context_candidates(
        self,
        request: AISafetyRequest,
        data: Mapping[str, Any],
        message: str,
    ) -> list[_SafetyCandidate]:
        status = str(data["safety_status"])
        if not data["assessment_available"] or status == "not_assessed":
            return [
                self._candidate(
                    8,
                    AISafetyDecision.FALLBACK,
                    AISafetyReasonCode.CONTEXT_NOT_ASSESSED,
                    "context.assessment_unavailable",
                    AISafetyFindingCategory.CONTEXT_INTEGRITY_FAILURE,
                    AISafetyRuleCategory.APPROVED_CONTEXT,
                    AISafetySeverity.HIGH,
                )
            ]
        if status == "stop":
            if self._has_any_phrase(message, TRAINING_WORDS) and self._has_any_token(
                message, {"continue", "ignore", "despite", "intense", "تجاهل", "رغم", "استمر"}
            ):
                return [
                    self._candidate(
                        1,
                        AISafetyDecision.REFUSE,
                        AISafetyReasonCode.SAFETY_BYPASS_BLOCKED,
                        "context.stop_status_override",
                        AISafetyFindingCategory.SAFETY_OVERRIDE_ATTEMPT,
                        AISafetyRuleCategory.APPROVED_CONTEXT,
                        AISafetySeverity.CRITICAL,
                    )
                ]
            return [
                self._candidate(
                    3,
                    AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
                    AISafetyReasonCode.ASSESSMENT_STOP_STATUS,
                    "context.assessment_stop_status",
                    AISafetyFindingCategory.PROFESSIONAL_GUIDANCE_FLAG,
                    AISafetyRuleCategory.APPROVED_CONTEXT,
                    AISafetySeverity.CRITICAL,
                )
            ]
        readiness = data.get("readiness_score")
        if isinstance(readiness, int) and readiness < self.thresholds.low_readiness_score:
            return [
                self._candidate(
                    10,
                    AISafetyDecision.ALLOW_WITH_CAUTION,
                    AISafetyReasonCode.LOW_READINESS,
                    "context.low_readiness",
                    AISafetyFindingCategory.LOW_READINESS,
                    AISafetyRuleCategory.APPROVED_CONTEXT,
                    AISafetySeverity.CAUTION,
                    threshold=self.thresholds.low_readiness_score,
                )
            ]
        if status == "caution" or str(data["risk_level"]) in {"medium", "high", "critical"}:
            return [
                self._candidate(
                    10,
                    AISafetyDecision.ALLOW_WITH_CAUTION,
                    AISafetyReasonCode.CONTEXT_CAUTION_STATUS,
                    "context.caution_status",
                    AISafetyFindingCategory.LOW_READINESS,
                    AISafetyRuleCategory.APPROVED_CONTEXT,
                    AISafetySeverity.CAUTION,
                )
            ]
        return []

    def _build_result(
        self,
        request: AISafetyRequest,
        candidates: list[_SafetyCandidate],
        selected: _SafetyCandidate,
    ) -> AISafetyResult:
        context = request.approved_context
        classification = request.classification
        policy = request.policy
        findings = tuple(
            AISafetyFinding(
                category=item.finding_category,
                severity=item.severity,
                reason_code=item.reason_code,
                source_category=item.source_category,
                metadata=item.metadata or {},
            )
            for item in candidates
            if item.priority < 11 and item.priority <= selected.priority
        )
        warnings = tuple(
            AISafetyWarning(
                severity=item.severity,
                reason_code=item.reason_code,
                source_category=item.source_category,
            )
            for item in candidates
            if item.decision
            in {
                AISafetyDecision.ALLOW_WITH_CAUTION,
                AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
            }
            and item.priority <= selected.priority
        )
        allowed, blocked = self._context_access(request, selected.decision)
        matched = tuple(
            dict.fromkeys(
                item.rule_id
                for item in sorted(candidates, key=lambda item: item.priority)
                if item.priority <= selected.priority
            )
        )
        return AISafetyResult(
            final_decision=selected.decision,
            reason_code=selected.reason_code,
            classified_capability=classification.capability if classification else None,
            policy_decision=policy.decision if policy else None,
            findings=findings,
            warnings=warnings,
            requires_provider=selected.decision
            in {AISafetyDecision.ALLOW, AISafetyDecision.ALLOW_WITH_CAUTION},
            requires_professional_guidance=(
                selected.decision == AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED
            ),
            allowed_context_sections=allowed,
            blocked_context_sections=blocked,
            metadata=AISafetyEvaluationMetadata(
                evaluation_version=AI_SAFETY_VERSION,
                evaluated_at=self.clock(),
                classifier_reason_code=(
                    classification.reason_code.value if classification else None
                ),
                policy_reason_code=policy.reason_code if policy else None,
                context_version=context.context_version if context else None,
                matched_rule_ids=matched,
            ),
        )

    def _fallback(
        self,
        request: AISafetyRequest,
        reason: AISafetyReasonCode,
        rule_id: str,
    ) -> AISafetyResult:
        candidate = self._candidate(
            0,
            AISafetyDecision.FALLBACK,
            reason,
            rule_id,
            AISafetyFindingCategory.CONTEXT_INTEGRITY_FAILURE,
            AISafetyRuleCategory.INPUT_INTEGRITY,
            AISafetySeverity.CRITICAL,
        )
        return self._build_result(request, [candidate], candidate)

    def _context_access(
        self,
        request: AISafetyRequest,
        decision: AISafetyDecision,
    ) -> tuple[tuple[AIContextSectionName, ...], tuple[AIContextSectionName, ...]]:
        context = request.approved_context
        classification = request.classification
        if context is None:
            return (), ()
        present = tuple(section.name for section in context.sections)
        if decision not in {AISafetyDecision.ALLOW, AISafetyDecision.ALLOW_WITH_CAUTION}:
            return (), present
        if classification is None or not isinstance(classification.capability, AICapability):
            return (), present
        approved = _CAPABILITY_CONTEXT[classification.capability]
        allowed = tuple(name for name in present if name in approved)
        blocked = tuple(name for name in present if name not in approved)
        return allowed, blocked

    def _log_result(self, owner_reference: str, result: AISafetyResult) -> None:
        self.logger.info(
            "ai_safety_evaluated",
            extra={
                "owner_reference": owner_reference,
                "capability": str(result.classified_capability),
                "policy_decision": str(result.policy_decision),
                "safety_decision": result.final_decision.value,
                "reason_code": result.reason_code.value,
                "matched_rule_ids": result.metadata.matched_rule_ids,
                "finding_categories": tuple(item.category.value for item in result.findings),
                "context_version": result.metadata.context_version,
            },
        )

    @staticmethod
    def _candidate(
        priority: int,
        decision: AISafetyDecision,
        reason: AISafetyReasonCode,
        rule_id: str,
        finding: AISafetyFindingCategory,
        source: AISafetyRuleCategory,
        severity: AISafetySeverity,
        **metadata: bool | int | float | str,
    ) -> _SafetyCandidate:
        return _SafetyCandidate(
            priority=priority,
            decision=decision,
            reason_code=reason,
            rule_id=rule_id,
            finding_category=finding,
            source_category=source,
            severity=severity,
            metadata=safe_finding_metadata(**metadata),
        )

    def _missing_restriction_candidate(self, domain: str) -> _SafetyCandidate:
        return self._candidate(
            0,
            AISafetyDecision.FALLBACK,
            AISafetyReasonCode.MISSING_REQUIRED_RESTRICTIONS,
            f"context.{domain}_restrictions_missing",
            AISafetyFindingCategory.CONTEXT_INTEGRITY_FAILURE,
            AISafetyRuleCategory.APPROVED_CONTEXT,
            AISafetySeverity.CRITICAL,
        )

    def _minor_extreme_candidate(self) -> _SafetyCandidate:
        return self._candidate(
            4,
            AISafetyDecision.PROFESSIONAL_GUIDANCE_REQUIRED,
            AISafetyReasonCode.MINOR_SUPPLEMENT_OR_EXTREME_TRAINING,
            "age.minor_supplement_or_extreme_training",
            AISafetyFindingCategory.MINOR_RESTRICTION,
            AISafetyRuleCategory.AGE,
            AISafetySeverity.HIGH,
        )

    @staticmethod
    def _contains_phrase(message: str, phrase: str) -> bool:
        return f" {phrase} " in f" {message} "

    @classmethod
    def _contains_any(cls, message: str, phrases: tuple[str, ...]) -> bool:
        return any(cls._contains_phrase(message, phrase) for phrase in phrases)

    @classmethod
    def _has_any_phrase(cls, message: str, phrases: frozenset[str]) -> bool:
        return any(cls._contains_phrase(message, phrase) for phrase in phrases)

    @staticmethod
    def _has_any_token(message: str, tokens: frozenset[str] | set[str]) -> bool:
        return bool(frozenset(message.split()).intersection(tokens))

    @staticmethod
    def _normalized_strings(value: object) -> frozenset[str]:
        if not isinstance(value, list):
            return frozenset()
        return frozenset(
            normalized
            for item in value
            if isinstance(item, str)
            if (normalized := CapabilityClassifier.normalize(item))
        )

    def _dietary_conflict(
        self,
        message: str,
        restrictions: frozenset[str],
        consumption_intent: bool,
        override: bool,
    ) -> bool:
        if not restrictions:
            return False
        if override and any(self._contains_phrase(message, item) for item in restrictions):
            return True
        if not consumption_intent:
            return False
        for restriction in restrictions:
            conflict_terms = DIETARY_CONFLICT_TERMS.get(restriction, frozenset())
            if any(self._contains_phrase(message, item) for item in conflict_terms):
                return True
        return False

    @staticmethod
    def _duration_minutes(message: str) -> int:
        match = DURATION_PATTERN.search(message)
        if not match:
            return 0
        value = int(match.group(1))
        matched = match.group(0)
        if any(unit in matched for unit in ("minute", "mins", "min", "دقيقه")):
            return value
        return value * 60

    @staticmethod
    def _weekly_weight_loss(message: str) -> float | None:
        match = WEIGHT_LOSS_PATTERN.search(message)
        if not match:
            return None
        kilograms = float(match.group(1))
        period_count = int(match.group(2) or "1") or 1
        matched = match.group(0)
        if any(unit in matched for unit in ("day", "days", "يوم", "ايام")):
            return kilograms * 7 / period_count
        return kilograms / period_count
