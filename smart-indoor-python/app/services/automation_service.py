import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.automation import AutomationRule, AutomationEvent
from app.models.device import Device
from app.models.notification import Notification
from app.schemas.automation import AutomationRuleCreate, AutomationRuleUpdate, AutomationAction
from app.iot.device_controller import device_controller
from app.realtime.manager import connection_manager

logger = logging.getLogger("smart_indoor.automation")

class AutomationService:
    async def get_rules(self, db: AsyncSession, hall_id: str) -> List[AutomationRule]:
        result = await db.execute(
            select(AutomationRule)
            .where(AutomationRule.hall_id == hall_id)
            .order_by(AutomationRule.priority.desc())
        )
        return list(result.scalars().all())

    async def get_rule_by_id(self, db: AsyncSession, rule_id: str) -> Optional[AutomationRule]:
        result = await db.execute(select(AutomationRule).where(AutomationRule.id == rule_id))
        return result.scalars().first()

    async def create_rule(self, db: AsyncSession, rule_in: AutomationRuleCreate) -> AutomationRule:
        rule = AutomationRule(
            id=rule_in.id,
            hall_id=rule_in.hall_id,
            name=rule_in.name,
            description=rule_in.description,
            condition_type=rule_in.condition_type,
            operator=rule_in.operator,
            threshold=rule_in.threshold,
            hysteresis=rule_in.hysteresis,
            action_device=rule_in.action_device,
            action_type=rule_in.action_type,
            action_value=rule_in.action_value,
            priority=rule_in.priority,
            enabled=rule_in.enabled,
            cooldown_seconds=rule_in.cooldown_seconds
        )
        db.add(rule)
        await db.commit()
        await db.refresh(rule)
        return rule

    async def update_rule(self, db: AsyncSession, rule_id: str, rule_in: AutomationRuleUpdate) -> Optional[AutomationRule]:
        rule = await self.get_rule_by_id(db, rule_id)
        if not rule:
            return None

        for field, value in rule_in.model_dump(exclude_unset=True).items():
            setattr(rule, field, value)

        await db.commit()
        await db.refresh(rule)
        return rule

    async def get_events(self, db: AsyncSession, hall_id: str, limit: int = 50) -> List[AutomationEvent]:
        result = await db.execute(
            select(AutomationEvent)
            .where(AutomationEvent.hall_id == hall_id)
            .order_by(AutomationEvent.timestamp.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def evaluate_hall_automation(
        self,
        db: AsyncSession,
        hall_id: str,
        env_data: Dict[str, float],
        occ_data: Dict[str, Any]
    ) -> List[AutomationAction]:
        """
        Autonomous rule evaluation with anti-flapping hysteresis and override checking.
        """
        rules = await self.get_rules(db, hall_id)
        if not rules:
            return []

        devices = await db.execute(select(Device).where(Device.hall_id == hall_id))
        device_map = {d.type.lower(): d for d in devices.scalars().all()}

        actions_taken: List[AutomationAction] = []
        now = datetime.now(timezone.utc)

        for rule in rules:
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.last_triggered:
                # Handle naive / aware datetime
                last_trig = rule.last_triggered
                if last_trig.tzinfo is None:
                    last_trig = last_trig.replace(tzinfo=timezone.utc)
                if (now - last_trig).total_seconds() < rule.cooldown_seconds:
                    continue

            # Evaluate condition
            triggered = False
            trigger_reason = ""
            val = 0.0

            if rule.condition_type == "TEMPERATURE":
                val = env_data.get("temperature", 25.0)
                # Anti-flapping hysteresis
                if rule.operator == ">" and val > (rule.threshold + rule.hysteresis):
                    triggered = True
                    trigger_reason = f"Temperature {val}°C exceeded threshold ({rule.threshold}°C + hysteresis {rule.hysteresis}°C)"
                elif rule.operator == "<" and val < (rule.threshold - rule.hysteresis):
                    triggered = True
                    trigger_reason = f"Temperature {val}°C dropped below threshold ({rule.threshold}°C - hysteresis {rule.hysteresis}°C)"
            elif rule.condition_type == "OCCUPANCY":
                val = occ_data.get("occupancy_percentage", 0.0)
                if rule.operator == ">" and val > (rule.threshold + rule.hysteresis):
                    triggered = True
                    trigger_reason = f"Occupancy {val}% exceeded threshold ({rule.threshold}%)"
                elif rule.operator == "<" and val < (rule.threshold - rule.hysteresis):
                    triggered = True
                    trigger_reason = f"Occupancy {val}% dropped below threshold ({rule.threshold}%)"
            elif rule.condition_type == "CO2":
                val = env_data.get("co2", 450.0)
                if rule.operator == ">" and val > rule.threshold:
                    triggered = True
                    trigger_reason = f"Air quality CO2 {val} ppm exceeded safety threshold ({rule.threshold} ppm)"

            if triggered:
                target_dev_type = rule.action_device.lower()
                dev = device_map.get(target_dev_type)

                # Respect Manual Override
                if dev and dev.control_mode == "MANUAL":
                    if dev.manual_override_until and dev.manual_override_until > now:
                        logger.info(f"Automation skipped for {dev.name} due to active manual override")
                        continue
                    else:
                        dev.control_mode = "AUTO"
                        dev.manual_override_until = None

                # Apply device action
                action = AutomationAction(
                    device=rule.action_device,
                    action=rule.action_type,
                    value=rule.action_value,
                    reason=trigger_reason
                )
                actions_taken.append(action)

                # Execute action via device controller
                if target_dev_type == "ac":
                    if rule.action_type in ["COOLING", "ON"]:
                        device_controller.turn_ac_on(hall_id)
                        device_controller.set_ac_temperature(hall_id, float(rule.action_value or 22.0))
                    elif rule.action_type in ["OFF", "ENERGY_SAVING"]:
                        device_controller.turn_ac_off(hall_id)
                elif target_dev_type == "fan":
                    if rule.action_type in ["SPEED_HIGH", "HIGH"]:
                        device_controller.set_fan_speed(hall_id, 4)
                    elif rule.action_type in ["SPEED_LOW", "LOW"]:
                        device_controller.set_fan_speed(hall_id, 1)

                # Update rule last_triggered
                rule.last_triggered = now

                # Record automation event in DB
                evt = AutomationEvent(
                    hall_id=hall_id,
                    rule_id=rule.id,
                    rule_name=rule.name,
                    trigger_reason=trigger_reason,
                    actions_taken=[action.model_dump()]
                )
                db.add(evt)

                # Create safety notification if High CO2 or Critical Temp
                if rule.condition_type == "CO2" or (rule.condition_type == "TEMPERATURE" and val >= 30.0):
                    notif = Notification(
                        id=f"notif-{uuid.uuid4().hex[:8]}",
                        hall_id=hall_id,
                        title=f"Automated Alert: {rule.name}",
                        message=trigger_reason,
                        type="WARNING" if val < 32 else "CRITICAL",
                        category="AUTOMATION"
                    )
                    db.add(notif)

        if actions_taken:
            await db.commit()
            # Broadcast automation event via WebSocket
            await connection_manager.broadcast_to_hall(hall_id, {
                "event_type": "automation_event",
                "hall_id": hall_id,
                "data": {
                    "actions": [a.model_dump() for a in actions_taken]
                }
            })

        return actions_taken

automation_service = AutomationService()
