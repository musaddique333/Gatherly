from fastapi import APIRouter
from .events import router as events_router
from .members import router as member_router
from .reminders import router as reminder_router

router = APIRouter()

router.include_router(events_router, prefix="/event", tags=["events"])
router.include_router(member_router, prefix="/event-members", tags=["event-members"])
router.include_router(reminder_router, prefix="/reminder", tags=["reminder"])