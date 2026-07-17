from datetime import date
from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Query, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.auth import get_current_user
from app.health import HealthProfileRepository
from app.models.ai_decision import DailyDecision
from app.models.user import User
from app.profile import UserProfileRepository
from app.repositories.ai_decisions import AIDecisionRepository
from app.repositories.nutrition import NutritionRepository
from app.services.ai_decision import AIDecisionEngineService
from app.workouts.repository import MongoWorkoutRepository

router = APIRouter(prefix="/decisions", tags=["AI Decisions"])


def get_ai_decision_service(request: Request) -> AIDecisionEngineService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return AIDecisionEngineService(
        decision_repo=AIDecisionRepository(database),
        profile_repo=UserProfileRepository(database),
        health_repo=HealthProfileRepository(database),
        workout_repo=MongoWorkoutRepository(database),
        nutrition_repo=NutritionRepository(database),
    )


@router.get(
    "/today",
    response_model=DailyDecision,
    summary="Get today's active AI decision",
    description="Returns the active daily decision for the authenticated user.",
)
async def get_today_decision(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIDecisionEngineService, Depends(get_ai_decision_service)],
) -> DailyDecision:
    today_date = date.today()
    decision = await service.get_or_generate_decision(user, today_date, force_regenerate=False)
    return decision


@router.post(
    "/generate",
    response_model=DailyDecision,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a daily decision snapshot",
    description="Idempotently creates or overrides a daily decision based on current readiness, pain, and log snapshot.",
)
async def generate_daily_decision(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AIDecisionEngineService, Depends(get_ai_decision_service)],
    force_regenerate: bool = Query(default=False),
) -> DailyDecision:
    today_date = date.today()
    decision = await service.get_or_generate_decision(
        user, today_date, force_regenerate=force_regenerate
    )
    return decision
