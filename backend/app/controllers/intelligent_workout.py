from typing import Annotated, Any, NoReturn, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.resolver import AIProviderResolver
from app.ai.service import AIService
from app.config import Settings, get_settings
from app.context import UserIntelligenceContextBuilder
from app.controllers.auth import get_current_user
from app.health import HealthProfileRepository
from app.models.user import User
from app.profile import UserProfileRepository
from app.readiness import ReadinessChecker
from app.services.ai_safety import AISafetyEngine
from app.users.service import UserIntelligenceService
from app.workouts.exceptions import (
    WorkoutActivePlanConflictError,
    WorkoutError,
    WorkoutExerciseUnavailableError,
    WorkoutGenerationError,
    WorkoutHealthProfileIncompleteError,
    WorkoutMedicalClearanceRequiredError,
    WorkoutPersistenceError,
    WorkoutPlanArchivedError,
    WorkoutPlanNotFoundError,
    WorkoutProfileIncompleteError,
    WorkoutReadinessBlockedError,
    WorkoutSessionNotFoundError,
    WorkoutSessionStateError,
    WorkoutValidationError,
)
from app.workouts.exercises import ExerciseCatalog, ExerciseSelector
from app.workouts.generator import WorkoutGenerator
from app.workouts.planner import WorkoutPlanner
from app.workouts.repository import MongoWorkoutRepository
from app.workouts.schemas import (
    RecordWorkoutSessionRequest,
    UpdateWorkoutSessionRequest,
    WorkoutAdaptationRequest,
    WorkoutAdaptationResponse,
    WorkoutArchiveResponse,
    WorkoutGenerationRequest,
    WorkoutPlanListResponse,
    WorkoutPlanResponse,
    WorkoutSessionListResponse,
    WorkoutSessionResponse,
)
from app.workouts.service import WorkoutService
from app.workouts.validator import WorkoutValidator

RESOURCE_ID_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
DEFAULT_PAGE_SIZE = 20
MAXIMUM_PAGE_SIZE = 100

router = APIRouter(prefix="/intelligent-workouts", tags=["Intelligent Workouts"])


def get_intelligent_workout_service(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> WorkoutService:
    """Composition root for the new workout boundary; no provider request occurs here."""
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    intelligence = UserIntelligenceService(
        UserProfileRepository(database),
        HealthProfileRepository(database),
    )
    readiness = ReadinessChecker()
    resolution = AIProviderResolver(settings).resolve()
    ai_service = (
        AIService(
            provider=resolution.provider,
            context_builder=UserIntelligenceContextBuilder(intelligence, readiness),
            safety_engine=AISafetyEngine(),
        )
        if resolution.provider is not None
        else None
    )
    generator = WorkoutGenerator(
        intelligence=intelligence,
        readiness=readiness,
        planner=WorkoutPlanner(),
        catalog=ExerciseCatalog(),
        selector=ExerciseSelector(),
        validator=WorkoutValidator(),
        ai_service=ai_service,
    )
    return WorkoutService(
        MongoWorkoutRepository(database),
        generator,
        intelligence=intelligence,
        readiness=readiness,
    )


def _error(status_code: int, code: str, message: str) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": []},
    )


def _translate(exc: WorkoutError) -> NoReturn:
    if isinstance(exc, WorkoutPlanNotFoundError | WorkoutSessionNotFoundError):
        _error(status.HTTP_404_NOT_FOUND, exc.reason_code, "The workout resource is not available.")
    if isinstance(exc, WorkoutProfileIncompleteError | WorkoutHealthProfileIncompleteError):
        _error(
            status.HTTP_409_CONFLICT,
            exc.reason_code,
            "Complete the required profile and health information first.",
        )
    if isinstance(exc, WorkoutMedicalClearanceRequiredError):
        _error(
            status.HTTP_403_FORBIDDEN,
            exc.reason_code,
            "Professional clearance is required before workout generation.",
        )
    if isinstance(exc, WorkoutReadinessBlockedError):
        _error(
            status.HTTP_403_FORBIDDEN,
            exc.reason_code,
            "Workout generation is unavailable under the current readiness state.",
        )
    if isinstance(exc, WorkoutExerciseUnavailableError | WorkoutValidationError):
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            exc.reason_code,
            "The workout request cannot satisfy the approved safety constraints.",
        )
    if isinstance(
        exc,
        WorkoutPlanArchivedError | WorkoutSessionStateError | WorkoutActivePlanConflictError,
    ):
        _error(
            status.HTTP_409_CONFLICT,
            exc.reason_code,
            "The requested workout lifecycle transition is not allowed.",
        )
    if isinstance(exc, WorkoutPersistenceError | WorkoutGenerationError):
        _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            exc.reason_code,
            "The workout operation could not be completed safely.",
        )
    _error(status.HTTP_500_INTERNAL_SERVER_ERROR, "workout_error", "The workout operation failed.")


