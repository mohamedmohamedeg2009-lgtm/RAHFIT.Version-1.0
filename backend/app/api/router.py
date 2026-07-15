from fastapi import APIRouter

from app.controllers.assessment import router as assessment_router
from app.controllers.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(assessment_router)
