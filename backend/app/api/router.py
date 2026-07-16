from fastapi import APIRouter

from app.controllers.assessment import router as assessment_router
from app.controllers.auth import router as auth_router
from app.controllers.dashboard import router as dashboard_router
from app.controllers.workout import router as workout_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(assessment_router)
router.include_router(dashboard_router)
router.include_router(workout_router)
