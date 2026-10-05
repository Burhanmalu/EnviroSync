import pytest

@pytest.mark.asyncio
async def test_automation_rules_flow(async_client):
    # Fetch automation rules
    rules_res = await async_client.get("/api/halls/hall-01/automation/rules")
    assert rules_res.status_code == 200
    rules = rules_res.json()
    assert isinstance(rules, list)

    # Ingest high temperature to trigger cooling rule
    env_res = await async_client.post("/api/halls/hall-01/environment", json={
        "hall_id": "hall-01",
        "temperature": 31.5,
        "humidity": 65.0,
        "co2": 700.0,
        "light": 500.0
    })
    assert env_res.status_code == 200

    # Fetch events
    events_res = await async_client.get("/api/halls/hall-01/automation/events")
    assert events_res.status_code == 200
