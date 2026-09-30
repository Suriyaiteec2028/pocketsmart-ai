import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

def test_history_flow_and_user_isolation():
    u = uuid.uuid4().hex[:8]
    # User A
    user_a_res = client.post("/api/register", json={
        "name": "User Alpha",
        "email": f"alpha_hist_{u}@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    token_a = user_a_res.json()["data"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # User B
    user_b_res = client.post("/api/register", json={
        "name": "User Beta",
        "email": f"beta_hist_{u}@example.com",
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    token_b = user_b_res.json()["data"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 1. User A creates a home plan
    plan_res = client.post("/api/generate-home", json={
        "budget": 75000,
        "rooms": ["Living Room"],
        "home_type": "Apartment",
        "overall_style": "Modern"
    }, headers=headers_a)
    assert plan_res.status_code == 200
    plan_id = plan_res.json()["data"]["plan_id"]

    # 2. User A retrieves history
    hist_a = client.get("/api/history", headers=headers_a)
    assert hist_a.status_code == 200
    plans = hist_a.json()["data"]["plans"]
    assert any(p["id"] == plan_id for p in plans)

    # 3. User B attempts to access User A's plan -> Must be 404/Denied
    unauthorized_res = client.get(f"/api/recommendations/{plan_id}", headers=headers_b)
    assert unauthorized_res.status_code == 404

    # 4. User A saves an individual item
    save_res = client.post(f"/api/recommendations/{plan_id}/save", json={
        "item_name": "Modern Fabric Sofa",
        "item_category": "Sofa",
        "platform": "Amazon",
        "estimated_price": 22000,
        "recommendation_data": {"style": "Modern"}
    }, headers=headers_a)
    assert save_res.status_code == 200
    assert save_res.json()["data"]["saved"] is True

    # 5. User A reuses the plan
    reuse_res = client.post(f"/api/recommendations/{plan_id}/reuse", headers=headers_a)
    assert reuse_res.status_code == 200
    reuse_data = reuse_res.json()["data"]
    assert reuse_data["planner_type"] == "home"
    assert reuse_data["input_data"]["budget"] == 75000

    # 6. User A deletes the plan
    del_res = client.delete(f"/api/history/{plan_id}", headers=headers_a)
    assert del_res.status_code == 200

    # 7. Verify plan no longer exists
    check_del = client.get(f"/api/recommendations/{plan_id}", headers=headers_a)
    assert check_del.status_code == 404
