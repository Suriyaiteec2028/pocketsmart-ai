import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

@pytest.fixture
def auth_headers():
    unique = uuid.uuid4().hex[:8]
    email = f"home_tester_{unique}@example.com"
    res = client.post("/api/register", json={
        "name": "Home Tester",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_home_planner_valid_generation(auth_headers):
    payload = {
        "budget": 100000,
        "currency": "INR",
        "home_type": "Apartment",
        "rooms": ["Living Room", "Bedroom"],
        "overall_style": "Modern",
        "budget_allocation_preference": "Balanced",
        "additional_requirements": "Spacious seating with warm lighting"
    }

    res = client.post("/api/generate-home", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    plan = data["data"]
    assert plan["budget"] == 100000
    assert plan["estimated_total"] <= 100000
    assert plan["remaining_budget"] >= 0
    assert len(plan["recommendations"]) > 0

def test_home_planner_invalid_budget(auth_headers):
    payload = {
        "budget": -500,
        "currency": "INR",
        "home_type": "Apartment",
        "rooms": ["Living Room"]
    }
    res = client.post("/api/generate-home", json=payload, headers=auth_headers)
    assert res.status_code == 422 or res.status_code == 400
