from typing import Annotated, Any, NoReturn, cast
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.ai.conversation_limits import AI_CONVERSATION_LIMITS
from app.ai.exceptions import AIProviderError, AISafetyError, AITimeoutError
from app.ai.prompts.ai_coach import build_ai_coach_system_instructions
from app.ai.resolver import AIProviderResolver
from app.ai.schemas import AIServiceRequest
from app.ai.service import AIService
from app.config import Settings, get_settings
from app.context import UserIntelligenceContextBuilder
from app.controllers.auth import get_current_user
from app.health import HealthProfileRepository
from app.models.ai_classifier import AIClassifierSpecialCapability
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
    AICoachMessageResponse,
    AIConversationDetailResponse,
    AIConversationListResponse,
    AIConversationSummaryResponse,
    AIMessageResponse,
    CreateAIConversationRequest,
    SendAIMessageRequest,
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
    from app.repositories.daily_check_in import MongoDailyCheckInRepository

    return AIService(
        provider=resolution.provider,
        context_builder=UserIntelligenceContextBuilder(intelligence, ReadinessChecker()),
        safety_engine=AISafetyEngine(),
        daily_check_in_repository=MongoDailyCheckInRepository(database),
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


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=AICoachMessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message to an owned AI Coach conversation",
)
async def send_ai_conversation_message(
    conversation_id: Annotated[str, Path(pattern=CONVERSATION_ID_PATTERN)],
    body: SendAIMessageRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIConversationService, Depends(get_ai_conversation_service)],
    ai_service: Annotated[AIService | None, Depends(get_ai_service)],
) -> AICoachMessageResponse:
    try:
        detail = await service.get_conversation(user.id, conversation_id)
    except Exception as exc:
        _translate_conversation_error(exc)

    if detail.conversation.status == AIConversationStatus.CLOSED:
        _error(
            status.HTTP_409_CONFLICT,
            "ai_conversation_closed",
            "Cannot send messages to a closed conversation.",
        )
    if detail.conversation.status == AIConversationStatus.DELETED:
        _error(
            status.HTTP_404_NOT_FOUND,
            "ai_conversation_not_found",
            "The conversation is not available.",
        )

    raw_content = body.content.strip()
    if not raw_content:
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "ai_message_empty",
            "Message content cannot be empty.",
        )

    if len(raw_content) > AI_CONVERSATION_LIMITS.maximum_message_length:
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "ai_message_too_long",
            f"Message exceeds maximum allowed length of {AI_CONVERSATION_LIMITS.maximum_message_length} characters.",
        )

    lowered = raw_content.lower()
    if "<script" in lowered or "<iframe" in lowered:
        _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "ai_message_invalid",
            "Unsafe HTML content is not permitted.",
        )

    classification = CapabilityClassifier().classify(raw_content)
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
        if capability == AIClassifierSpecialCapability.MEDICAL_RELATED:
            policy = AIPolicyService().evaluate(
                AICapability.EXPLAIN_ASSESSMENT,
                AIForbiddenAction.DIAGNOSE_MEDICAL_CONDITION,
            )
        else:
            policy = AIPolicyService().evaluate(
                AICapability.EXPLAIN_ASSESSMENT,
                AIForbiddenAction.EXECUTE_CODE,
            )
        purpose = AIContextPurpose.GENERAL_FITNESS_QUESTION

    capability_str = str(capability.value if hasattr(capability, "value") else capability)

    if policy.decision == AIPolicyDecision.DENY:
        user_msg = await service.append_user_message(user.id, conversation_id, raw_content)
        refusal_text = "This request cannot be fulfilled as it falls outside allowed Rahafit coaching boundaries."
        asst_msg = await service.append_assistant_message(user.id, conversation_id, refusal_text)
        return AICoachMessageResponse(
            conversation_id=conversation_id,
            user_message=_message(user_msg),
            assistant_message=_message(asst_msg),
            capability=capability_str,
            safety_decision="refuse",
            safe_reason_code=policy.reason_code.value,
            provider_used=None,
            created_at=asst_msg.created_at,
        )

    if policy.decision == AIPolicyDecision.PROFESSIONAL_GUIDANCE_REQUIRED:
        user_msg = await service.append_user_message(user.id, conversation_id, raw_content)
        guidance_text = (
            "Your safety is our priority. Rahafit provides fitness and wellness guidance but does not provide medical advice, diagnosis, or treatment. "
            "Please consult a qualified medical professional or healthcare provider for guidance on medical concerns or symptoms."
        )
        asst_msg = await service.append_assistant_message(user.id, conversation_id, guidance_text)
        return AICoachMessageResponse(
            conversation_id=conversation_id,
            user_message=_message(user_msg),
            assistant_message=_message(asst_msg),
            capability=capability_str,
            safety_decision="professional_guidance_required",
            safe_reason_code=policy.reason_code.value,
            provider_used=None,
            created_at=asst_msg.created_at,
        )

    if ai_service is None:
        _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "ai_provider_unavailable",
            "AI coaching features are not configured or available on this server.",
        )

    system_instructions = build_ai_coach_system_instructions()
    request = AIServiceRequest(
        prompt=raw_content,
        system_instructions=system_instructions,
        context_request=AIContextRequest(
            purpose=purpose,
            current_user_question=raw_content,
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
    except AISafetyError as exc:
        user_msg = await service.append_user_message(user.id, conversation_id, raw_content)
        if "professional_guidance" in exc.reason_code or "medical" in exc.reason_code:
            decision_str = "professional_guidance_required"
            safety_text = (
                "Your safety is our priority. Rahafit provides fitness and wellness guidance but does not provide medical advice, diagnosis, or treatment. "
                "Please consult a qualified medical professional or healthcare provider for guidance on medical concerns or symptoms."
            )
        else:
            decision_str = "refuse"
            safety_text = "This request was declined by Rahafit safety controls to ensure health guidelines and prompt security are maintained."

        asst_msg = await service.append_assistant_message(user.id, conversation_id, safety_text)
        return AICoachMessageResponse(
            conversation_id=conversation_id,
            user_message=_message(user_msg),
            assistant_message=_message(asst_msg),
            capability=capability_str,
            safety_decision=decision_str,
            safe_reason_code=exc.reason_code,
            provider_used=None,
            created_at=asst_msg.created_at,
        )

    user_msg = await service.append_user_message(user.id, conversation_id, raw_content)

    try:
        ai_response = await ai_service.generate_prepared_text(request, provider_request, safety)
    except AITimeoutError:
        _error(
            status.HTTP_504_GATEWAY_TIMEOUT,
            "ai_provider_timeout",
            "The AI provider request timed out. Please try again.",
        )
    except AIProviderError:
        _error(
            status.HTTP_502_BAD_GATEWAY,
            "ai_provider_error",
            "An error occurred while communicating with the AI service. Please try again.",
        )

    asst_msg = await service.append_assistant_message(
        user.id, conversation_id, ai_response.output.text
    )

    return AICoachMessageResponse(
        conversation_id=conversation_id,
        user_message=_message(user_msg),
        assistant_message=_message(asst_msg),
        capability=capability_str,
        safety_decision=safety.final_decision.value,
        safe_reason_code=safety.reason_code.value,
        provider_used=ai_response.provider,
        created_at=asst_msg.created_at,
    )
