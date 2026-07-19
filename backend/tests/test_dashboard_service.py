from datetime import UTC, datetime, timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.controllers.auth import get_current_user
from app.controllers.dashboard import get_dashboard_service, router
from app.models.ai_provider import AIAvailability, AIAvailabilityStatus
from app.models.assessment import (
    AssessmentAnswer,
    AssessmentProgress,
    AssessmentResult,
    AssessmentSession,
    QuestionCategory,
    RiskLevel,
    SafetyEvaluation,
    SafetyStatus,
)
from app.models.dashboard import DashboardActionType, FeatureStatus
from app.models.user import User
from app.services.assessment import SessionState
from app.services.dashboard import DashboardOwnershipError, DashboardService

NOW = datetime(2026, 7, 16, 8, 0, tzinfo=UTC)


def settings() -> Settings:
    return Settings(
        _env_file=None,
        debug=False,
        mongodb_uri="mongodb://localhost:27017",
        mongodb_database="rahfit_test",
        jwt_secret_key="a" * 32,
    )


class FakeAssessmentReader:
    def __init__(
        self,
        *,
        active: SessionState | None = None,
        result: AssessmentResult | None = None,
        fail: bool = False,
    ) -> None:
        self.active = active
        self.result = result
        self.fail = fail
        self.requested_user_ids: list[str] = []

    async def get_active_assessment(self, user_id: str) -> SessionState | None:
        self.requested_user_ids.append(user_id)
        if self.fail:
            raise RuntimeError("database details must remain private")
        return self.active

    async def get_latest_assessment_optional(self, user_id: str) -> AssessmentResult | None:
        self.requested_user_ids.append(user_id)
        if self.fail:
            raise RuntimeError("database details must remain private")
        return self.result


class FakeAIAvailabilityReader:
    async def get_availability(self) -> AIAvailability:
        return AIAvailability(
            feature_enabled=True,
            status=AIAvailabilityStatus.AVAILABLE,
            provider="openai",
            model="test-model",
            reason_code="ai_provider_available",
            message="AI provider infrastructure is available.",
        )


def user(*, complete_profile: bool = True, user_id: str = "owner-user") -> User:
    return User(
        id=user_id,
        email="mohamed.ahmed@example.com",
        password_hash="hash",
        display_name="Mohamed Ahmed" if complete_profile else None,
        preferred_units="metric" if complete_profile else None,
    )


def active_state(
    *,
    safety_status: SafetyStatus = SafetyStatus.SAFE,
    completeness: int = 40,
) -> SessionState:
    risk = RiskLevel.CRITICAL if safety_status == SafetyStatus.STOP else RiskLevel.LOW
    explanations = (
        ("Reported chest pain requires medical clearance before continuing.",)
        if safety_status == SafetyStatus.STOP
        else ("No answered safety item currently triggers a restriction.",)
    )
    session = AssessmentSession(
        id="session-1",
        user_id="owner-user",
        assessment_version=1,
        answers={
            "primary_goal": AssessmentAnswer(
                question_id="primary_goal", value="fat_loss", answered_at=NOW
            )
        },
        last_activity_at=NOW,
    )
    progress = AssessmentProgress(
        assessment_completeness=completeness,
        readiness_score=max(0, completeness - 10),
        missing_categories=(QuestionCategory.MEDICAL,),
        safety=SafetyEvaluation(
            status=safety_status,
            risk_level=risk,
            explanations=explanations,
        ),
    )
    return SessionState(session=session, next_question=None, progress=progress)


def completed_result(
    *, generated_at: datetime = NOW, user_id: str = "owner-user"
) -> AssessmentResult:
    return AssessmentResult(
        id="result-1",
        user_id=user_id,
        session_id="completed-session",
        assessment_version=1,
        profile={"goals": {"primary_goal": "muscle_gain"}},
        answered_question_ids=("primary_goal",),
        completed_categories=(QuestionCategory.GOALS,),
        completion_percentage=100,
        assessment_completeness=100,
        readiness_score=86,
        safety_status=SafetyStatus.SAFE,
        risk_level=RiskLevel.LOW,
        generated_at=generated_at,
    )


async def test_no_assessment_selects_start_priority_and_locks_planning() -> None:
    dashboard = await DashboardService(FakeAssessmentReader(), clock=lambda: NOW).get_dashboard(
        user()
    )

    assert dashboard.assessment.status == "not_started"
    assert dashboard.daily_priority.action_type == DashboardActionType.START_ASSESSMENT
    assert dashboard.daily_priority.destination_route == "/assessment"
    feature_statuses = {feature.key: feature.status for feature in dashboard.features}
    assert feature_statuses["assessment"] == FeatureStatus.ACTION_REQUIRED
    assert feature_statuses["workout"] == FeatureStatus.LOCKED
    assert dashboard.progress.latest_readiness_score is None


async def test_dashboard_exposes_ai_availability_without_copying_ai_rules() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(result=completed_result()),
        ai_coach=FakeAIAvailabilityReader(),
        clock=lambda: NOW,
    ).get_dashboard(user())
    ai_feature = next(item for item in dashboard.features if item.key == "ai_coach")
    assert ai_feature.status == FeatureStatus.AVAILABLE
    assert ai_feature.destination_route is None
    assert ai_feature.reason == "AI provider infrastructure is available."


