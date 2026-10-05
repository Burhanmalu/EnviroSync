from app.services.auth_service import auth_service
from app.services.environment_service import environment_service
from app.services.occupancy_service import occupancy_service
from app.services.device_service import device_service
from app.services.automation_service import automation_service
from app.services.notification_service import notification_service
from app.services.analytics_service import analytics_service
from app.services.comfort_service import comfort_service
from app.services.prediction_service import prediction_service
from app.services.demo_service import demo_service
from app.services.camera_service import camera_service

__all__ = [
    "auth_service",
    "environment_service",
    "occupancy_service",
    "device_service",
    "automation_service",
    "notification_service",
    "analytics_service",
    "comfort_service",
    "prediction_service",
    "demo_service",
    "camera_service"
]
