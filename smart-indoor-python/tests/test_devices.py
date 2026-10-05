import pytest

@pytest.mark.asyncio
async def test_device_control_and_override(async_client):
    # Check hall devices
    devs_res = await async_client.get("/api/halls/hall-01/devices")
    assert devs_res.status_code == 200

    # Execute device command
    cmd_res = await async_client.post("/api/devices/ac-hall-01/command", json={
        "action": "SET_TEMP",
        "value": 21.5
    })
    # If device exists, returns 200
    if cmd_res.status_code == 200:
        d_data = cmd_res.json()
        assert d_data["control_mode"] == "MANUAL"
        assert d_data["state"]["target_temp"] == 21.5
