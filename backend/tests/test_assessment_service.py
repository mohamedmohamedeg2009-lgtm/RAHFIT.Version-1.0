from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.controllers.assessment import router
from app.models.assessment import (
    AssessmentAnswer,
    AssessmentQuestion,
    AssessmentResult,
    AssessmentSession,
    AssessmentStatus,
    QuestionCategory,
    QuestionOption,
    QuestionType,
    RiskLevel,
    SafetyStatus,
    VisibilityOperator,
    VisibilityRule,
)
from app.services.assessment import (
    AssessmentAnswerValidationError,
    AssessmentIncompleteError,
    AssessmentNotFoundError,
    AssessmentSafetyStopError,
    AssessmentService,
)


def question_catalogue() -> list[AssessmentQuestion]:
    return [
        AssessmentQuestion(
            id="primary_goal",
            category=QuestionCategory.GOALS,
            title="What is your primary goal?",
            type=QuestionType.SINGLE_CHOICE,
            required=True,
            options=(
                QuestionOption(value="fitness", label="Improve fitness"),
                QuestionOption(value="strength", label="Gain strength"),
            ),
            display_order=1,
            version=1,
        ),
        AssessmentQuestion(
            id="training_days",
            category=QuestionCategory.LIFESTYLE,
            title="How many days can you train?",
            type=QuestionType.INTEGER,
            required=True,
            min=1,
            max=7,
            unit="days_per_week",
            display_order=2,
            version=1,
        ),
        AssessmentQuestion(
            id="has_injury",
            category=QuestionCategory.INJURIES,
            title="Do you have a current injury?",
            type=QuestionType.BOOLEAN,
            required=True,
            display_order=3,
            version=1,
        ),
        AssessmentQuestion(
            id="injury_details",
            category=QuestionCategory.INJURIES,
            title="Describe the limitation.",
            type=QuestionType.TEXTAREA,
            required=True,
            depends_on="has_injury",
            visibility_rule=VisibilityRule(
                question_id="has_injury",
                operator=VisibilityOperator.EQUALS,
                value=True,
            ),
            display_order=4,
            version=1,
        ),
    ]


class FakeAssessmentStore:
    def __init__(self) -> None:
        self.questions = question_catalogue()
        self.sessions: dict[str, AssessmentSession] = {}
        self.results: dict[str, AssessmentResult] = {}

    async def latest_question_version(self) -> int | None:
        return 1

    async def list_questions(self, version: int) -> list[AssessmentQuestion]:
        return [question for question in self.questions if question.version == version]

    async def find_active_session(self, user_id: str) -> AssessmentSession | None:
        return next(
            (
                session
                for session in self.sessions.values()
                if session.user_id == user_id and session.status == AssessmentStatus.IN_PROGRESS
            ),
            None,
        )

    async def create_session(self, user_id: str, version: int) -> AssessmentSession:
        now = datetime.now(UTC)
        session = AssessmentSession(
            id=f"session-{len(self.sessions) + 1}",
            user_id=user_id,
            assessment_version=version,
            created_at=now,
            updated_at=now,
            started_at=now,
            last_activity_at=now,
        )
        self.sessions[session.id] = session
        return session

    async def find_session(self, session_id: str, user_id: str) -> AssessmentSession | None:
        session = self.sessions.get(session_id)
        return session if session and session.user_id == user_id else None

    async def save_answer(
        self,
        session: AssessmentSession,
        answer: AssessmentAnswer,
        removed_question_ids: tuple[str, ...],
    ) -> AssessmentSession:
        answers = dict(session.answers)
        answers[answer.question_id] = answer
        for question_id in removed_question_ids:
            answers.pop(question_id, None)
        now = datetime.now(UTC)
        updated = session.model_copy(
            update={
                "answers": answers,
                "revision": session.revision + 1,
                "last_activity_at": now,
                "updated_at": now,
            }
        )
        self.sessions[session.id] = updated
        return updated

    async def complete_session(
        self, session: AssessmentSession, result: AssessmentResult
    ) -> AssessmentSession:
        now = datetime.now(UTC)
        completed = session.model_copy(
            update={
                "status": AssessmentStatus.COMPLETED,
                "result_id": result.id,
                "revision": session.revision + 1,
                "completed_at": now,
                "last_activity_at": now,
                "updated_at": now,
            }
        )
        self.sessions[session.id] = completed
        self.results[result.id] = result
        return completed

    async def find_result_by_session(
        self, session_id: str, user_id: str
    ) -> AssessmentResult | None:
        return next(
            (
                result
                for result in self.results.values()
                if result.session_id == session_id and result.user_id == user_id
            ),
            None,
        )

    async def find_latest_result(self, user_id: str) -> AssessmentResult | None:
        matches = [result for result in self.results.values() if result.user_id == user_id]
        return max(matches, key=lambda result: result.generated_at) if matches else None


