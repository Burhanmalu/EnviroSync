import json
import logging
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger("smart_indoor.websocket")

class ConnectionManager:
    """
    WebSocket Connection Manager for multi-client real-time synchronization.
    Supports room subscriptions per hall_id and global broadcast.
    """

    def __init__(self):
        # Map hall_id -> Set of active WebSocket connections
        self.active_rooms: Dict[str, Set[WebSocket]] = {}
        # All connected clients
        self.all_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, hall_id: str):
        await websocket.accept()
        self.all_connections.add(websocket)
        if hall_id not in self.active_rooms:
            self.active_rooms[hall_id] = set()
        self.active_rooms[hall_id].add(websocket)
        logger.info(f"WebSocket client connected to hall {hall_id}. Active room count: {len(self.active_rooms[hall_id])}")

        # Send initial connection handshake
        await websocket.send_text(json.dumps({
            "event_type": "connection_status",
            "hall_id": hall_id,
            "data": {
                "status": "CONNECTED",
                "message": f"Subscribed to real-time telemetry stream for {hall_id}"
            }
        }))

    def disconnect(self, websocket: WebSocket, hall_id: str):
        if websocket in self.all_connections:
            self.all_connections.remove(websocket)
        if hall_id in self.active_rooms and websocket in self.active_rooms[hall_id]:
            self.active_rooms[hall_id].remove(websocket)
            if len(self.active_rooms[hall_id]) == 0:
                del self.active_rooms[hall_id]
        logger.info(f"WebSocket client disconnected from hall {hall_id}")

    async def broadcast_to_hall(self, hall_id: str, message: dict):
        if hall_id in self.active_rooms:
            payload_str = json.dumps(message)
            dead_sockets = []
            for connection in list(self.active_rooms[hall_id]):
                try:
                    await connection.send_text(payload_str)
                except Exception as e:
                    logger.warning(f"Error sending message to client: {e}")
                    dead_sockets.append(connection)

            for dead in dead_sockets:
                self.disconnect(dead, hall_id)

    async def broadcast_global(self, message: dict):
        payload_str = json.dumps(message)
        dead_sockets = []
        for connection in list(self.all_connections):
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                dead_sockets.append(connection)

        for dead in dead_sockets:
            if dead in self.all_connections:
                self.all_connections.remove(dead)

connection_manager = ConnectionManager()
