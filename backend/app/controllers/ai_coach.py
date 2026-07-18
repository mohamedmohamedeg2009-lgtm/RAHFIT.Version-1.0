from typing import Annotated, Any, NoReturn, cast
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS
from app.ai.resolver import AIProviderResolver
from app.ai.schemas import AIServiceRequest
from app.ai.service import AIService
from app.config import Settings, get_settings
from app.context import UserIntelligenceContextBuilder
from app.controllers.auth import get_current_user
from app.health import HealthProfileRepository
from app.models.ai_context import AIContextPurpose, AIContextRequest
from app.models.ai_conversation import (
    CONVERSATION_ID_PATTERN,
    AIConversation,
    AIConversationStatus,
    AIMessage,
)
from app.models.ai_policy import (
    AIAction,
    AICapability,
    AIForbiddenAction,
    AIPolicyDecision,
)
from app.models.user import User
from app.profile import UserProfileRepository
from app.readiness import ReadinessChecker
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
from app.services.ai_classifier import CapabilityClassifier
from app.services.ai_conversation import (
    AIConversationLimitError,
    AIConversationNotFoundError,
    AIConversationService,
    AIConversationStateError,
    AIConversationValidationError,
)
from app.services.ai_policy import AIPolicyService
from app.services.ai_safety import AISafetyEngine
from app.users.service import UserIntelligenceService

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


def get_ai_service(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIService | None:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    resolution = AIProviderResolver(settings).resolve()
    if resolution.provider is None:
        return None
    intelligence = UserIntelligenceService(
        UserProfileRepository(database),
        HealthProfileRepository(database),
    )
    return AIService(
        provider=resolution.provider,
        context_builder=UserIntelligenceContextBuilder(intelligence, ReadinessChecker()),
        safety_engine=AISafetyEngine(),
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


# Intentionally not decorated: Phase A keeps free-form generation internal only.
async def send_ai_conversation_message(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    body: Any,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
    ai_service: Annotated[Any, Depends(get_ai_service)],
) -> AIMessageResponse:
    try:
        detail = await service.get_conversation(user.id, conversation_id)
    except Exception as exc:
        _translate_conversation_error(exc)

    if detail.conversation.status != AIConversationStatus.ACTIVE:
        _error(
            status.HTTP_400_BAD_REQUEST,
            "ai_conversation_closed",
            "Cannot send messages to a closed or deleted conversation.",
        )

    try:
        classification = CapabilityClassifier().classify(body.content)
    except Exception as exc:
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "ai_classification_failed",
            str(exc),
        )

    capability = classification.capability
    if isinstance(capability, AICapability):
        policy_actions = {
            AICapability.EXPLAIN_ASSESSMENT: AIAction.EXPLAIN,
            AICapability.EXPLAIN_WORKOUT: AIAction.EXPLAIN,
            AICapability.EXPLAIN_NUTRITION: AIAction.EXPLAIN,
            AICapability.EXPLAIN_PROGRESS: AIAction.EXPLAIN,
            AICapability.MOTIVATE: AIAction.ENCOURAGE,
            AICapability.SUMMARIZE: AIAction.SUMMARIZE,
            AICapability.SUGGEST_WORKOUT_ALTERNATIVE: AIAction.RECOMMEND,
            AICapability.SUGGEST_NUTRITION_ALTERNATIVE: AIAction.RECOMMEND,
        }
        action = policy_actions.get(capability, AIAction.EXPLAIN)
        policy = AIPolicyService().evaluate(capability, action)

        if capability in {
            AICapability.EXPLAIN_NUTRITION,
            AICapability.SUGGEST_NUTRITION_ALTERNATIVE,
        }:
            purpose = AIContextPurpose.GENERAL_NUTRITION_QUESTION
        elif capability == AICapability.MOTIVATE:
            purpose = AIContextPurpose.SAFE_MOTIVATION
        else:
            purpose = AIContextPurpose.GENERAL_FITNESS_QUESTION
    else:
        policy = AIPolicyService().evaluate(
            AICapability.EXPLAIN_ASSESSMENT,
            AIForbiddenAction.DIAGNOSE_MEDICAL_CONDITION,
        )
        purpose = AIContextPurpose.GENERAL_FITNESS_QUESTION

    if policy.decision in {AIPolicyDecision.DENY, AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED}:
        _error(
            status.HTTP_400_BAD_REQUEST,
            "ai_policy_refusal",
            "This request cannot be handled by AI coaching. Please seek appropriate professional guidance.",
        )

    if ai_service is None:
        _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "ai_provider_unavailable",
            "AI coaching features are not configured on this server.",
        )

    from app.ai.prompts.ai_coach import build_ai_coach_system_instructions

    system_instructions = build_ai_coach_system_instructions()

    request = AIServiceRequest(
        prompt=body.content,
        system_instructions=system_instructions,
        context_request=AIContextRequest(
            purpose=purpose,
            current_user_question=body.content,
            conversation_id=conversation_id,
            include_conversation_context=True,
        ),
        classification=classification,
        policy=policy,
        request_id=uuid4().hex,
        locale="en",
    )

    try:
        provider_request, safety = await ai_service.prepare_text(user, request)
    except Exception as exc:
        _translate_conversation_error(exc)

    try:
        await service.append_user_message(user.id, conversation_id, body.content)
    except Exception as exc:
        _translate_conversation_error(exc)

    try:
        ai_response = await ai_service.generate_prepared_text(request, provider_request, safety)
    except Exception as exc:
        _translate_conversation_error(exc)

    try:
        stored_assistant = await service.append_assistant_message(
            user.id, conversation_id, ai_response.output.text
        )
    except Exception as exc:
        _translate_conversation_error(exc)

    return _message(stored_assistant)


# Kept as an internal helper only until Phase B defines the public message contract.
async def get_ai_conversation_messages(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
) -> list[AIMessageResponse]:
    try:
        detail = await service.get_conversation(user.id, conversation_id)
    except Exception as exc:
        _translate_conversation_error(exc)
    return [_message(item) for item in detail.messages]
