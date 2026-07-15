from typing import Annotated, Any, NoReturn, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.models.user import User
from app.repositories.assessments import AssessmentRepository
from app.schemas.assessment import (
    AssessmentResultResponse,
    AssessmentSessionResponse,
    QuestionResponse,
    SaveAnswerRequest,
    SaveAnswerResponse,
    StartAssessmentRequest,
    question_response,
    result_response,
    session_response,
)
from app.services.assessment import (
    AssessmentAnswerValidationError,
    AssessmentConflictError,
    AssessmentIncompleteError,
    AssessmentNotFoundError,
    AssessmentQuestionsUnavailableError,
    AssessmentSafetyStopError,
    AssessmentService,
    AssessmentStateError,
)

router = APIRouter(prefix="/assessments", tags=["Assessments"])


def get_assessment_service(request: Request) -> AssessmentService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return AssessmentService(AssessmentRepository(database))


def _api_error(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, object]] | None = None,
) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": details},
    )


def _translate_assessment_error(exc: Exception) -> NoReturn:
    if isinstance(exc, AssessmentNotFoundError):
        _api_error(
            status.HTTP_404_NOT_FOUND,
            "assessment_not_found",
            "The requested assessment is not available.",
        )
    if isinstance(exc, AssessmentQuestionsUnavailableError):
        _api_error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "assessment_questions_unavailable",
            "Assessment questions are temporarily unavailable.",
        )
    if isinstance(exc, AssessmentAnswerValidationError):
        _api_error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "assessment_answer_invalid",
            exc.message,
            [{"field": exc.question_id, "message": exc.message}],
        )
    if isinstance(exc, AssessmentIncompleteError):
        _api_error(
            status.HTTP_409_CONFLICT,
            "assessment_incomplete",
            "Complete the required assessment questions first.",
            [
                {"field": question_id, "message": "This question is required."}
                for question_id in exc.missing_question_ids
            ],
        )
    if isinstance(exc, AssessmentSafetyStopError):
        _api_error(
            status.HTTP_403_FORBIDDEN,
            "safety_restricted",
            "Assessment completion is restricted pending professional clearance.",
            [
                {
                    "status": exc.evaluation.status.value,
                    "risk_level": exc.evaluation.risk_level.value,
                    "explanations": list(exc.evaluation.explanations),
                }
            ],
        )
    if isinstance(exc, AssessmentStateError):
        _api_error(status.HTTP_409_CONFLICT, "assessment_state_invalid", str(exc))
    if isinstance(exc, AssessmentConflictError):
        _api_error(
            status.HTTP_409_CONFLICT,
            "assessment_conflict",
            "The assessment changed. Refresh and try again.",
        )
    raise exc


@router.get(
    "/questions",
    response_model=list[QuestionResponse],
    summary="Get the active assessment questions",
    description="Returns a versioned, ordered question catalogue for an authenticated user.",
)
async def get_questions(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
    version: Annotated[int | None, Query(ge=1)] = None,
) -> list[QuestionResponse]:
    del user
    try:
        questions = await service.get_questions(version)
    except Exception as exc:
        _translate_assessment_error(exc)
    return [QuestionResponse.model_validate(question) for question in questions]


@router.post(
    "/start",
    response_model=AssessmentSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start or resume an assessment session",
    responses={409: {"description": "Concurrent assessment conflict."}},
)
async def start_assessment(
    body: StartAssessmentRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssessmentSessionResponse:
    try:
        state = await service.start_assessment(user.id, body.version)
    except Exception as exc:
        _translate_assessment_error(exc)
    return session_response(state.session, state.progress, state.next_question)


@router.post(
    "/{session_id}/answer",
    response_model=SaveAnswerResponse,
    summary="Validate and save one assessment answer",
    responses={404: {"description": "Session not found."}, 409: {"description": "Conflict."}},
)
async def save_answer(
    session_id: str,
    body: SaveAnswerRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> SaveAnswerResponse:
    try:
        state = await service.save_answer(user.id, session_id, body.question_id, body.value)
    except Exception as exc:
        _translate_assessment_error(exc)
    return SaveAnswerResponse(
        session=session_response(state.session, state.progress),
        next_question=question_response(state.next_question),
    )


@router.post(
    "/{session_id}/finish",
    response_model=AssessmentResultResponse,
    summary="Validate and complete an assessment",
    responses={409: {"description": "Required answers are incomplete or state changed."}},
)
async def finish_assessment(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssessmentResultResponse:
    try:
        result = await service.finish_assessment(user.id, session_id)
    except Exception as exc:
        _translate_assessment_error(exc)
    return result_response(result)


@router.get(
    "/latest",
    response_model=AssessmentResultResponse,
    summary="Get the latest completed assessment",
    responses={404: {"description": "No completed assessment exists."}},
)
async def latest_assessment(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssessmentResultResponse:
    try:
        result = await service.get_latest_assessment(user.id)
    except Exception as exc:
        _translate_assessment_error(exc)
    return result_response(result)


@router.get(
    "/sessions/{session_id}",
    response_model=AssessmentSessionResponse,
    summary="Get an owned assessment session",
    responses={404: {"description": "Session not found."}},
)
async def get_session(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssessmentSessionResponse:
    try:
        state = await service.get_session(user.id, session_id)
    except Exception as exc:
        _translate_assessment_error(exc)
    return session_response(state.session, state.progress, state.next_question)


@router.post(
    "/sessions/{session_id}/resume",
    response_model=AssessmentSessionResponse,
    summary="Resume an owned in-progress assessment session",
)
async def resume_session(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AssessmentService, Depends(get_assessment_service)],
) -> AssessmentSessionResponse:
    try:
        state = await service.resume_assessment(user.id, session_id)
    except Exception as exc:
        _translate_assessment_error(exc)
    return session_response(state.session, state.progress, state.next_question)
