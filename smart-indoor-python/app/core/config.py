from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Smart Indoor Environment Monitoring & Automated Comfort Control System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./smart_indoor.db"
    SYNC_DATABASE_URL: str = "sqlite:///./smart_indoor.db"
    DB_ECHO: bool = False

    # Security / JWT
    SECRET_KEY: str = "envirosync-super-secret-jwt-signing-key-production-grade-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:19006",
        "*"
    ]

    # MQTT Settings
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_TOPIC_PREFIX: str = "smart-building"
    MQTT_ENABLED: bool = False

    # Simulation Defaults
    SIMULATION_ENABLED: bool = True
    SIMULATION_INTERVAL_SECONDS: float = 3.0
    
    # Camera Defaults
    CAMERA_SOURCE: str = "mock"
    CAMERA_RTSP_URL: str = ""
    CAMERA_FPS: int = 5

    # Demo Mode
    DEMO_DEFAULT_SCENARIO: str = "NORMAL"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
