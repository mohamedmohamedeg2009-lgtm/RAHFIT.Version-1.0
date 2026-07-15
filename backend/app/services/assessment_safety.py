from dataclasses import dataclass

from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    RiskLevel,
    SafetyEvaluation,
    SafetyStatus,
)


@dataclass(frozen=True)
class SafetyRule:
    id: str
    question_id: str
    trigger_value: AnswerValue
    status: SafetyStatus
    risk_level: RiskLevel
    explanation: str


SAFETY_RULES: tuple[SafetyRule, ...] = (
    SafetyRule(
        "chest_pain_stop",
        "chest_pain",
        True,
        SafetyStatus.STOP,
        RiskLevel.CRITICAL,
        "Reported chest pain requires medical clearance before personalized exercise guidance.",
    ),
    SafetyRule(
        "loss_of_consciousness_stop",
        "loss_of_consciousness",
        True,
        SafetyStatus.STOP,
        RiskLevel.CRITICAL,
        "Reported loss of consciousness requires medical clearance before continuing.",
    ),
    SafetyRule(
        "medical_red_flag_stop",
        "medical_red_flags",
        True,
        SafetyStatus.STOP,
        RiskLevel.CRITICAL,
        "A reported medical red flag requires professional review before continuing.",
    ),
    SafetyRule(
        "recent_surgery_stop",
        "recent_surgery",
        True,
        SafetyStatus.STOP,
        RiskLevel.HIGH,
        "Recent surgery requires professional clearance before personalized training.",
    ),
    SafetyRule(
        "heart_disease_stop",
        "heart_disease",
        True,
        SafetyStatus.STOP,
        RiskLevel.HIGH,
        "Reported heart disease requires medical clearance before personalized training.",
    ),
    SafetyRule(
        "hypertension_stop",
        "uncontrolled_hypertension",
        True,
        SafetyStatus.STOP,
        RiskLevel.HIGH,
        "Reported uncontrolled hypertension requires medical clearance before continuing.",
    ),
    SafetyRule(
        "severe_dizziness_stop",
        "severe_dizziness",
        True,
        SafetyStatus.STOP,
        RiskLevel.HIGH,
        "Reported severe dizziness requires professional review before training guidance.",
    ),
    SafetyRule(
        "serious_injury_stop",
        "serious_injury",
        True,
        SafetyStatus.STOP,
        RiskLevel.HIGH,
        "A reported serious injury requires professional clearance before continuing.",
    ),
    SafetyRule(
        "pregnancy_caution",
        "pregnancy",
        True,
        SafetyStatus.CAUTION,
        RiskLevel.MEDIUM,
        "Pregnancy requires conservative guidance and appropriate professional advice.",
    ),
    SafetyRule(
        "injury_caution",
        "has_injury",
        True,
        SafetyStatus.CAUTION,
        RiskLevel.MEDIUM,
        "A reported injury requires conservative exercise selection and monitoring.",
    ),
)


class SafetyRuleEngine:
    """Evaluates deterministic safety policy without AI or probabilistic behavior."""

    def __init__(self, rules: tuple[SafetyRule, ...] = SAFETY_RULES) -> None:
        self.rules = rules

    def evaluate(self, answers: dict[str, AssessmentAnswer]) -> SafetyEvaluation:
        triggered = [rule for rule in self.rules if self._is_triggered(rule, answers)]
        if not triggered:
            return SafetyEvaluation(
                status=SafetyStatus.SAFE,
                risk_level=RiskLevel.LOW,
                explanations=("No answered safety item currently triggers a restriction.",),
            )
        status = max(triggered, key=lambda rule: self._status_rank(rule.status)).status
        risk_level = max(triggered, key=lambda rule: self._risk_rank(rule.risk_level)).risk_level
        return SafetyEvaluation(
            status=status,
            risk_level=risk_level,
            explanations=tuple(rule.explanation for rule in triggered),
            triggered_rule_ids=tuple(rule.id for rule in triggered),
        )

    @staticmethod
    def _is_triggered(rule: SafetyRule, answers: dict[str, AssessmentAnswer]) -> bool:
        answer = answers.get(rule.question_id)
        if not answer:
            return False
        if isinstance(answer.value, list):
            return rule.trigger_value in answer.value
        return answer.value == rule.trigger_value

    @staticmethod
    def _status_rank(status: SafetyStatus) -> int:
        return {
            SafetyStatus.SAFE: 0,
            SafetyStatus.CAUTION: 1,
            SafetyStatus.STOP: 2,
        }[status]

    @staticmethod
    def _risk_rank(risk_level: RiskLevel) -> int:
        return {
            RiskLevel.LOW: 0,
            RiskLevel.MEDIUM: 1,
            RiskLevel.HIGH: 2,
            RiskLevel.CRITICAL: 3,
        }[risk_level]
