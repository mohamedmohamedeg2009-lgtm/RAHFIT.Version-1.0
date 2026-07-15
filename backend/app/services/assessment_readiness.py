from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    AssessmentProgress,
    AssessmentQuestion,
    QuestionCategory,
    RiskLevel,
    SafetyEvaluation,
    SafetyStatus,
)


class ReadinessCalculator:
    """Calculates transparent completeness and readiness metrics."""

    def calculate(
        self,
        visible_questions: list[AssessmentQuestion],
        answers: dict[str, AssessmentAnswer],
        safety: SafetyEvaluation,
    ) -> AssessmentProgress:
        answered_count = sum(
            1
            for question in visible_questions
            if question.id in answers and not self._is_empty(answers[question.id].value)
        )
        completeness = (
            round(answered_count / len(visible_questions) * 100) if visible_questions else 0
        )
        missing_categories = self._missing_categories(visible_questions, answers)
        if safety.status == SafetyStatus.STOP:
            readiness = 0
        else:
            penalty = {
                RiskLevel.LOW: 0,
                RiskLevel.MEDIUM: 15,
                RiskLevel.HIGH: 35,
                RiskLevel.CRITICAL: 100,
            }[safety.risk_level]
            readiness = max(0, completeness - penalty)
        return AssessmentProgress(
            assessment_completeness=completeness,
            readiness_score=readiness,
            missing_categories=missing_categories,
            safety=safety,
        )

    @staticmethod
    def _missing_categories(
        questions: list[AssessmentQuestion], answers: dict[str, AssessmentAnswer]
    ) -> tuple[QuestionCategory, ...]:
        missing: list[QuestionCategory] = []
        categories = dict.fromkeys(question.category for question in questions)
        for category in categories:
            category_questions = [
                question for question in questions if question.category == category
            ]
            required_missing = any(
                question.required
                and (
                    question.id not in answers
                    or ReadinessCalculator._is_empty(answers[question.id].value)
                )
                for question in category_questions
            )
            category_unanswered = not any(
                question.id in answers
                and not ReadinessCalculator._is_empty(answers[question.id].value)
                for question in category_questions
            )
            if required_missing or category_unanswered:
                missing.append(category)
        return tuple(missing)

    @staticmethod
    def _is_empty(value: AnswerValue) -> bool:
        return value == "" or value == []
