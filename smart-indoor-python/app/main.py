import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db, AsyncSessionLocal
from app.api import api_router
from app.api.websocket import router as ws_router
from app.iot.mqtt_client import mqtt_service
from app.simulation.scenario_manager import scenario_manager
from app.iot.device_controller import device_controller
from app.services.environment_service import environment_service
from app.services.occupancy_service import occupancy_service
from app.services.comfort_service import comfort_service
from app.services.automation_service import automation_service
from app.schemas.environment import EnvironmentData
from app.schemas.occupancy import OccupancyData
from app.realtime.manager import connection_manager
from app.models.hall import Hall
from sqlalchemy.future import select

setup_logging()
logger = logging.getLogger("smart_indoor.main")

# Background simulation task handle
simulation_task = None

async def run_simulation_loop():
    """
    Continuous background simulation loop.
    Simulates physical sensor telemetry, crowd movements, comfort indexing,
    automation engine evaluation, and real-time WebSocket broadcasting.
    """
    logger.info("Starting background Environmental & Occupancy Simulation worker...")
    while True:
        try:
            if settings.SIMULATION_ENABLED:
                async with AsyncSessionLocal() as db:
                    # Get list of halls
                    result = await db.execute(select(Hall))
                    halls = result.scalars().all()

                    for hall in halls:
                        hall_id = hall.id
                        dev_state = device_controller.get_state(hall_id)
                        ac_power = dev_state["ac"]["power"]
                        fan_speed = dev_state["fan"]["speed"]

                        sensor_sim, occ_sim = scenario_manager.get_or_create_simulators(hall_id, hall.capacity)
                        
                        # Step physics
                        sensor_data = sensor_sim.step(ac_power=ac_power, fan_speed=fan_speed)
                        occ_data = occ_sim.step()

                        # Ingest reading
                        env_payload = EnvironmentData(
                            hall_id=hall_id,
                            temperature=sensor_data["temperature"],
                            humidity=sensor_data["humidity"],
                            co2=sensor_data["co2"],
                            light=sensor_data["light"]
                        )
                        await environment_service.record_reading(db, env_payload)

                        occ_payload = OccupancyData(
                            hall_id=hall_id,
                            people_count=occ_data["people_count"],
                            occupancy_percentage=occ_data["occupancy_percentage"],
                            capacity=occ_data["capacity"],
                            zone_distribution=occ_data["zone_distribution"]
                        )
                        await occupancy_service.record_occupancy(db, occ_payload)

                        # Re-calculate Comfort Score
                        comfort_result = await comfort_service.evaluate_and_record(
                            db,
                            hall_id,
                            temperature=sensor_data["temperature"],
                            humidity=sensor_data["humidity"],
                            co2=sensor_data["co2"],
                            occupancy_pct=occ_data["occupancy_percentage"],
                            light=sensor_data["light"]
                        )

                        # Autonomous Rule Evaluation (Anti-flapping & hysteresis)
                        await automation_service.evaluate_hall_automation(
                            db,
                            hall_id,
                            env_data=sensor_data,
                            occ_data=occ_data
                        )

                        # Real-time WebSocket Broadcast
                        await connection_manager.broadcast_to_hall(hall_id, {
                            "event_type": "environment_update",
                            "hall_id": hall_id,
                            "data": {
                                "hall_id": hall_id,
                                "temperature": sensor_data["temperature"],
                                "humidity": sensor_data["humidity"],
                                "co2": sensor_data["co2"],
                                "light": sensor_data["light"],
                                "iaq_score": comfort_result.get("air_quality_score", 85),
                                "comfort_score": comfort_result["score"],
                                "comfort_status": comfort_result["status"],
                                "timestamp": comfort_result["timestamp"].isoformat()
                            }
                        })

                        await connection_manager.broadcast_to_hall(hall_id, {
                            "event_type": "occupancy_update",
                            "hall_id": hall_id,
                            "data": {
                                "hall_id": hall_id,
                                "people_count": occ_data["people_count"],
                                "occupancy_percentage": occ_data["occupancy_percentage"],
                                "capacity": occ_data["capacity"],
                                "zone_distribution": occ_data["zone_distribution"],
                                "timestamp": comfort_result["timestamp"].isoformat()
                            }
                        })

        except Exception as e:
            logger.error(f"Error in background simulation loop: {e}", exc_info=True)

        await asyncio.sleep(settings.SIMULATION_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Smart Indoor Environment AI & IoT Backend...")
    await init_db()
    mqtt_service.start()
    
    # Auto-seed database if empty
    from scripts.seed_database import seed_all
    try:
        await seed_all()
    except Exception as e:
        logger.warning(f"Database seed check: {e}")

    # Launch simulation task
    sim_task = asyncio.create_task(run_simulation_loop())
    yield
    # Shutdown
    logger.info("Shutting down backend...")
    sim_task.cancel()
    mqtt_service.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI, Computer Vision, and IoT Backend for Smart Indoor Environment Monitoring and Comfort Control",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router)

@app.get("/")
async def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "docs": "/docs",
        "redoc": "/redoc",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
