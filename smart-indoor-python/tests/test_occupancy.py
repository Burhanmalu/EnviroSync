import pytest

@pytest.mark.asyncio
async def test_occupancy_ingest_and_cv(async_client):
    post_res = await async_client.post("/api/halls/hall-01/occupancy", json={
        "hall_id": "hall-01",
        "people_count": 35,
        "occupancy_percentage": 58.3,
        "capacity": 60,
        "zone_distribution": {
            "Zone A": 12,
            "Zone B": 10,
            "Zone C": 8,
            "Zone D": 5
        }
    })
    assert post_res.status_code == 200
    data = post_res.json()
    assert data["people_count"] == 35
    assert data["zone_distribution"]["Zone A"] == 12

    # Camera status
    cam_res = await async_client.get("/api/halls/hall-01/camera")
    assert cam_res.status_code == 200
    cam_data = cam_res.json()
    assert "privacy_notice" in cam_data
    assert "people_detected" in cam_data
