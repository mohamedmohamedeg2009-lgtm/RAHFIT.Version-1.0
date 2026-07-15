import re
from dataclasses import dataclass
from datetime import date, time
from typing import NoReturn, Protocol
from uuid import uuid4

from app.models.assessment import (
    AnswerValue,
    AssessmentAnswer,
    AssessmentProgress,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
    QuestionType,
    SafetyEvaluation,
    SafetyStatus,
)
from app.repositories.assessments import (
    ActiveAssessmentExistsError,
    AssessmentRevisionConflictError,
)
from app.services.assessment_branching import (
    AdaptiveBranchingEngine,
    CatalogConfigurationError,
)
from app.services.assessment_readiness import ReadinessCalculator
from app.services.assessment_safety import SafetyRuleEngine
from app.services.assessment_summary import AssessmentSummaryBuilder
from app.services.assessment_validation import (
    AssessmentConsistencyError,
    AssessmentConsistencyValidator,
)


class AssessmentNotFoundError(Exception):
    """Raised when an assessment resource is absent or not owned by the actor."""


class AssessmentQuestionsUnavailableError(Exception):
    """Raised when no active, versioned question catalogue is available."""


class AssessmentStateError(Exception):
    """Raised when an operation is invalid for the session lifecycle state."""


class AssessmentConflictError(Exception):
    """Raised when concurrent assessment changes cannot be safely merged."""


class AssessmentAnswerValidationError(Exception):
    def __init__(self, question_id: str, message: str) -> None:
        super().__init__(message)
        self.question_id = question_id
        self.message = message


class AssessmentIncompleteError(Exception):
    def __init__(self, missing_question_ids: tuple[str, ...]) -> None:
        super().__init__("Required assessment questions are incomplete.")
        self.missing_question_ids = missing_question_ids


class AssessmentSafetyStopError(Exception):
    def __init__(self, evaluation: SafetyEvaluation) -> None:
        super().__init__("Assessment completion is blocked by a safety rule.")
        self.evaluation = evaluation


class AssessmentStore(Protocol):
    async def latest_question_version(self) -> int | None: ...

    async def list_questions(self, version: int) -> list[AssessmentQuestion]: ...

    async def find_active_session(self, user_id: str) -> AssessmentSession | None: ...

    async def create_session(self, user_id: str, version: int) -> AssessmentSession: ...

    async def find_session(self, session_id: str, user_id: str) -> AssessmentSession | None: ...

    async def save_answer(
        self,
        session: AssessmentSession,
        answer: AssessmentAnswer,
        removed_question_ids: tuple[str, ...],
    ) -> AssessmentSession: ...

    async def complete_session(
        self, session: AssessmentSession, result: AssessmentResult
    ) -> AssessmentSession: ...

    async def find_result_by_session(
        self, session_id: str, user_id: str
    ) -> AssessmentResult | None: ...

    async def find_latest_result(self, user_id: str) -> AssessmentResult | None: ...


@dataclass(frozen=True)
class SessionState:
    session: AssessmentSession
    next_question: AssessmentQuestion | None
    progress: AssessmentProgress


