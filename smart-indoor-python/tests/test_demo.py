import pytest

@pytest.mark.asyncio
async def test_demo_scenario_activation(async_client):
    res = await async_client.post("/api/demo/scenario", json={
        "scenario": "HIGH_TEMPERATURE",
        "hall_id": "hall-01"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["current_scenario"] == "HIGH_TEMPERATURE"

    # Verify status
    stat_res = await async_client.get("/api/demo/status/hall-01")
    assert stat_res.status_code == 200
    assert stat_res.json()["current_scenario"] == "HIGH_TEMPERATURE"
