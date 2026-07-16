from typing import Annotated, Any, NoReturn, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.assessment import get_assessment_service
from app.controllers.auth import get_current_user
from app.models.user import User
from app.models.workout import WorkoutPlan, WorkoutSession
from app.repositories.workouts import WorkoutRepository
from app.schemas.workout import (
    CurrentWorkoutResponse,
    GenerateWorkoutRequest,
    UpdateExerciseRequest,
    WorkoutHistoryResponse,
)
from app.services.assessment import AssessmentService
from app.services.workout import (
    WorkoutAssessmentRequiredError,
    WorkoutNotFoundError,
    WorkoutSafetyRestrictedError,
    WorkoutService,
    WorkoutStateError,
)
from app.services.workout_generator import WorkoutGenerationError

router = APIRouter(prefix="/workouts", tags=["Workouts"])


def get_workout_service(
    request: Request,
    assessment: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> WorkoutService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return WorkoutService(WorkoutRepository(database), assessment)


def _error(status_code: int, code: str, message: str) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": []},
    )


def _translate(exc: Exception) -> NoReturn:
    if isinstance(exc, WorkoutNotFoundError):
        _error(status.HTTP_404_NOT_FOUND, "workout_not_found", "The workout is not available.")
    if isinstance(exc, WorkoutAssessmentRequiredError):
        _error(
            status.HTTP_409_CONFLICT,
            "assessment_required",
            "Complete the smart assessment before generating a workout.",
        )
    if isinstance(exc, WorkoutSafetyRestrictedError):
        _error(
            status.HTTP_403_FORBIDDEN,
            "workout_safety_restricted",
            "Workout generation is paused pending professional clearance.",
        )
    if isinstance(exc, WorkoutStateError | WorkoutGenerationError):
        _error(status.HTTP_409_CONFLICT, "workout_state_invalid", str(exc))
    raise exc


@router.get("/current", response_model=CurrentWorkoutResponse, summary="Get current workout")
async def current_workout(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> CurrentWorkoutResponse:
    try:
        state = await service.get_current(user.id)
    except Exception as exc:
        _translate(exc)
    return CurrentWorkoutResponse(plan=state.plan, today=state.today, session=state.session)


@router.post(
    "/generate",
    response_model=WorkoutPlan,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a deterministic workout plan",
)
async def generate_workout(
    body: GenerateWorkoutRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutPlan:
    try:
        return await service.generate_plan(
            user.id, body.available_days, body.session_duration_minutes
        )
    except Exception as exc:
        _translate(exc)


@router.get("/history", response_model=WorkoutHistoryResponse, summary="Get workout history")
async def workout_history(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutHistoryResponse:
    history = await service.get_history(user.id)
    return WorkoutHistoryResponse(
        plans=history.plans,
        completed_sessions=history.completed_sessions,
        weekly_adherence_percentage=history.weekly_adherence_percentage,
    )


@router.get("/{plan_id}", response_model=WorkoutPlan, summary="Get workout details")
async def workout_details(
    plan_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutPlan:
    try:
        return await service.get_plan(user.id, plan_id)
    except Exception as exc:
        _translate(exc)


@router.post(
    "/{plan_id}/days/{day_id}/sessions/start",
    response_model=WorkoutSession,
    status_code=status.HTTP_201_CREATED,
    summary="Start or resume a workout session",
)
async def start_session(
    plan_id: str,
    day_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutSession:
    try:
        return await service.start_session(user.id, plan_id, day_id)
    except Exception as exc:
        _translate(exc)


@router.patch(
    "/sessions/{session_id}/exercises/{exercise_id}",
    response_model=WorkoutSession,
    summary="Record exercise completion or skip state",
)
async def update_exercise(
    session_id: str,
    exercise_id: str,
    body: UpdateExerciseRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutSession:
    try:
        return await service.update_exercise(
            user.id, session_id, exercise_id, body.completed_sets, body.skipped
        )
    except Exception as exc:
        _translate(exc)


@router.post(
    "/sessions/{session_id}/complete",
    response_model=WorkoutSession,
    summary="Complete a workout session",
)
async def complete_session(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[WorkoutService, Depends(get_workout_service)],
) -> WorkoutSession:
    try:
        return await service.complete_session(user.id, session_id)
    except Exception as exc:
        _translate(exc)
