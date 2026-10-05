import json
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger("smart_indoor.mqtt")

try:
    import paho.mqtt.client as mqtt
    PAHO_AVAILABLE = True
except ImportError:
    PAHO_AVAILABLE = False

class MQTTService:
    """
    MQTT Communication Service for ESP32 Gateways and Edge Sensors.
    Topics:
      - {prefix}/{hall_id}/environment
      - {prefix}/{hall_id}/occupancy
      - {prefix}/{hall_id}/devices
      - {prefix}/{hall_id}/commands
      - {prefix}/{hall_id}/events
    """

    def __init__(self):
        self.client = None
        self.connected = False
        self.callbacks: Dict[str, list[Callable[[Dict[str, Any]], None]]] = {}

    def start(self):
        if not settings.MQTT_ENABLED:
            logger.info("MQTT disabled via configuration. Using internal mock bus.")
            return

        if not PAHO_AVAILABLE:
            logger.warning("paho-mqtt not installed. MQTT client running in virtual mode.")
            return

        try:
            self.client = mqtt.Client()
            if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
                self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)

            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.on_disconnect = self._on_disconnect

            self.client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, 60)
            self.client.loop_start()
            logger.info(f"MQTT Client connecting to {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info("MQTT Broker connected successfully.")
            # Subscribe to all hall subtopics
            sub_topic = f"{settings.MQTT_TOPIC_PREFIX}/+/+"
            self.client.subscribe(sub_topic)
            logger.info(f"Subscribed to topic pattern: {sub_topic}")
        else:
            logger.error(f"MQTT Connection failed with code {rc}")

    def _on_disconnect(self, client, userdata, rc):
        self.connected = False
        logger.warning(f"MQTT Client disconnected. RC: {rc}")

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            topic = msg.topic
            logger.debug(f"MQTT Message received on {topic}: {payload}")
            for pattern, cbs in self.callbacks.items():
                if mqtt.topic_matches_sub(pattern, topic):
                    for cb in cbs:
                        cb(payload)
        except Exception as e:
            logger.error(f"Error parsing incoming MQTT message: {e}")

    def publish_command(self, hall_id: str, device_type: str, action: str, value: Any = None):
        """
        Publish command payload for ESP32 actuator relay.
        """
        topic = f"{settings.MQTT_TOPIC_PREFIX}/{hall_id}/commands"
        payload = {
            "device": device_type,
            "action": action,
            "value": value
        }
        if self.connected and self.client:
            self.client.publish(topic, json.dumps(payload), qos=1)
            logger.info(f"Published MQTT command to {topic}: {payload}")
        else:
            logger.debug(f"[Virtual MQTT] Command routed to {topic}: {payload}")

    def register_callback(self, topic_pattern: str, callback: Callable[[Dict[str, Any]], None]):
        if topic_pattern not in self.callbacks:
            self.callbacks[topic_pattern] = []
        self.callbacks[topic_pattern].append(callback)

    def stop(self):
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT Client stopped.")

mqtt_service = MQTTService()
