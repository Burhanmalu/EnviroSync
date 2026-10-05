import pytest

@pytest.mark.asyncio
async def test_auth_flow(async_client):
    # 1. Register a new user
    reg_res = await async_client.post("/api/auth/register", json={
        "email": "tester@envirosync.io",
        "password": "Password@123",
        "full_name": "Test Engineer",
        "role": "USER"
    })
    assert reg_res.status_code in [200, 201]
    data = reg_res.json()
    assert data["email"] == "tester@envirosync.io"

    # 2. Login
    login_res = await async_client.post("/api/auth/login", json={
        "email": "tester@envirosync.io",
        "password": "Password@123"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # 3. Get profile
    me_res = await async_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "tester@envirosync.io"
