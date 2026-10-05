import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import logging
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.models.hall import Hall
from app.models.device import Device
from app.models.automation import AutomationRule
from app.models.notification import Notification
from app.core.security import get_password_hash

logger = logging.getLogger("smart_indoor.seed")

async def seed_all():
    async with AsyncSessionLocal() as db:
        # 1. Seed Users
        admin_res = await db.execute(select(User).where(User.email == "admin@envirosync.in"))
        if not admin_res.scalars().first():
            logger.info("Seeding default users...")
            admin_user = User(
                id="user-admin-01",
                email="admin@envirosync.in",
                hashed_password=get_password_hash("Admin@123456"),
                full_name="Dr. Rajesh Sharma",
                role=UserRole.ADMIN,
                is_active=True
            )
            demo_user = User(
                id="user-demo-01",
                email="user@envirosync.in",
                hashed_password=get_password_hash("User@123456"),
                full_name="Priya Patel",
                role=UserRole.USER,
                assigned_hall_id="hall-01",
                is_active=True
            )
            db.add_all([admin_user, demo_user])
            await db.commit()

        # 2. Seed Halls
        halls_data = [
            {"id": "hall-01", "name": "Hall 01", "building": "Aryabhata Academic Block", "floor": 1, "capacity": 60},
        ]

        for h in halls_data:
            h_res = await db.execute(select(Hall).where(Hall.id == h["id"]))
            if not h_res.scalars().first():
                logger.info(f"Seeding Hall {h['id']}...")
                hall = Hall(
                    id=h["id"],
                    name=h["name"],
                    building=h["building"],
                    floor=h["floor"],
                    capacity=h["capacity"],
                    current_occupancy=int(h["capacity"] * 0.35),
                    status="OPTIMAL",
                    comfort_score=87,
                    comfort_status="EXCELLENT"
                )
                db.add(hall)

                # Seed Devices for this hall
                ac = Device(
                    id=f"ac-{h['id']}",
                    hall_id=h["id"],
                    name=f"{h['name']} AC Unit 1",
                    type="ac",
                    status="ONLINE",
                    power=True,
                    control_mode="AUTO",
                    state={"target_temp": 24.0, "mode": "cool", "fan_speed": "auto"}
                )
                fan = Device(
                    id=f"fan-{h['id']}",
                    hall_id=h["id"],
                    name=f"{h['name']} Ventilation Fan",
                    type="fan",
                    status="ONLINE",
                    power=True,
                    control_mode="AUTO",
                    state={"speed": 2, "oscillation": False}
                )
                curtain = Device(
                    id=f"curtain-{h['id']}",
                    hall_id=h["id"],
                    name=f"{h['name']} Smart Blinds",
                    type="curtain",
                    status="ONLINE",
                    power=True,
                    control_mode="AUTO",
                    state={"position": 50, "state": "PARTIAL"}
                )
                db.add_all([ac, fan, curtain])

                # Seed Automation Rules for this hall
                r1 = AutomationRule(
                    id=f"rule-temp-{h['id']}",
                    hall_id=h["id"],
                    name="High Temperature Cooling Trigger",
                    description="Activates AC Cooling when temperature exceeds 28°C with 0.5°C hysteresis",
                    condition_type="TEMPERATURE",
                    operator=">",
                    threshold=28.0,
                    hysteresis=0.5,
                    action_device="AC",
                    action_type="COOLING",
                    action_value="22.0",
                    priority=3,
                    enabled=True,
                    cooldown_seconds=180
                )
                r2 = AutomationRule(
                    id=f"rule-occ-{h['id']}",
                    hall_id=h["id"],
                    name="High Crowd Density Ventilation",
                    description="Increases ventilation speed when room occupancy exceeds 70%",
                    condition_type="OCCUPANCY",
                    operator=">",
                    threshold=70.0,
                    hysteresis=2.0,
                    action_device="FAN",
                    action_type="SPEED_HIGH",
                    action_value="4",
                    priority=2,
                    enabled=True,
                    cooldown_seconds=120
                )
                r3 = AutomationRule(
                    id=f"rule-co2-{h['id']}",
                    hall_id=h["id"],
                    name="CO2 Air Quality Safety Threshold",
                    description="Triggers air circulation and safety alert if CO2 exceeds 1000 ppm",
                    condition_type="CO2",
                    operator=">",
                    threshold=1000.0,
                    hysteresis=50.0,
                    action_device="FAN",
                    action_type="SPEED_HIGH",
                    action_value="5",
                    priority=4,
                    enabled=True,
                    cooldown_seconds=300
                )
                r4 = AutomationRule(
                    id=f"rule-empty-{h['id']}",
                    hall_id=h["id"],
                    name="Empty Room Energy Saver",
                    description="Switches AC to energy saving mode when room occupancy is below 10%",
                    condition_type="OCCUPANCY",
                    operator="<",
                    threshold=10.0,
                    hysteresis=2.0,
                    action_device="AC",
                    action_type="ENERGY_SAVING",
                    action_value="OFF",
                    priority=1,
                    enabled=True,
                    cooldown_seconds=300
                )
                db.add_all([r1, r2, r3, r4])

        # 3. Seed Initial Notifications
        notif_res = await db.execute(select(Notification).limit(1))
        if not notif_res.scalars().first():
            n1 = Notification(
                id="notif-init-01",
                hall_id="hall-01",
                title="System Initialized",
                message="AI Environment Monitoring & Automation Engine active.",
                type="SUCCESS",
                category="SYSTEM"
            )
            n2 = Notification(
                id="notif-init-02",
                hall_id="hall-01",
                title="Comfort Score Optimal",
                message="Seminar Hall 01 operating at 87% comfort index.",
                type="INFO",
                category="ENVIRONMENT"
            )
            db.add_all([n1, n2])

        await db.commit()
        logger.info("Database seeding successfully completed.")

if __name__ == "__main__":
    async def main():
        await init_db()
        await seed_all()
    asyncio.run(main())
