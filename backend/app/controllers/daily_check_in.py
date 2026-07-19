from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.models.user import User
from app.repositories.daily_check_in import MongoDailyCheckInRepository
from app.schemas.daily_check_in import (
    DailyCheckInCreate,
    DailyCheckInHistoryResponse,
    DailyCheckInResponse,
)
from app.services.daily_check_in import DailyCheckInService
from app.services.daily_check_in_engine import DailyCheckInEngine, DailyCheckInEngineError

router = APIRouter(prefix="/check-ins/daily", tags=["Daily Check-in"])


def get_daily_check_in_service(request: Request) -> DailyCheckInService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    repository = MongoDailyCheckInRepository(database)
    return DailyCheckInService(repository, DailyCheckInEngine())


@router.post(
    "",
    response_model=DailyCheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit or update daily readiness check-in",
    description="Calculates deterministic readiness scores and persists owner-scoped daily record.",
)
async def submit_daily_check_in(
    payload: DailyCheckInCreate,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DailyCheckInService, Depends(get_daily_check_in_service)],
) -> DailyCheckInResponse:
    try:
        check_in = await service.submit_check_in(user.id, payload)
        return DailyCheckInResponse(check_in=check_in)
    except DailyCheckInEngineError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "invalid_check_in_input",
                "message": str(exc),
            },
        ) from exc


@router.get(
    "/today",
    response_model=DailyCheckInResponse,
    status_code=status.HTTP_200_OK,
    summary="Get today's daily readiness check-in",
    description="Returns the authenticated user's check-in for today if present.",
)
async def get_today_check_in(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DailyCheckInService, Depends(get_daily_check_in_service)],
) -> DailyCheckInResponse:
    check_in = await service.get_today_check_in(user.id)
    if not check_in:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "check_in_not_found",
                "message": "No daily check-in found for today.",
            },
        )
    return DailyCheckInResponse(check_in=check_in)


@router.get(
    "/history",
    response_model=DailyCheckInHistoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get paginated daily check-in history",
    description="Returns owner-scoped historical daily check-ins ordered newest first.",
)
async def get_check_in_history(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DailyCheckInService, Depends(get_daily_check_in_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DailyCheckInHistoryResponse:
    items, total = await service.list_history(user.id, limit=limit, offset=offset)
    has_more = (offset + len(items)) < total
    return DailyCheckInHistoryResponse(
        items=tuple(items),
        total=total,
        limit=limit,
        offset=offset,
        has_more=has_more,
    )
