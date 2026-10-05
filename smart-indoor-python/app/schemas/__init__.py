from app.schemas.auth import UserBase, UserCreate, UserResponse, LoginRequest, TokenResponse
from app.schemas.hall import HallBase, HallCreate, HallUpdate, HallResponse
from app.schemas.environment import EnvironmentData, EnvironmentResponse, EnvironmentHistoricalQuery
from app.schemas.occupancy import OccupancyData, OccupancyResponse
from app.schemas.device import DeviceBase, DeviceCreate, DeviceUpdate, DeviceCommand, DeviceResponse, HallDevicesState
from app.schemas.automation import (
    AutomationRuleBase, AutomationRuleCreate, AutomationRuleUpdate,
    AutomationRuleResponse, AutomationAction, AutomationEventResponse
)
from app.schemas.notification import NotificationBase, NotificationCreate, NotificationResponse
from app.schemas.analytics import ComfortScoreResponse, PredictionResponse, AnalyticsSummaryResponse
from app.schemas.camera import CameraStatusResponse
from app.schemas.demo import DemoScenarioRequest, DemoScenarioResponse
from app.schemas.health import HealthCheckResponse

__all__ = [
    "UserBase", "UserCreate", "UserResponse", "LoginRequest", "TokenResponse",
    "HallBase", "HallCreate", "HallUpdate", "HallResponse",
    "EnvironmentData", "EnvironmentResponse", "EnvironmentHistoricalQuery",
    "OccupancyData", "OccupancyResponse",
    "DeviceBase", "DeviceCreate", "DeviceUpdate", "DeviceCommand", "DeviceResponse", "HallDevicesState",
    "AutomationRuleBase", "AutomationRuleCreate", "AutomationRuleUpdate",
    "AutomationRuleResponse", "AutomationAction", "AutomationEventResponse",
    "NotificationBase", "NotificationCreate", "NotificationResponse",
    "ComfortScoreResponse", "PredictionResponse", "AnalyticsSummaryResponse",
    "CameraStatusResponse",
    "DemoScenarioRequest", "DemoScenarioResponse",
    "HealthCheckResponse"
]
