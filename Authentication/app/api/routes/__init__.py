from fastapi import APIRouter
from .login import router as login_router
from .dashboard import router as dashboard_router

router = APIRouter()

router.include_router(login_router, prefix="/auth", tags=["auth"])
router.include_router(dashboard_router, prefix="/user", tags=["dashboard"])
