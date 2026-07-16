from datetime import UTC, datetime
from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient

from app.controllers.auth import get_current_user
from app.controllers.intelligent_workout import get_intelligent_workout_service, router
from app.models.user import User
from app.workouts.adaptation import AdaptationAction, AdaptationSeverity
from app.workouts.exceptions import (
    WorkoutActivePlanConflictError,
    WorkoutGenerationError,
    WorkoutHealthProfileIncompleteError,
    WorkoutMedicalClearanceRequiredError,
    WorkoutPlanArchivedError,
    WorkoutPlanNotFoundError,
    WorkoutProfileIncompleteError,
    WorkoutReadinessBlockedError,
    WorkoutSessionNotFoundError,
    WorkoutValidationError,
)
from app.workouts.models import (
    GenerationMode,
    SessionStatus,
    WorkoutExplanation,
    WorkoutPlanType,
    WorkoutStatus,
)
from app.workouts.schemas import (
    WorkoutAdaptationResponse,
    WorkoutPlanResponse,
    WorkoutSessionResponse,
)
from app.workouts.service import WorkoutService

NOW = datetime(2026, 7, 17, 12, tzinfo=UTC)
USER = User(id="user-1", email="user@example.com", password_hash="hash")


def _plan(mode: GenerationMode = GenerationMode.DETERMINISTIC) -> WorkoutPlanResponse:
    return WorkoutPlanResponse.model_construct(
        plan_id="plan-1",
        plan_type=WorkoutPlanType.GENERAL_FITNESS,
        status=WorkoutStatus.ACTIVE,
        duration_weeks=8,
        training_days_per_week=1,
        weekly_schedule=(),
        warnings=(),
        safety_notes=("Stop for unusual symptoms.",),
        progression_guidance=("Progress conservatively.",),
        explanation=WorkoutExplanation(
            summary="Approved deterministic plan.",
            rationale=("Profile and safety constraints were applied.",),
            motivation="Build consistency safely.",
        ),
        generation_mode=mode,
        generated_at=NOW,
        activated_at=NOW,
        archived_at=None,
        version=1,
    )


def _session() -> WorkoutSessionResponse:
    return WorkoutSessionResponse(
        session_id="session-1",
        plan_id="plan-1",
        workout_day_id="day-1",
        day_number=1,
        status=SessionStatus.IN_PROGRESS,
        completion_percentage=0,
        completed_exercises=(),
        skipped_exercise_ids=(),
        adaptation_flags=(),
        planned_duration_minutes=45,
        actual_duration_minutes=None,
        started_at=NOW,
        completed_at=None,
        updated_at=NOW,
    )


def _service() -> Mock:
    service = Mock(spec=WorkoutService)
    service.generate_plan = AsyncMock(return_value=_plan())
    service.get_active_plan = AsyncMock(return_value=_plan())
    service.list_plans = AsyncMock(return_value=(_plan(),))
    service.get_plan = AsyncMock(return_value=_plan())
    service.activate_plan = AsyncMock(return_value=_plan())
    service.archive_plan = AsyncMock(return_value=None)
    service.record_session = AsyncMock(return_value=_session())
    service.list_sessions = AsyncMock(return_value=(_session(),))
    service.get_session = AsyncMock(return_value=_session())
    service.update_session = AsyncMock(return_value=_session())
    service.analyze_adaptation = AsyncMock(
        return_value=WorkoutAdaptationResponse(
            recommendation_code="maintain_plan",
            action=AdaptationAction.MAINTAIN_PLAN,
            reason_code="insufficient_history",
            severity=AdaptationSeverity.INFO,
            evidence_summary=("Not enough completed sessions for a change.",),
            automatic_application_allowed=False,
            affected_exercise_id=None,
            affected_day_number=None,
        )
    )
    return service


