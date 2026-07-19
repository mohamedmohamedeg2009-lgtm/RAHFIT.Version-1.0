from fastapi import APIRouter

from app.controllers.ai_coach import router as ai_coach_router
from app.controllers.ai_decision import router as ai_decision_router
from app.controllers.assessment import router as assessment_router
from app.controllers.auth import router as auth_router
from app.controllers.daily_check_in import router as daily_check_in_router
from app.controllers.dashboard import router as dashboard_router
from app.controllers.intelligent_workout import router as intelligent_workout_router
from app.controllers.nutrition import router as nutrition_router
from app.controllers.user_intelligence import router as user_intelligence_router
from app.controllers.workout import router as workout_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(user_intelligence_router)
router.include_router(assessment_router)
router.include_router(daily_check_in_router)
router.include_router(dashboard_router)
router.include_router(workout_router)
router.include_router(intelligent_workout_router)
router.include_router(nutrition_router)
router.include_router(ai_coach_router)
router.include_router(ai_decision_router)
