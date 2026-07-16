from typing import Annotated, Any, NoReturn, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS
from app.config import Settings, get_settings
from app.controllers.auth import get_current_user
from app.models.ai_conversation import CONVERSATION_ID_PATTERN, AIConversation, AIMessage
from app.models.user import User
from app.repositories.ai_conversations import AIConversationRepository, AIMessageRepository
from app.schemas.ai_conversation import (
    AIConversationDetailResponse,
    AIConversationListResponse,
    AIConversationSummaryResponse,
    AIMessageResponse,
    CreateAIConversationRequest,
)
from app.schemas.ai_provider import AIAvailabilityResponse
from app.services.ai_availability import AIAvailabilityService
from app.services.ai_conversation import (
    AIConversationLimitError,
    AIConversationNotFoundError,
    AIConversationService,
    AIConversationStateError,
    AIConversationValidationError,
)

router = APIRouter(prefix="/ai-coach", tags=["AI Provider Infrastructure"])


def get_ai_availability_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIAvailabilityService:
    return AIAvailabilityService(settings)


def get_ai_conversation_service(request: Request) -> AIConversationService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return AIConversationService(
        AIConversationRepository(database),
        AIMessageRepository(database),
    )


def _error(status_code: int, code: str, message: str) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail={"code": code, "message": message, "details": []},
    )


def _translate_conversation_error(exc: Exception) -> NoReturn:
    if isinstance(exc, AIConversationNotFoundError):
        _error(
            status.HTTP_404_NOT_FOUND,
            "ai_conversation_not_found",
            "The conversation is not available.",
        )
    if isinstance(exc, AIConversationValidationError):
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "ai_conversation_validation_error",
            str(exc),
        )
    if isinstance(exc, AIConversationLimitError):
        _error(
            status.HTTP_409_CONFLICT,
            "ai_conversation_limit_reached",
            str(exc),
        )
    if isinstance(exc, AIConversationStateError):
        _error(
            status.HTTP_409_CONFLICT,
            "ai_conversation_state_invalid",
            str(exc),
        )
    raise exc


def _summary(conversation: AIConversation) -> AIConversationSummaryResponse:
    return AIConversationSummaryResponse(
        id=conversation.id,
        title=conversation.title,
        status=conversation.status,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_activity_at=conversation.last_activity_at,
        closed_at=conversation.closed_at,
        last_message_at=conversation.last_message_at,
        message_count=conversation.message_count,
        schema_version=conversation.schema_version,
    )


def _message(message: AIMessage) -> AIMessageResponse:
    return AIMessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        role=message.role,
        content=message.content,
        source=message.source,
        created_at=message.created_at,
        schema_version=message.schema_version,
    )


@router.get(
    "/availability",
    response_model=AIAvailabilityResponse,
    summary="Get configured AI provider availability",
    description=(
        "Returns a secret-free local configuration state. This endpoint never calls the provider."
    ),
)
async def get_ai_availability(
    _user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIAvailabilityService, Depends(get_ai_availability_service)],
) -> AIAvailabilityResponse:
    availability = await service.get_availability()
    return AIAvailabilityResponse.model_validate(availability.model_dump())


@router.post(
    "/conversations",
    response_model=AIConversationSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an AI Coach conversation",
    description="Creates local conversation storage without calling an AI provider.",
)
async def create_ai_conversation(
    body: CreateAIConversationRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
) -> AIConversationSummaryResponse:
    try:
        conversation = await service.create_conversation(user.id, body.title)
    except Exception as exc:
        _translate_conversation_error(exc)
    return _summary(conversation)


@router.get(
    "/conversations",
    response_model=AIConversationListResponse,
    summary="List owned AI Coach conversations",
)
async def list_ai_conversations(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
    limit: Annotated[
        int,
        Query(ge=1, le=AI_CONVERSATION_LIMITS.maximum_page_size),
    ] = AI_CONVERSATION_LIMITS.default_page_size,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
) -> AIConversationListResponse:
    try:
        result = await service.list_conversations(user.id, limit, offset)
    except Exception as exc:
        _translate_conversation_error(exc)
    return AIConversationListResponse(
        items=tuple(_summary(item) for item in result.items),
        limit=result.limit,
        offset=result.offset,
        has_more=result.has_more,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=AIConversationDetailResponse,
    summary="Get an owned AI Coach conversation",
)
async def get_ai_conversation(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
) -> AIConversationDetailResponse:
    try:
        detail = await service.get_conversation(user.id, conversation_id)
    except Exception as exc:
        _translate_conversation_error(exc)
    summary = _summary(detail.conversation)
    return AIConversationDetailResponse(
        **summary.model_dump(),
        messages=tuple(_message(item) for item in detail.messages),
        message_history_limit=detail.message_history_limit,
        messages_truncated=detail.messages_truncated,
    )


@router.post(
    "/conversations/{conversation_id}/close",
    response_model=AIConversationSummaryResponse,
    summary="Close an owned AI Coach conversation",
)
async def close_ai_conversation(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
) -> AIConversationSummaryResponse:
    try:
        conversation = await service.close_conversation(user.id, conversation_id)
    except Exception as exc:
        _translate_conversation_error(exc)
    return _summary(conversation)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an owned AI Coach conversation",
)
async def delete_ai_conversation(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
) -> Response:
    await service.delete_conversation(user.id, conversation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
