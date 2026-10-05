from fastapi import APIRouter, Depends, Query, Body, HTTPException, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.camera import CameraStatusResponse
from app.services.camera_service import camera_service
from app.models.hall import Hall
from sqlalchemy.future import select

router = APIRouter(tags=["Camera & CV"])

@router.get("/halls/{id}/camera", response_model=CameraStatusResponse)
async def get_hall_camera_feed(id: str, db: AsyncSession = Depends(get_db)):
    hall_res = await db.execute(select(Hall).where(Hall.id == id))
    hall = hall_res.scalars().first()
    capacity = hall.capacity if hall else 50

    status_data = camera_service.get_status(id, capacity=capacity)
    return CameraStatusResponse(**status_data)

@router.get("/halls/{id}/camera/stream")
async def stream_hall_camera(id: str):
    """
    Live MJPEG Video Stream from laptop camera (or simulated stream)
    with real-time person detection bounding box overlays.
    Open in browser: http://localhost:8000/api/halls/hall-01/camera/stream
    """
    # Ensure camera is initialized
    if camera_service.camera_source != "webcam":
        camera_service.init_webcam(0)

    return StreamingResponse(
        camera_service.generate_mjpeg_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@router.get("/halls/{id}/camera/snapshot")
async def snapshot_hall_camera(id: str):
    """
    Captures a single annotated JPEG snapshot from the laptop webcam.
    """
    if camera_service.camera_source != "webcam":
        camera_service.init_webcam(0)

    jpeg_bytes, det = camera_service.read_annotated_frame()
    if jpeg_bytes is None:
        raise HTTPException(status_code=503, detail="Camera frame unavailable")

    return Response(content=jpeg_bytes, media_type="image/jpeg")

@router.post("/halls/{id}/camera/source")
async def set_camera_source(
    id: str,
    source: str = Body("webcam", embed=True)
):
    """
    Switch camera feed source between 'webcam' (laptop camera 0) and 'mock'.
    """
    success = camera_service.set_camera_source(source)
    return {
        "hall_id": id,
        "source": camera_service.camera_source,
        "status": camera_service.camera_status,
        "success": success
    }

@router.put("/halls/{id}/camera/status")
async def update_camera_status(
    id: str,
    status: str = Body(..., embed=True)
):
    camera_service.set_camera_state(status)
    return {"hall_id": id, "status": status}