def _client(service: Mock, *, authenticated: bool = True) -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")

    if authenticated:
        app.dependency_overrides[get_current_user] = lambda: USER
    else:

        def reject() -> None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        app.dependency_overrides[get_current_user] = reject
    app.dependency_overrides[get_intelligent_workout_service] = lambda: cast(
        WorkoutService, service
    )
    return TestClient(app)


ENDPOINTS: tuple[tuple[str, str, dict[str, Any] | None], ...] = (
    ("POST", "/api/v1/intelligent-workouts/plans/generate", {}),
    ("GET", "/api/v1/intelligent-workouts/plans/active", None),
    ("GET", "/api/v1/intelligent-workouts/plans", None),
    ("GET", "/api/v1/intelligent-workouts/plans/plan-1", None),
    ("POST", "/api/v1/intelligent-workouts/plans/plan-1/activate", None),
    ("POST", "/api/v1/intelligent-workouts/plans/plan-1/archive", None),
    (
        "POST",
        "/api/v1/intelligent-workouts/sessions",
        {
            "plan_id": "plan-1",
            "day_number": 1,
            "status": "in_progress",
            "completed_exercises": [],
        },
    ),
    ("GET", "/api/v1/intelligent-workouts/sessions", None),
    ("GET", "/api/v1/intelligent-workouts/sessions/session-1", None),
    (
        "PATCH",
        "/api/v1/intelligent-workouts/sessions/session-1",
        {"notes": "Felt controlled."},
    ),
    ("POST", "/api/v1/intelligent-workouts/adaptation/analyze", {"plan_id": "plan-1"}),
)


@pytest.mark.parametrize(("method", "path", "body"), ENDPOINTS)
def test_every_intelligent_workout_endpoint_requires_authentication(
    method: str, path: str, body: dict[str, Any] | None
) -> None:
    response = _client(_service(), authenticated=False).request(method, path, json=body)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ("method", "path", "body", "expected_status"),
    tuple(
        (
            method,
            path,
            body,
            201 if method == "POST" and path.endswith(("generate", "sessions")) else 200,
        )
        for method, path, body in ENDPOINTS
    ),
)
def test_authenticated_api_surface_uses_safe_response_contracts(
    method: str,
    path: str,
    body: dict[str, Any] | None,
    expected_status: int,
) -> None:
    response = _client(_service()).request(method, path, json=body)
    assert response.status_code == expected_status, response.text
    assert "user_id" not in response.text
    assert "provider" not in response.text


def test_owner_scoped_missing_plan_is_indistinguishable_from_unknown_plan() -> None:
    service = _service()
    service.get_plan.side_effect = WorkoutPlanNotFoundError()
    response = _client(service).get("/api/v1/intelligent-workouts/plans/other-user-plan")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] == "workout_plan_not_found"


