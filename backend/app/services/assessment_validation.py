from dataclasses import dataclass

from app.models.assessment import AnswerValue, AssessmentAnswer


@dataclass(frozen=True)
class ConsistencyIssue:
    question_id: str
    message: str


class AssessmentConsistencyError(Exception):
    def __init__(self, issues: tuple[ConsistencyIssue, ...]) -> None:
        super().__init__(issues[0].message)
        self.issues = issues


class AssessmentConsistencyValidator:
    """Enforces cross-answer invariants independently of question presentation."""

    _positive_fields = ("height", "current_weight", "target_weight")
    _exclusive_none_fields = ("injury_area", "equipment_available")

    def validate(self, answers: dict[str, AssessmentAnswer]) -> None:
        values = {question_id: answer.value for question_id, answer in answers.items()}
        issues: list[ConsistencyIssue] = []
        for question_id in self._positive_fields:
            value = self._number(values.get(question_id))
            if value is not None and value <= 0:
                issues.append(ConsistencyIssue(question_id, "Value must be greater than zero."))

        age = self._number(values.get("age"))
        if age is not None and age < 13:
            issues.append(ConsistencyIssue("age", "Users must be at least 13 years old."))
        sleep = self._number(values.get("sleep_hours"))
        if sleep is not None and not 0 <= sleep <= 24:
            issues.append(
                ConsistencyIssue("sleep_hours", "Sleep duration must be between 0 and 24 hours.")
            )

        for question_id in self._exclusive_none_fields:
            selected_values = values.get(question_id)
            if (
                isinstance(selected_values, list)
                and "none" in selected_values
                and len(selected_values) > 1
            ):
                issues.append(
                    ConsistencyIssue(
                        question_id, "The 'none' option cannot be combined with other choices."
                    )
                )

        current_weight = self._number(values.get("current_weight"))
        target_weight = self._number(values.get("target_weight"))
        goal = values.get("primary_goal")
        if current_weight is not None and target_weight is not None:
            if goal == "fat_loss" and target_weight >= current_weight:
                issues.append(
                    ConsistencyIssue(
                        "target_weight",
                        "A fat-loss target must be below the current weight.",
                    )
                )
            if goal == "muscle_gain" and target_weight <= current_weight:
                issues.append(
                    ConsistencyIssue(
                        "target_weight",
                        "A muscle-gain target must be above the current weight.",
                    )
                )

        if issues:
            raise AssessmentConsistencyError(tuple(issues))

    @staticmethod
    def _number(value: AnswerValue | None) -> float | None:
        if isinstance(value, int | float) and not isinstance(value, bool):
            return float(value)
        return None
