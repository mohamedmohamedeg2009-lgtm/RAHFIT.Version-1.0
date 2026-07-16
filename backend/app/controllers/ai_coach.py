from typing import Annotated

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.controllers.auth import get_current_user
from app.models.user import User
from app.schemas.ai_provider import AIAvailabilityResponse
from app.services.ai_availability import AIAvailabilityService

router = APIRouter(prefix="/ai-coach", tags=["AI Provider Infrastructure"])


def get_ai_availability_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AIAvailabilityService:
    return AIAvailabilityService(settings)


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