@pytest.mark.parametrize(
    "mode",
    (
        GenerationMode.DETERMINISTIC,
        GenerationMode.AI_ASSISTED,
        GenerationMode.DETERMINISTIC_FALLBACK,
    ),
)
def test_generation_modes_are_exposed_without_provider_metadata(mode: GenerationMode) -> None:
    service = _service()
    service.generate_plan.return_value = _plan(mode)
    response = _client(service).post(
        "/api/v1/intelligent-workouts/plans/generate",
        json={"use_ai_assistance": mode != GenerationMode.DETERMINISTIC},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["generation_mode"] == mode.value
    assert "provider" not in response.json()


def test_generation_failure_has_stable_service_unavailable_error() -> None:
    service = _service()
    service.generate_plan.side_effect = WorkoutGenerationError()
    response = _client(service).post("/api/v1/intelligent-workouts/plans/generate", json={})
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json()["detail"]["code"] == "workout_generation_failed"


def test_pagination_and_filters_are_forwarded_to_service() -> None:
    service = _service()
    response = _client(service).get(
        "/api/v1/intelligent-workouts/sessions?plan_id=plan-1&limit=10&offset=20"
    )
    assert response.status_code == status.HTTP_200_OK
    service.list_sessions.assert_awaited_once_with(USER, "plan-1", 11, 20)
    assert response.json()["limit"] == 10
    assert response.json()["offset"] == 20


@pytest.mark.parametrize(
    ("method", "path", "service_method", "error"),
    (
        (
            "GET",
            "/api/v1/intelligent-workouts/plans/foreign-plan",
            "get_plan",
            WorkoutPlanNotFoundError(),
        ),
        (
            "POST",
            "/api/v1/intelligent-workouts/plans/foreign-plan/activate",
            "activate_plan",
            WorkoutPlanNotFoundError(),
        ),
        (
            "POST",
            "/api/v1/intelligent-workouts/plans/foreign-plan/archive",
            "archive_plan",
            WorkoutPlanNotFoundError(),
        ),
        (
            "GET",
            "/api/v1/intelligent-workouts/sessions/foreign-session",
            "get_session",
            WorkoutSessionNotFoundError(),
        ),
    ),
)
def test_foreign_resources_use_the_same_not_found_contract(
    method: str, path: str, service_method: str, error: Exception
) -> None:
    service = _service()
    getattr(service, service_method).side_effect = error
    response = _client(service).request(method, path)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["code"] in {
        "workout_plan_not_found",
        "workout_session_not_found",
    }


@pytest.mark.parametrize(
    ("body", "path"),
    (
        ({"user_id": "other-user"}, "/api/v1/intelligent-workouts/plans/generate"),
        (
            {
                "owner_id": "other-user",
                "plan_id": "plan-1",
                "day_number": 1,
                "status": "in_progress",
                "completed_exercises": [],
            },
            "/api/v1/intelligent-workouts/sessions",
        ),
    ),
)
def test_client_supplied_ownership_fields_are_rejected(body: dict[str, Any], path: str) -> None:
    service = _service()
    response = _client(service).post(path, json=body)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    service.generate_plan.assert_not_awaited()
    service.record_session.assert_not_awaited()


@pytest.mark.parametrize(
    ("error", "expected_status", "expected_code"),
    (
        (WorkoutProfileIncompleteError(), 409, "workout_profile_incomplete"),
        (WorkoutHealthProfileIncompleteError(), 409, "workout_health_profile_incomplete"),
        (WorkoutReadinessBlockedError(), 403, "workout_readiness_blocked"),
        (
            WorkoutMedicalClearanceRequiredError(),
            403,
            "workout_medical_clearance_required",
        ),
        (WorkoutPlanArchivedError(), 409, "workout_plan_archived"),
        (WorkoutValidationError(("unsafe_plan",)), 422, "workout_validation_failed"),
        (WorkoutActivePlanConflictError(), 409, "workout_active_plan_conflict"),
    ),
)
def test_generation_and_lifecycle_errors_have_stable_mappings(
    error: Exception, expected_status: int, expected_code: str
) -> None:
    service = _service()
    service.generate_plan.side_effect = error
    response = _client(service).post("/api/v1/intelligent-workouts/plans/generate", json={})
    assert response.status_code == expected_status
    assert response.json()["detail"]["code"] == expected_code


def test_adaptation_endpoint_returns_recommendation_without_plan_mutation() -> None:
    service = _service()
    response = _client(service).post(
        "/api/v1/intelligent-workouts/adaptation/analyze", json={"plan_id": "plan-1"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["automatic_application_allowed"] is False
    service.analyze_adaptation.assert_awaited_once_with(USER, "plan-1")
    service.activate_plan.assert_not_awaited()
    service.archive_plan.assert_not_awaited()


def test_legacy_and_intelligent_workout_routes_are_both_registered() -> None:
    from app.api.router import router as application_router

    paths = {route.path for route in application_router.routes}
    assert "/workouts/current" in paths
    assert "/intelligent-workouts/plans/generate" in paths
