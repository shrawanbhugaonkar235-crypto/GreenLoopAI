import uuid
import pytest

def test_register_and_login_flow(client):
    unique_email = f"citizen_{uuid.uuid4().hex[:8]}@example.com"
    
    # 1. Register
    reg_payload = {
        "name": "Aarav Sharma",
        "email": unique_email,
        "password": "securepassword123"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == unique_email
    assert reg_data["user"]["name"] == "Aarav Sharma"

    token = reg_data["access_token"]

    # 2. Duplicate registration fails
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409

    # 3. Login with correct password
    login_payload = {
        "email": unique_email,
        "password": "securepassword123"
    }
    login_res = client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 4. Login with wrong password
    bad_login = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "wrongpassword"
    })
    assert bad_login.status_code == 401

    # 5. Access /api/v1/auth/me with Bearer token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email

    # 6. Access /api/v1/auth/me without token fails
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401
