import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.realtime.manager import connection_manager

logger = logging.getLogger("smart_indoor.ws_router")
router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/halls/{hall_id}")
async def websocket_hall_endpoint(websocket: WebSocket, hall_id: str):
    await connection_manager.connect(websocket, hall_id)
    try:
        while True:
            # Keep receiving client events (e.g. ping/heartbeat or client requests)
            raw_text = await websocket.receive_text()
            try:
                data = json.loads(raw_text)
                msg_type = data.get("type", "ping")
                if msg_type == "ping":
                    await websocket.send_text(json.dumps({
                        "event_type": "pong",
                        "hall_id": hall_id,
                        "data": {"status": "ALIVE"}
                    }))
            except Exception:
                pass
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, hall_id)
    except Exception as e:
        logger.warning(f"WebSocket exception on hall {hall_id}: {e}")
        connection_manager.disconnect(websocket, hall_id)