class AssessmentService:
    """Deterministic assessment lifecycle, visibility, and validation rules."""

    def __init__(
        self,
        store: AssessmentStore,
        branching: AdaptiveBranchingEngine | None = None,
        safety: SafetyRuleEngine | None = None,
        readiness: ReadinessCalculator | None = None,
        consistency: AssessmentConsistencyValidator | None = None,
        summary: AssessmentSummaryBuilder | None = None,
    ) -> None:
        self.store = store
        self.branching = branching or AdaptiveBranchingEngine()
        self.safety = safety or SafetyRuleEngine()
        self.readiness = readiness or ReadinessCalculator()
        self.consistency = consistency or AssessmentConsistencyValidator()
        self.summary = summary or AssessmentSummaryBuilder()

    async def get_questions(self, version: int | None = None) -> list[AssessmentQuestion]:
        selected_version = version or await self.store.latest_question_version()
        if selected_version is None:
            raise AssessmentQuestionsUnavailableError
        questions = await self.store.list_questions(selected_version)
        if not questions:
            raise AssessmentQuestionsUnavailableError
        try:
            self.branching.validate_catalog(questions)
        except CatalogConfigurationError as exc:
            raise AssessmentQuestionsUnavailableError from exc
        return questions

    async def start_assessment(self, user_id: str, version: int | None = None) -> SessionState:
        active = await self.store.find_active_session(user_id)
        if active:
            questions = await self.get_questions(active.assessment_version)
            return self._session_state(active, questions)

        questions = await self.get_questions(version)
        selected_version = questions[0].version
        try:
            session = await self.store.create_session(user_id, selected_version)
        except ActiveAssessmentExistsError:
            concurrent = await self.store.find_active_session(user_id)
            if not concurrent:
                raise AssessmentConflictError from None
            concurrent_questions = await self.get_questions(concurrent.assessment_version)
            return self._session_state(concurrent, concurrent_questions)
        return self._session_state(session, questions)

    async def resume_assessment(self, user_id: str, session_id: str) -> SessionState:
        session = await self._owned_session(user_id, session_id)
        if session.status != AssessmentStatus.IN_PROGRESS:
            raise AssessmentStateError("Only an in-progress assessment can be resumed.")
        questions = await self.get_questions(session.assessment_version)
        return self._session_state(session, questions)

    async def get_session(self, user_id: str, session_id: str) -> SessionState:
        session = await self._owned_session(user_id, session_id)
        questions = await self.get_questions(session.assessment_version)
        return self._session_state(session, questions)

    async def get_active_assessment(self, user_id: str) -> SessionState | None:
        """Return an owned active assessment without creating a new session."""
        session = await self.store.find_active_session(user_id)
        if not session:
            return None
        questions = await self.get_questions(session.assessment_version)
        return self._session_state(session, questions)

    async def save_answer(
        self, user_id: str, session_id: str, question_id: str, value: AnswerValue
    ) -> SessionState:
        session = await self._owned_session(user_id, session_id)
        if session.status != AssessmentStatus.IN_PROGRESS:
            raise AssessmentStateError("Answers can only be saved to an in-progress assessment.")

        questions = await self.get_questions(session.assessment_version)
        question = next((item for item in questions if item.id == question_id), None)
        if not question:
            raise AssessmentAnswerValidationError(question_id, "Question is not available.")
        if not self.branching.is_visible(question, session.answers):
            raise AssessmentAnswerValidationError(
                question_id, "Question is not available for the current assessment path."
            )
        normalized = self.validate_answer(question, value)
        answer = AssessmentAnswer(question_id=question.id, value=normalized)
        candidate_answers = dict(session.answers)
        candidate_answers[question.id] = answer
        previous_answer = session.answers.get(question.id)
        changed_question_id = (
            question.id if previous_answer and previous_answer.value != normalized else None
        )
        removed_question_ids = self.branching.invalidated_answer_ids(
            questions, candidate_answers, changed_question_id
        )
        active_candidate_answers = {
            key: candidate
            for key, candidate in candidate_answers.items()
            if key not in removed_question_ids
        }
        try:
            self.consistency.validate(active_candidate_answers)
        except AssessmentConsistencyError as exc:
            issue = exc.issues[0]
            raise AssessmentAnswerValidationError(issue.question_id, issue.message) from exc
        try:
            updated = await self.store.save_answer(session, answer, removed_question_ids)
        except AssessmentRevisionConflictError as exc:
            raise AssessmentConflictError from exc
        return self._session_state(updated, questions)

    async def get_next_question(self, user_id: str, session_id: str) -> AssessmentQuestion | None:
        state = await self.get_session(user_id, session_id)
        return state.next_question

    async def finish_assessment(self, user_id: str, session_id: str) -> AssessmentResult:
        session = await self._owned_session(user_id, session_id)
        if session.status == AssessmentStatus.COMPLETED:
            existing = await self.store.find_result_by_session(session.id, user_id)
            if not existing:
                raise AssessmentConflictError
            return existing

        questions = await self.get_questions(session.assessment_version)
        visible = self.branching.visible_questions(questions, session.answers)
        missing = tuple(
            question.id
            for question in visible
            if question.required
            and (
                question.id not in session.answers
                or self._is_empty(session.answers[question.id].value)
            )
        )
        if missing:
            raise AssessmentIncompleteError(missing)

        try:
            self.consistency.validate(session.answers)
        except AssessmentConsistencyError as exc:
            issue = exc.issues[0]
            raise AssessmentAnswerValidationError(issue.question_id, issue.message) from exc
        safety = self.safety.evaluate(session.answers)
        if safety.status == SafetyStatus.STOP:
            raise AssessmentSafetyStopError(safety)
        progress = self.readiness.calculate(visible, session.answers, safety)
        result = self.generate_assessment_result(session, visible, progress)
        try:
            await self.store.complete_session(session, result)
        except AssessmentRevisionConflictError as exc:
            latest = await self.store.find_result_by_session(session.id, user_id)
            if latest:
                return latest
            raise AssessmentConflictError from exc
        return result

    async def get_latest_assessment(self, user_id: str) -> AssessmentResult:
        result = await self.store.find_latest_result(user_id)
        if not result:
            raise AssessmentNotFoundError
        return result

    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None:
        """Return an owned result when present without translating absence into an error."""
        return await self.store.find_latest_result(user_id)

    def validate_answer(self, question: AssessmentQuestion, value: AnswerValue) -> AnswerValue:
        if question.required and self._is_empty(value):
            raise AssessmentAnswerValidationError(question.id, "An answer is required.")

        if question.type in {
            QuestionType.TEXT,
            QuestionType.TEXTAREA,
            QuestionType.DATE,
            QuestionType.TIME,
            QuestionType.SINGLE_CHOICE,
        }:
            if not isinstance(value, str):
                self._invalid_type(question)
            normalized: AnswerValue = value.strip()
        elif question.type == QuestionType.BOOLEAN:
            if not isinstance(value, bool):
                self._invalid_type(question)
            normalized = value
        elif question.type == QuestionType.INTEGER:
            if isinstance(value, bool) or not isinstance(value, int):
                self._invalid_type(question)
            normalized = value
        elif question.type in {
            QuestionType.NUMBER,
            QuestionType.HEIGHT,
            QuestionType.WEIGHT,
            QuestionType.SLIDER,
        }:
            if isinstance(value, bool) or not isinstance(value, int | float):
                self._invalid_type(question)
            normalized = value
        elif question.type == QuestionType.MULTIPLE_CHOICE:
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                self._invalid_type(question)
            if len(value) != len(set(value)):
                raise AssessmentAnswerValidationError(
                    question.id, "Multiple-choice answers cannot contain duplicates."
                )
            normalized = value
        else:
            self._invalid_type(question)

        self._validate_semantics(question, normalized)
        return normalized

    def generate_assessment_result(
        self,
        session: AssessmentSession,
        visible_questions: list[AssessmentQuestion],
        progress: AssessmentProgress,
    ) -> AssessmentResult:
        visible_by_id = {question.id: question for question in visible_questions}
        profile: dict[str, dict[str, AnswerValue]] = {}
        answered_ids: list[str] = []
        completed_categories = []
        for question in visible_questions:
            answer = session.answers.get(question.id)
            if not answer:
                continue
            category = question.category.value
            profile.setdefault(category, {})[question.id] = answer.value
            answered_ids.append(question.id)
            if question.category not in completed_categories:
                completed_categories.append(question.category)

        unknown_answers = set(session.answers) - set(visible_by_id)
        if unknown_answers:
            raise AssessmentConflictError

        return AssessmentResult(
            id=uuid4().hex,
            user_id=session.user_id,
            session_id=session.id,
            assessment_version=session.assessment_version,
            profile=profile,
            answered_question_ids=tuple(answered_ids),
            completed_categories=tuple(completed_categories),
            completion_percentage=progress.assessment_completeness,
            assessment_completeness=progress.assessment_completeness,
            readiness_score=progress.readiness_score,
            missing_categories=progress.missing_categories,
            safety_status=progress.safety.status,
            risk_level=progress.safety.risk_level,
            safety_explanations=progress.safety.explanations,
            summary=self.summary.build(session.answers, progress.safety),
        )

    async def _owned_session(self, user_id: str, session_id: str) -> AssessmentSession:
        session = await self.store.find_session(session_id, user_id)
        if not session:
            raise AssessmentNotFoundError
        return session

    @staticmethod
    def _is_empty(value: AnswerValue) -> bool:
        return value == "" or value == []

    @staticmethod
    def _invalid_type(question: AssessmentQuestion) -> NoReturn:
        raise AssessmentAnswerValidationError(
            question.id, f"Answer must match the {question.type.value} question type."
        )

    def _session_state(
        self, session: AssessmentSession, questions: list[AssessmentQuestion]
    ) -> SessionState:
        visible = self.branching.visible_questions(questions, session.answers)
        safety = self.safety.evaluate(session.answers)
        progress = self.readiness.calculate(visible, session.answers, safety)
        next_question = (
            self.branching.next_question(questions, session.answers)
            if session.status == AssessmentStatus.IN_PROGRESS
            else None
        )
        return SessionState(session, next_question, progress)

    def _validate_semantics(self, question: AssessmentQuestion, value: AnswerValue) -> None:
        if question.type == QuestionType.DATE and isinstance(value, str) and value:
            try:
                date.fromisoformat(value)
            except ValueError as exc:
                raise AssessmentAnswerValidationError(
                    question.id, "Date must use ISO format YYYY-MM-DD."
                ) from exc
        if question.type == QuestionType.TIME and isinstance(value, str) and value:
            try:
                time.fromisoformat(value)
            except ValueError as exc:
                raise AssessmentAnswerValidationError(
                    question.id, "Time must use ISO 24-hour format."
                ) from exc

        if question.type in {QuestionType.SINGLE_CHOICE, QuestionType.MULTIPLE_CHOICE}:
            allowed = {option.value for option in question.options}
            if isinstance(value, str):
                selected = {value}
            elif isinstance(value, list):
                selected = set(value)
            else:
                self._invalid_type(question)
            if not selected.issubset(allowed):
                raise AssessmentAnswerValidationError(
                    question.id, "Answer contains an unsupported choice."
                )

        if isinstance(value, int | float) and not isinstance(value, bool):
            if question.min is not None and value < question.min:
                raise AssessmentAnswerValidationError(
                    question.id, f"Answer must be at least {question.min:g}."
                )
            if question.max is not None and value > question.max:
                raise AssessmentAnswerValidationError(
                    question.id, f"Answer must be at most {question.max:g}."
                )

        rule = question.validation_rule
        if rule and isinstance(value, str):
            if rule.min_length is not None and len(value) < rule.min_length:
                raise AssessmentAnswerValidationError(
                    question.id, f"Answer must contain at least {rule.min_length} characters."
                )
            if rule.max_length is not None and len(value) > rule.max_length:
                raise AssessmentAnswerValidationError(
                    question.id, f"Answer cannot exceed {rule.max_length} characters."
                )
            if rule.pattern and not re.fullmatch(rule.pattern, value):
                raise AssessmentAnswerValidationError(
                    question.id, "Answer does not match the required format."
                )
