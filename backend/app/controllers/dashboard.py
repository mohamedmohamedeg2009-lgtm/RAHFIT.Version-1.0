from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.models.user import User
from app.repositories.assessments import AssessmentRepository
from app.schemas.dashboard import DashboardResponse
from app.services.assessment import AssessmentService
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(request: Request) -> DashboardService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    assessment = AssessmentService(AssessmentRepository(database))
    return DashboardService(assessment)


@router.get(
    "",
    response_model=DashboardResponse,
    summary="Get the authenticated user's intelligent dashboard",
    description=(
        "Returns an owner-scoped aggregate with one deterministic priority, assessment state, "
        "feature availability, safety restrictions, and real-data progress signals."
    ),
)
async def get_dashboard(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardResponse:
    dashboard = await service.get_dashboard(user)
    return DashboardResponse.model_validate(dashboard.model_dump())