@router.post(
    "/plans/generate",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate and activate an intelligent workout plan",
)
async def generate_plan(
    body: WorkoutGenerationRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutPlanResponse:
    try:
        return await service.generate_plan(user, body)
    except WorkoutError as exc:
        _translate(exc)


@router.get("/plans/active", response_model=WorkoutPlanResponse, summary="Get active plan")
async def get_active_plan(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutPlanResponse:
    try:
        return await service.get_active_plan(user)
    except WorkoutError as exc:
        _translate(exc)


@router.get("/plans", response_model=WorkoutPlanListResponse, summary="List owned plans")
async def list_plans(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
    limit: Annotated[int, Query(ge=1, le=MAXIMUM_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
) -> WorkoutPlanListResponse:
    items = await service.list_plans(user, limit + 1, offset)
    return WorkoutPlanListResponse(
        items=items[:limit],
        limit=limit,
        offset=offset,
        has_more=len(items) > limit,
    )


@router.get("/plans/{plan_id}", response_model=WorkoutPlanResponse, summary="Get owned plan")
async def get_plan(
    plan_id: Annotated[str, Path(pattern=RESOURCE_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutPlanResponse:
    try:
        return await service.get_plan(user, plan_id)
    except WorkoutError as exc:
        _translate(exc)


@router.post(
    "/plans/{plan_id}/activate",
    response_model=WorkoutPlanResponse,
    summary="Activate an owned plan",
)
async def activate_plan(
    plan_id: Annotated[str, Path(pattern=RESOURCE_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutPlanResponse:
    try:
        return await service.activate_plan(user, plan_id)
    except WorkoutError as exc:
        _translate(exc)


@router.post(
    "/plans/{plan_id}/archive",
    response_model=WorkoutArchiveResponse,
    summary="Archive an owned active plan",
)
async def archive_plan(
    plan_id: Annotated[str, Path(pattern=RESOURCE_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutArchiveResponse:
    try:
        await service.archive_plan(user, plan_id)
    except WorkoutError as exc:
        _translate(exc)
    return WorkoutArchiveResponse(plan_id=plan_id)


@router.post(
    "/sessions",
    response_model=WorkoutSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start or record an owned workout session",
)
async def create_session(
    body: RecordWorkoutSessionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutSessionResponse:
    try:
        return await service.record_session(user, body)
    except WorkoutError as exc:
        _translate(exc)


@router.get("/sessions", response_model=WorkoutSessionListResponse, summary="List sessions")
async def list_sessions(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
    plan_id: Annotated[str | None, Query(pattern=RESOURCE_ID_PATTERN)] = None,
    limit: Annotated[int, Query(ge=1, le=MAXIMUM_PAGE_SIZE)] = DEFAULT_PAGE_SIZE,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
) -> WorkoutSessionListResponse:
    items = await service.list_sessions(user, plan_id, limit + 1, offset)
    return WorkoutSessionListResponse(
        items=items[:limit],
        limit=limit,
        offset=offset,
        has_more=len(items) > limit,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=WorkoutSessionResponse,
    summary="Get owned session",
)
async def get_session(
    session_id: Annotated[str, Path(pattern=RESOURCE_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutSessionResponse:
    try:
        return await service.get_session(user, session_id)
    except WorkoutError as exc:
        _translate(exc)


@router.patch(
    "/sessions/{session_id}",
    response_model=WorkoutSessionResponse,
    summary="Update owned in-progress session",
)
async def update_session(
    session_id: Annotated[str, Path(pattern=RESOURCE_ID_PATTERN)],
    body: UpdateWorkoutSessionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutSessionResponse:
    try:
        return await service.update_session(user, session_id, body)
    except WorkoutError as exc:
        _translate(exc)


@router.post(
    "/adaptation/analyze",
    response_model=WorkoutAdaptationResponse,
    summary="Analyze safe deterministic plan adaptation",
)
async def analyze_adaptation(
    body: WorkoutAdaptationRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_intelligent_workout_service)],
) -> WorkoutAdaptationResponse:
    try:
        return await service.analyze_adaptation(user, body.plan_id)
    except WorkoutError as exc:
        _translate(exc)
