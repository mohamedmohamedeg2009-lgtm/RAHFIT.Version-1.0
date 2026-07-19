from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import get_settings
from app.controllers.auth import get_current_user
from app.models.user import User
from app.repositories.assessments import AssessmentRepository
from app.repositories.nutrition import NutritionRepository
from app.repositories.workouts import WorkoutRepository
from app.schemas.dashboard import DashboardResponse
from app.services.ai_availability import AIAvailabilityService
from app.services.assessment import AssessmentService
from app.services.dashboard import DashboardService
from app.services.nutrition import NutritionService
from app.workouts.repository import MongoWorkoutRepository


class IntelligentWorkoutDashboardAdapter:
    def __init__(self, repository: MongoWorkoutRepository) -> None:
        self.repository = repository

    async def get_dashboard_state(self, user_id: str) -> Any:
        from datetime import UTC, datetime

        from app.models.workout import WorkoutDashboardState

        plan = await self.repository.get_active_plan(user_id)
        if not plan:
            return None

        # Determine today's weekday (1-7)
        now = datetime.now(UTC)
        weekday = now.isoweekday()
        day = next((d for d in plan.weekly_schedule if d.weekday == weekday), None)
        if not day and plan.weekly_schedule:
            day = plan.weekly_schedule[0]

        if not day:
            return None

        sessions = await self.repository.list_sessions(user_id, plan.plan_id, limit=50)
        today_date = now.date()

        session = next((s for s in sessions if s.status == "in_progress"), None)
        if not session:
            session = next((s for s in sessions if s.started_at.date() == today_date), None)

        status = "not_started"
        completion = 0
        if session:
            status = session.status.value
            completion = session.completion_percentage
            route = (
                f"/intelligent-workouts/sessions/{session.session_id}"
                if status == "in_progress"
                else "/intelligent-workouts"
            )
        else:
            route = "/intelligent-workouts"

        return WorkoutDashboardState(
            plan_id=plan.plan_id,
            day_id=f"day-{day.day_number}",
            title=day.title,
            focus=day.focus,
            status=status,
            completion_percentage=completion,
            destination_route=route,
            last_activity_at=session.updated_at if session else plan.generated_at,
        )


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_dashboard_service(request: Request) -> DashboardService:
    database = cast(AsyncIOMotorDatabase[dict[str, Any]], request.app.state.database.database)
    assessment = AssessmentService(AssessmentRepository(database))
    workout = IntelligentWorkoutDashboardAdapter(MongoWorkoutRepository(database))
    nutrition = NutritionService(
        NutritionRepository(database), assessment, WorkoutRepository(database)
    )
    from app.repositories.daily_check_in import MongoDailyCheckInRepository
    from app.services.daily_check_in import DailyCheckInService
    from app.services.daily_check_in_engine import DailyCheckInEngine

    check_in_service = DailyCheckInService(
        MongoDailyCheckInRepository(database), DailyCheckInEngine()
    )
    settings = get_settings()
    return DashboardService(
        assessment,
        workout,
        nutrition,
        AIAvailabilityService(settings),
        daily_check_in_reader=check_in_service,
    )


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
