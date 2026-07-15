from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    AssessmentSummary,
    SafetyEvaluation,
    SafetyStatus,
)


class AssessmentSummaryBuilder:
    """Builds a fixed-template summary from validated answers."""

    def build(
        self,
        answers: dict[str, AssessmentAnswer],
        safety: SafetyEvaluation,
    ) -> AssessmentSummary:
        values = {question_id: answer.value for question_id, answer in answers.items()}
        return AssessmentSummary(
            goals=self._goals(values),
            lifestyle=self._lifestyle(values),
            medical_considerations=safety.explanations,
            training_readiness=self._training_readiness(safety.status),
            equipment=self._as_strings(values.get("equipment_available")),
            experience=self._as_string(values.get("experience")),
        )

    @staticmethod
    def _goals(values: dict[str, AnswerValue]) -> tuple[str, ...]:
        goals: list[str] = []
        primary = AssessmentSummaryBuilder._as_string(values.get("primary_goal"))
        if primary:
            goals.append(f"Primary goal: {primary}.")
        target = values.get("target_weight")
        if isinstance(target, int | float) and not isinstance(target, bool):
            goals.append(f"Target weight: {target:g} kg.")
        return tuple(goals)

    @staticmethod
    def _lifestyle(values: dict[str, AnswerValue]) -> tuple[str, ...]:
        items: list[str] = []
        sleep = values.get("sleep_hours")
        if isinstance(sleep, int | float) and not isinstance(sleep, bool):
            items.append(f"Reported sleep: {sleep:g} hours per night.")
        home_training = values.get("home_training")
        if isinstance(home_training, bool):
            location = "home" if home_training else "gym or other locations"
            items.append(f"Primary training setting: {location}.")
        return tuple(items)

    @staticmethod
    def _training_readiness(status: SafetyStatus) -> str:
        return {
            SafetyStatus.SAFE: "Ready for standard assessment-based training guidance.",
            SafetyStatus.CAUTION: "Ready only for conservative guidance with stated cautions.",
            SafetyStatus.STOP: (
                "Not ready for personalized training pending professional clearance."
            ),
        }[status]

    @staticmethod
    def _as_string(value: AnswerValue | None) -> str | None:
        return value if isinstance(value, str) and value else None

    @staticmethod
    def _as_strings(value: AnswerValue | None) -> tuple[str, ...]:
        if isinstance(value, list):
            return tuple(value)
        if isinstance(value, str) and value:
            return (value,)
        return ()
