import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

@pytest.fixture
def auth_headers():
    unique = uuid.uuid4().hex[:8]
    email = f"party_tester_{unique}@example.com"
    res = client.post("/api/register", json={
        "name": "Party Tester",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_party_planner_valid_generation(auth_headers):
    payload = {
        "budget": 50000,
        "currency": "INR",
        "event_type": "Birthday",
        "guest_count": 50,
        "event_date": "2026-11-20",
        "venue_type": "Hall",
        "location": "Bengaluru",
        "catering_preference": "Vegetarian",
        "decoration_level": "Standard",
        "entertainment": "Music",
        "need_accommodation": True,
        "room_count": 2,
        "additional_requirements": "Cake cutting table"
    }

    res = client.post("/api/generate-party", json=payload, headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    plan = data["data"]
    assert plan["budget"] == 50000
    assert plan["estimated_total"] <= 50000
    assert plan["remaining_budget"] >= 0
    assert "Accommodation" in plan["allocated_budget"]

def test_party_planner_invalid_guests(auth_headers):
    payload = {
        "budget": 50000,
        "event_type": "Birthday",
        "guest_count": 0  # Invalid
    }
    res = client.post("/api/generate-party", json=payload, headers=auth_headers)
    assert res.status_code == 422 or res.status_code == 400
