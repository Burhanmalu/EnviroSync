import pytest

@pytest.mark.asyncio
async def test_environment_ingest_and_get(async_client):
    # Ingest telemetry
    post_res = await async_client.post("/api/halls/hall-01/environment", json={
        "hall_id": "hall-01",
        "temperature": 26.5,
        "humidity": 55.0,
        "co2": 620.0,
        "light": 480.0
    })
    assert post_res.status_code == 200
    data = post_res.json()
    assert data["temperature"] == 26.5
    assert data["co2"] == 620.0
    assert "iaq_score" in data

    # Retrieve latest reading
    get_res = await async_client.get("/api/halls/hall-01/environment")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["temperature"] == 26.5
