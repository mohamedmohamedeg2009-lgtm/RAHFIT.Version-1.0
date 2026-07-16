from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.core.exceptions import ErrorResponse
from app.health import (
    HealthProfileData,
    HealthProfileRepository,
    HealthProfileService,
    HealthProfileUpdateRequest,
)
from app.models.user import User
from app.profile import UserProfileData, UserProfileRepository, UserProfileService

router = APIRouter(tags=["User Intelligence"])


def get_user_profile_service(request: Request) -> UserProfileService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return UserProfileService(UserProfileRepository(database))


def get_health_profile_service(request: Request) -> HealthProfileService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return HealthProfileService(HealthProfileRepository(database))


@router.put(
    "/profile",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="user_intelligence_upsert_profile",
    summary="Create or update the authenticated user's canonical profile",
    description=(
        "Stores the strict profile required by readiness-gated intelligent features. "
        "Ownership is always derived from the bearer token."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is required."},
        422: {"model": ErrorResponse, "description": "Profile validation failed."},
    },
)
async def upsert_profile(
    body: UserProfileData,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
) -> Response:
    await service.save_profile(user.id, body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put(
    "/health-profile",
    status_code=status.HTTP_204_NO_CONTENT,
    operation_id="user_intelligence_upsert_health_profile",
    summary="Create or update the authenticated user's health declaration",
    description=(
        "Stores the explicit health declaration used by deterministic readiness and safety "
        "rules. Ownership is always derived from the bearer token."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is required."},
        422: {"model": ErrorResponse, "description": "Health declaration validation failed."},
    },
)
async def upsert_health_profile(
    body: HealthProfileUpdateRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[HealthProfileService, Depends(get_health_profile_service)],
) -> Response:
    await service.save_profile(user.id, HealthProfileData(**body.model_dump(), notes=None))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
