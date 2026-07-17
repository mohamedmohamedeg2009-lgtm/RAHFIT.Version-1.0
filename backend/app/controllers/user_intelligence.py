from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.core.exceptions import ErrorResponse
from app.health import (
    HealthProfileData,
    HealthProfileNotFoundError,
    HealthProfileReadResponse,
    HealthProfileRepository,
    HealthProfileService,
    HealthProfileUpdateRequest,
)
from app.models.user import User
from app.profile import (
    UserProfileData,
    UserProfileNotFoundError,
    UserProfileReadResponse,
    UserProfileRepository,
    UserProfileService,
)

router = APIRouter(tags=["User Intelligence"])


def get_user_profile_service(request: Request) -> UserProfileService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return UserProfileService(UserProfileRepository(database))


def get_health_profile_service(request: Request) -> HealthProfileService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return HealthProfileService(HealthProfileRepository(database))


@router.get(
    "/user-intelligence/profile",
    response_model=UserProfileReadResponse,
    operation_id="user_intelligence_get_profile",
    summary="Get the authenticated user's canonical profile",
    description=(
        "Returns the client-safe profile owned by the bearer token. Persistence and ownership "
        "metadata are never exposed."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is required."},
        404: {"model": ErrorResponse, "description": "No profile has been saved."},
    },
)
async def get_profile(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserProfileService, Depends(get_user_profile_service)],
) -> UserProfileReadResponse:
    try:
        profile = await service.get_profile(user.id)
    except UserProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "user_profile_not_found", "message": "No profile has been saved."},
        ) from exc
    return UserProfileReadResponse.from_domain(profile)


@router.get(
    "/user-intelligence/health",
    response_model=HealthProfileReadResponse,
    operation_id="user_intelligence_get_health",
    summary="Get the authenticated user's health declaration",
    description=(
        "Returns the client-safe health declaration owned by the bearer token. Private notes, "
        "persistence metadata, and ownership fields are never exposed."
    ),
    responses={
        401: {"model": ErrorResponse, "description": "Authentication is required."},
        404: {"model": ErrorResponse, "description": "No health declaration has been saved."},
    },
)
async def get_health_profile(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[HealthProfileService, Depends(get_health_profile_service)],
) -> HealthProfileReadResponse:
    try:
        profile = await service.get_profile(user.id)
    except HealthProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "health_profile_not_found",
                "message": "No health declaration has been saved.",
            },
        ) from exc
    return HealthProfileReadResponse.from_domain(profile)


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
