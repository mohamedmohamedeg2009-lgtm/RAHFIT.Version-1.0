from typing import Annotated, Any, NoReturn, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.controllers.assessment import get_assessment_service
from app.controllers.auth import get_current_user
from app.models.nutrition import NutritionPlan, NutritionProgress
from app.models.user import User
from app.repositories.nutrition import NutritionRepository
from app.schemas.nutrition import (
    CurrentNutritionResponse,
    GenerateNutritionRequest,
    LogMealRequest,
    WaterIntakeRequest,
)
from app.services.assessment import AssessmentService
from app.services.nutrition import (
    NutritionAssessmentRequiredError,
    NutritionNotFoundError,
    NutritionSafetyRestrictedError,
    NutritionService,
)
from app.services.nutrition_engine import NutritionGenerationError
from app.workouts.repository import MongoWorkoutRepository


class IntelligentWorkoutNutritionReader:
    def __init__(self, repo: MongoWorkoutRepository) -> None:
        self.repo = repo

    async def find_current_plan(self, user_id: str) -> Any:
        plan = await self.repo.get_active_plan(user_id)
        if plan is None:
            return None

        class CompatibleWorkoutPlan:
            def __init__(self, p: Any) -> None:
                self.id = p.plan_id
                self.goal = p.primary_goal
                self.available_days = p.training_days_per_week

        return CompatibleWorkoutPlan(plan)


router = APIRouter(prefix="/nutrition", tags=["Nutrition"])


def get_nutrition_service(
    request: Request, assessment: Annotated[AssessmentService, Depends(get_assessment_service)]
) -> NutritionService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    return NutritionService(
        NutritionRepository(database),
        assessment,
        IntelligentWorkoutNutritionReader(MongoWorkoutRepository(database)),
    )


def _translate(exc: Exception) -> NoReturn:
    if isinstance(exc, NutritionNotFoundError):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "nutrition_not_found",
                "message": "Nutrition plan not found.",
                "details": [],
            },
        )
    if isinstance(exc, NutritionAssessmentRequiredError):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "assessment_required",
                "message": "Complete the assessment first.",
                "details": [],
            },
        )
    if isinstance(exc, NutritionSafetyRestrictedError):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "nutrition_safety_restricted",
                "message": "Professional clearance is required.",
                "details": [],
            },
        )
    if isinstance(exc, NutritionGenerationError):
        raise HTTPException(
            status_code=409,
            detail={"code": "nutrition_generation_failed", "message": str(exc), "details": []},
        )
    raise exc


@router.get("/current", response_model=CurrentNutritionResponse)
async def current(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> CurrentNutritionResponse:
    try:
        state = await service.current(user.id)
    except Exception as exc:
        _translate(exc)
    return CurrentNutritionResponse(plan=state.plan, progress=state.progress)


@router.post("/generate", response_model=NutritionPlan, status_code=status.HTTP_201_CREATED)
async def generate(
    body: GenerateNutritionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> NutritionPlan:
    try:
        return await service.generate(
            user.id,
            body.diet_type,
            body.allergies,
            body.preferences,
            body.meal_count,
            body.activity_level,
        )
    except Exception as exc:
        _translate(exc)


@router.get("/history", response_model=tuple[NutritionPlan, ...])
async def history(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> tuple[NutritionPlan, ...]:
    return await service.history(user.id)


@router.post("/meals/log", response_model=NutritionProgress)
async def log_meal(
    body: LogMealRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> NutritionProgress:
    try:
        return await service.log_meal(user.id, body.meal_id)
    except Exception as exc:
        _translate(exc)


@router.post("/water", response_model=NutritionProgress)
async def water(
    body: WaterIntakeRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> NutritionProgress:
    try:
        return await service.add_water(user.id, body.milliliters)
    except Exception as exc:
        _translate(exc)


@router.get("/daily-summary", response_model=CurrentNutritionResponse)
async def daily_summary(
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[NutritionService, Depends(get_nutrition_service)],
) -> CurrentNutritionResponse:
    return await current(user, service)
