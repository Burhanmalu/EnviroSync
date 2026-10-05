from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.halls import router as halls_router
from app.api.environment import router as environment_router
from app.api.occupancy import router as occupancy_router
from app.api.devices import router as devices_router
from app.api.automation import router as automation_router
from app.api.notifications import router as notifications_router
from app.api.analytics import router as analytics_router
from app.api.camera import router as camera_router
from app.api.demo import router as demo_router
from app.api.health import router as health_router
from app.api.websocket import router as ws_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(halls_router)
api_router.include_router(environment_router)
api_router.include_router(occupancy_router)
api_router.include_router(devices_router)
api_router.include_router(automation_router)
api_router.include_router(notifications_router)
api_router.include_router(analytics_router)
api_router.include_router(camera_router)
api_router.include_router(demo_router)
api_router.include_router(health_router)
