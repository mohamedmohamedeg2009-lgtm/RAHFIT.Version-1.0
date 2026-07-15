from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    AssessmentQuestion,
    VisibilityOperator,
    VisibilityRule,
)


class CatalogConfigurationError(Exception):
    """Raised when a versioned question catalogue contains invalid dependencies."""


class AdaptiveBranchingEngine:
    """Deterministically resolves visibility, priority, and invalidated branches."""

    def validate_catalog(self, questions: list[AssessmentQuestion]) -> None:
        if not questions:
            raise CatalogConfigurationError("Question catalogue cannot be empty.")
        versions = {question.version for question in questions}
        if len(versions) != 1:
            raise CatalogConfigurationError("A catalogue must contain exactly one version.")
        question_ids = {question.id for question in questions}
        if len(question_ids) != len(questions):
            raise CatalogConfigurationError("Question identifiers must be unique per version.")

        dependencies: dict[str, set[str]] = {}
        for question in questions:
            references = self._dependency_ids(question)
            if question.id in references:
                raise CatalogConfigurationError("Questions cannot depend on themselves.")
            missing = references - question_ids
            if missing:
                raise CatalogConfigurationError(
                    f"Question '{question.id}' references unavailable dependencies."
                )
            dependencies[question.id] = references
        self._reject_cycles(dependencies)

    def visible_questions(
        self,
        questions: list[AssessmentQuestion],
        answers: dict[str, AssessmentAnswer],
    ) -> list[AssessmentQuestion]:
        visible = [question for question in questions if self.is_visible(question, answers)]
        return sorted(visible, key=lambda question: self._priority_key(question, answers))

    def next_question(
        self,
        questions: list[AssessmentQuestion],
        answers: dict[str, AssessmentAnswer],
    ) -> AssessmentQuestion | None:
        return next(
            (
                question
                for question in self.visible_questions(questions, answers)
                if question.id not in answers
            ),
            None,
        )

    def invalidated_answer_ids(
        self,
        questions: list[AssessmentQuestion],
        candidate_answers: dict[str, AssessmentAnswer],
        changed_question_id: str | None = None,
    ) -> tuple[str, ...]:
        removed = [
            question.id
            for question in questions
            if question.id in candidate_answers
            and changed_question_id is not None
            and changed_question_id in self._visibility_dependency_ids(question)
        ]
        while True:
            active_answers = {
                key: answer for key, answer in candidate_answers.items() if key not in removed
            }
            newly_removed = [
                question.id
                for question in questions
                if question.id in active_answers and not self.is_visible(question, active_answers)
            ]
            if not newly_removed:
                return tuple(removed)
            for question_id in newly_removed:
                if question_id not in removed:
                    removed.append(question_id)

    def is_visible(
        self, question: AssessmentQuestion, answers: dict[str, AssessmentAnswer]
    ) -> bool:
        rules = list(question.visibility_rules)
        if question.visibility_rule:
            rules.append(question.visibility_rule)
        if rules:
            return all(self.rule_matches(rule, answers) for rule in rules)
        if not question.depends_on:
            return True
        dependency = answers.get(question.depends_on)
        return bool(dependency and dependency.value)

    def rule_matches(self, rule: VisibilityRule, answers: dict[str, AssessmentAnswer]) -> bool:
        answer = answers.get(rule.question_id)
        if not answer:
            return False
        return self._compare(answer.value, rule.operator, rule.value)

    @staticmethod
    def _compare(actual: AnswerValue, operator: VisibilityOperator, expected: AnswerValue) -> bool:
        if operator == VisibilityOperator.EQUALS:
            return actual == expected
        if operator == VisibilityOperator.NOT_EQUALS:
            return actual != expected
        if operator == VisibilityOperator.IN:
            return isinstance(expected, list) and actual in expected
        if operator == VisibilityOperator.CONTAINS:
            if isinstance(actual, list):
                return expected in actual
            return isinstance(actual, str) and isinstance(expected, str) and expected in actual
        if (
            isinstance(actual, int | float)
            and not isinstance(actual, bool)
            and isinstance(expected, int | float)
            and not isinstance(expected, bool)
        ):
            if operator == VisibilityOperator.LESS_THAN:
                return actual < expected
            if operator == VisibilityOperator.LESS_THAN_OR_EQUAL:
                return actual <= expected
            if operator == VisibilityOperator.GREATER_THAN:
                return actual > expected
            if operator == VisibilityOperator.GREATER_THAN_OR_EQUAL:
                return actual >= expected
        return False

    def _priority_key(
        self,
        question: AssessmentQuestion,
        answers: dict[str, AssessmentAnswer],
    ) -> tuple[int, int, str]:
        adjustment = sum(
            rule.priority_delta
            for rule in question.priority_rules
            if self.rule_matches(rule.condition, answers)
        )
        return question.display_order + adjustment, question.display_order, question.id

    @staticmethod
    def _dependency_ids(question: AssessmentQuestion) -> set[str]:
        references = {rule.question_id for rule in question.visibility_rules}
        references.update(rule.condition.question_id for rule in question.priority_rules)
        if question.visibility_rule:
            references.add(question.visibility_rule.question_id)
        if question.depends_on:
            references.add(question.depends_on)
        return references

    @staticmethod
    def _visibility_dependency_ids(question: AssessmentQuestion) -> set[str]:
        references = {rule.question_id for rule in question.visibility_rules}
        if question.visibility_rule:
            references.add(question.visibility_rule.question_id)
        if question.depends_on:
            references.add(question.depends_on)
        return references

    @staticmethod
    def _reject_cycles(dependencies: dict[str, set[str]]) -> None:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(question_id: str) -> None:
            if question_id in visiting:
                raise CatalogConfigurationError("Question dependencies cannot contain cycles.")
            if question_id in visited:
                return
            visiting.add(question_id)
            for dependency in dependencies[question_id]:
                visit(dependency)
            visiting.remove(question_id)
            visited.add(question_id)

        for question_id in dependencies:
            visit(question_id)
