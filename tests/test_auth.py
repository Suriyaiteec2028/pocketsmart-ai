import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

def test_registration_and_duplicate_handling():
    unique = uuid.uuid4().hex[:8]
    unique_email = f"testuser_{unique}@example.com"
    payload = {
        "name": "Test User",
        "email": unique_email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    }
    
    # 1. Successful registration
    res1 = client.post("/api/register", json=payload)
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["success"] is True
    assert "access_token" in data1["data"]

    # 2. Duplicate registration attempt
    res2 = client.post("/api/register", json=payload)
    assert res2.status_code == 400
    data2 = res2.json()
    assert "already exists" in data2["detail"]

def test_login_success_and_failure():
    unique = uuid.uuid4().hex[:8]
    email = f"logintest_{unique}@example.com"
    # Register first
    client.post("/api/register", json={
        "name": "Login Tester",
        "email": email,
        "password": "SecretPassword123",
        "confirm_password": "SecretPassword123"
    })

    # Successful login
    res_ok = client.post("/api/login", json={
        "email": email,
        "password": "SecretPassword123"
    })
    assert res_ok.status_code == 200
    assert res_ok.json()["success"] is True
    assert "access_token" in res_ok.json()["data"]

    # Failed login: wrong password
    res_fail = client.post("/api/login", json={
        "email": email,
        "password": "WrongPassword123"
    })
    assert res_fail.status_code == 401

def test_protected_route_and_logout():
    # Clear any residual cookies from previous tests
    client.cookies.clear()
    # Attempting to access protected session without auth
    res_unauth = client.get("/api/session-info")
    assert res_unauth.status_code == 401

    # Register and obtain token
    u = uuid.uuid4().hex[:8]
    email = f"sessiontester_{u}@example.com"
    res_reg = client.post("/api/register", json={
        "name": "Session Tester",
        "email": email,
        "password": "SecurePassword999",
        "confirm_password": "SecurePassword999"
    })
    token = res_reg.json()["data"]["access_token"]

    # Access with Authorization header
    headers = {"Authorization": f"Bearer {token}"}
    res_auth = client.get("/api/session-info", headers=headers)
    assert res_auth.status_code == 200
    assert res_auth.json()["data"]["email"] == email

    # Logout
    res_logout = client.post("/api/logout")
    assert res_logout.status_code == 200