async def test_incomplete_assessment_selects_resume_with_real_progress() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(active=active_state()), clock=lambda: NOW
    ).get_dashboard(user())

    assert dashboard.daily_priority.action_type == DashboardActionType.RESUME_ASSESSMENT
    assert dashboard.daily_priority.destination_route == "/assessment/resume/session-1"
    assert dashboard.assessment.completion_percentage == 40
    assert dashboard.user.primary_goal == "fat_loss"
    assert dashboard.progress.last_activity_date == NOW


async def test_completed_safe_assessment_is_available_without_fake_future_data() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(result=completed_result()), clock=lambda: NOW
    ).get_dashboard(user())

    assert dashboard.daily_priority.action_type == DashboardActionType.VIEW_ASSESSMENT
    assert dashboard.assessment.readiness_score == 86
    assert dashboard.user.primary_goal == "muscle_gain"
    statuses = {feature.key: feature.status for feature in dashboard.features}
    assert statuses["assessment"] == FeatureStatus.AVAILABLE
    assert statuses["workout"] == FeatureStatus.COMING_SOON
    assert statuses["nutrition"] == FeatureStatus.COMING_SOON
    assert statuses["reports"] == FeatureStatus.LOCKED


async def test_stop_state_overrides_all_actions_and_blocks_plan_features() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(active=active_state(safety_status=SafetyStatus.STOP)),
        clock=lambda: NOW,
    ).get_dashboard(user())

    assert dashboard.daily_priority.action_type == DashboardActionType.REVIEW_SAFETY
    assert dashboard.daily_priority.severity == "danger"
    assert dashboard.safety_notice is not None
    assert dashboard.safety_notice.plan_generation_blocked is True
    statuses = {feature.key: feature.status for feature in dashboard.features}
    assert statuses["workout"] == FeatureStatus.LOCKED
    assert statuses["nutrition"] == FeatureStatus.LOCKED


async def test_missing_profile_state_is_explicit_after_assessment_completion() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(result=completed_result()), clock=lambda: NOW
    ).get_dashboard(user(complete_profile=False))

    assert dashboard.user.profile_completeness == 33
    assert dashboard.user.missing_profile_fields == ("display_name", "preferred_units")
    assert dashboard.user.display_name == "Mohamed Ahmed"
    assert dashboard.daily_priority.action_type == DashboardActionType.COMPLETE_PROFILE
    assert dashboard.daily_priority.destination_route == "/app#profile-summary"


async def test_old_completed_assessment_recommends_reassessment() -> None:
    old_result = completed_result(generated_at=NOW - timedelta(days=91))
    dashboard = await DashboardService(
        FakeAssessmentReader(result=old_result), clock=lambda: NOW
    ).get_dashboard(user())

    assert dashboard.assessment.reassessment_recommended is True


async def test_optional_source_failure_returns_safe_partial_dashboard() -> None:
    dashboard = await DashboardService(
        FakeAssessmentReader(fail=True), clock=lambda: NOW
    ).get_dashboard(user())

    assert dashboard.metadata.partial_data is True
    assert dashboard.metadata.data_freshness == "partial"
    assert dashboard.assessment.status == "unavailable"
    assert dashboard.daily_priority.action_type == DashboardActionType.CONTINUE_AVAILABLE
    assert "database" not in dashboard.daily_priority.description.lower()


async def test_dashboard_reader_receives_only_authenticated_owner_id() -> None:
    reader = FakeAssessmentReader(result=completed_result(user_id="authenticated-owner"))
    dashboard = await DashboardService(reader, clock=lambda: NOW).get_dashboard(
        user(user_id="authenticated-owner")
    )

    assert dashboard.metadata.partial_data is False
    assert reader.requested_user_ids == ["authenticated-owner", "authenticated-owner"]


async def test_dashboard_rejects_an_internal_cross_owner_result() -> None:
    reader = FakeAssessmentReader(result=completed_result(user_id="different-owner"))

    with pytest.raises(DashboardOwnershipError):
        await DashboardService(reader, clock=lambda: NOW).get_dashboard(user())


def test_dashboard_route_requires_authentication() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    app.dependency_overrides[get_settings] = settings

    response = TestClient(app).get("/api/v1/dashboard")

    assert response.status_code == 401


def test_dashboard_route_returns_stable_owner_scoped_schema() -> None:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    owner = user()
    reader = FakeAssessmentReader(result=completed_result())
    service = DashboardService(reader, clock=lambda: NOW)
    app.dependency_overrides[get_current_user] = lambda: owner
    app.dependency_overrides[get_dashboard_service] = lambda: service

    response = TestClient(app).get("/api/v1/dashboard")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {
        "user",
        "assessment",
        "workout",
        "nutrition",
        "daily_check_in",
        "daily_priority",
        "features",
        "safety_notice",
        "progress",
        "quick_actions",
        "metadata",
    }
    assert payload["metadata"] == {
        "generated_at": "2026-07-16T08:00:00Z",
        "data_freshness": "live",
        "partial_data": False,
        "dashboard_version": "1.1",
    }
    assert reader.requested_user_ids == [owner.id, owner.id]