@pytest.mark.asyncio
async def test_start_session_is_resumable_and_does_not_duplicate() -> None:
    store = FakeAssessmentStore()
    service = AssessmentService(store)

    started = await service.start_assessment("user-1")
    resumed = await service.start_assessment("user-1")

    assert started.session.id == resumed.session.id
    assert resumed.next_question is not None
    assert resumed.next_question.id == "primary_goal"
    assert len(store.sessions) == 1


@pytest.mark.asyncio
async def test_save_answer_validates_ranges_choices_and_replaces_duplicates() -> None:
    store = FakeAssessmentStore()
    service = AssessmentService(store)
    session = (await service.start_assessment("user-1")).session

    with pytest.raises(AssessmentAnswerValidationError):
        await service.save_answer("user-1", session.id, "training_days", 8)
    with pytest.raises(AssessmentAnswerValidationError):
        await service.save_answer("user-1", session.id, "primary_goal", "unsupported")

    first = await service.save_answer("user-1", session.id, "training_days", 3)
    second = await service.save_answer("user-1", session.id, "training_days", 4)

    assert len(second.session.answers) == 1
    assert second.session.answers["training_days"].value == 4
    assert second.session.revision == first.session.revision + 1


@pytest.mark.asyncio
async def test_parent_answer_change_removes_answers_from_hidden_branches() -> None:
    store = FakeAssessmentStore()
    service = AssessmentService(store)
    session = (await service.start_assessment("user-1")).session

    with_injury = await service.save_answer("user-1", session.id, "has_injury", True)
    with_details = await service.save_answer(
        "user-1", with_injury.session.id, "injury_details", "Limited knee flexion"
    )
    cleared = await service.save_answer("user-1", with_details.session.id, "has_injury", False)

    assert "injury_details" not in cleared.session.answers
    assert cleared.session.answers["has_injury"].value is False


@pytest.mark.asyncio
async def test_finish_requires_visible_answers_and_stores_versioned_result() -> None:
    store = FakeAssessmentStore()
    service = AssessmentService(store)
    state = await service.start_assessment("user-1")
    session_id = state.session.id

    await service.save_answer("user-1", session_id, "primary_goal", "fitness")
    await service.save_answer("user-1", session_id, "training_days", 3)
    await service.save_answer("user-1", session_id, "has_injury", True)

    with pytest.raises(AssessmentIncompleteError) as incomplete:
        await service.finish_assessment("user-1", session_id)
    assert incomplete.value.missing_question_ids == ("injury_details",)

    await service.save_answer("user-1", session_id, "injury_details", "Ankle limitation")
    result = await service.finish_assessment("user-1", session_id)
    latest = await service.get_latest_assessment("user-1")

    assert result.id == latest.id
    assert result.assessment_version == 1
    assert result.profile["goals"]["primary_goal"] == "fitness"
    assert result.profile["injuries"]["injury_details"] == "Ankle limitation"
    assert result.safety_status == SafetyStatus.CAUTION
    assert result.risk_level == RiskLevel.MEDIUM
    assert result.readiness_score < result.assessment_completeness
    assert result.summary.goals == ("Primary goal: fitness.",)
    assert result.summary.medical_considerations
    assert store.sessions[session_id].status == AssessmentStatus.COMPLETED


@pytest.mark.asyncio
async def test_users_cannot_access_or_change_another_users_session() -> None:
    service = AssessmentService(FakeAssessmentStore())
    session = (await service.start_assessment("owner-user")).session

    with pytest.raises(AssessmentNotFoundError):
        await service.get_session("different-user", session.id)
    with pytest.raises(AssessmentNotFoundError):
        await service.save_answer("different-user", session.id, "primary_goal", "fitness")
    with pytest.raises(AssessmentNotFoundError):
        await service.finish_assessment("different-user", session.id)


@pytest.mark.asyncio
async def test_stop_safety_status_prevents_completion() -> None:
    store = FakeAssessmentStore()
    store.questions = [
        AssessmentQuestion(
            id="chest_pain",
            category=QuestionCategory.MEDICAL,
            title="Chest pain",
            type=QuestionType.BOOLEAN,
            required=True,
            display_order=1,
            version=1,
        )
    ]
    service = AssessmentService(store)
    session = (await service.start_assessment("user-1")).session

    state = await service.save_answer("user-1", session.id, "chest_pain", True)

    assert state.progress.safety.status == SafetyStatus.STOP
    assert state.progress.safety.risk_level == RiskLevel.CRITICAL
    assert state.progress.readiness_score == 0
    with pytest.raises(AssessmentSafetyStopError):
        await service.finish_assessment("user-1", session.id)
    assert store.sessions[session.id].status == AssessmentStatus.IN_PROGRESS


def test_assessment_routes_require_authentication() -> None:
    settings = Settings(
        _env_file=None,
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = lambda: settings
    client = TestClient(app)

    assert client.get("/api/v1/assessments/questions").status_code == 401
    assert client.post("/api/v1/assessments/start", json={}).status_code == 401
