from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import Settings, get_settings
from app.models.user import User
from app.repositories.users import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LogoutResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenPairResponse,
    UserResponse,
)
from app.security.jwt import TokenPayload, TokenValidationError, decode_token
from app.services.auth import (
    AuthenticationError,
    AuthResult,
    AuthService,
    EmailAlreadyRegisteredError,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
_bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(
    request: Request, settings: Annotated[Settings, Depends(get_settings)]
) -> AuthService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return AuthService(UserRepository(database["users"]), settings)


def _authentication_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication credentials are invalid or expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPayload:
    if not credentials:
        raise _authentication_exception()
    try:
        return decode_token(credentials.credentials, settings)
    except TokenValidationError as exc:
        raise _authentication_exception() from exc


async def get_current_user(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    try:
        return await service.get_current_user(payload)
    except AuthenticationError as exc:
        raise _authentication_exception() from exc


def _token_response(result: AuthResult, settings: Settings) -> TokenPairResponse:
    return TokenPairResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        access_token_expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
    responses={409: {"description": "An account already exists for this email."}},
)
async def register(
    body: RegisterRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPairResponse:
    try:
        result = await service.register(body.email, body.password)
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account already exists for this email."
        ) from exc
    return _token_response(result, settings)


@router.post(
    "/login",
    response_model=TokenPairResponse,
    summary="Create an authenticated session",
    responses={401: {"description": "Invalid sign-in details."}},
)
async def login(
    body: LoginRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPairResponse:
    try:
        result = await service.login(body.email, body.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The sign-in details are not valid.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    return _token_response(result, settings)


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    summary="Refresh an authenticated session",
)
async def refresh(
    body: RefreshTokenRequest,
    service: Annotated[AuthService, Depends(get_auth_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TokenPairResponse:
    try:
        payload = decode_token(body.refresh_token, service.settings)
        result = await service.refresh(payload)
    except (AuthenticationError, TokenValidationError) as exc:
        raise _authentication_exception() from exc
    return _token_response(result, service.settings)


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
async def current_user(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Invalidate the current user session tokens",
)
async def logout(
    payload: Annotated[TokenPayload, Depends(get_token_payload)],
    service: Annotated[AuthService, Depends(get_auth_service)],
) -> LogoutResponse:
    try:
        await service.logout(payload)
    except AuthenticationError as exc:
        raise _authentication_exception() from exc
    return LogoutResponse()
