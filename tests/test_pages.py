import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def create_authenticated_session():
    """Helper to create a user, log in, and return client with cookie."""
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = "password123"
    name = "Test User"
    
    reg_res = client.post("/api/register", json={
        "name": name,
        "email": unique_email,
        "password": password,
        "confirm_password": password
    })
    assert reg_res.status_code == 200
    token = reg_res.json()["data"]["access_token"]
    return token, unique_email

def test_public_pages_render():
    """Verify that public pages render with public navbar."""
    client.cookies.clear()
    
    # 1. Landing page
    res_index = client.get("/")
    assert res_index.status_code == 200
    assert "public-navbar" in res_index.text
    assert "Start Planning" in res_index.text
    
    # 2. Login page
    res_login = client.get("/login")
    assert res_login.status_code == 200
    assert "public-navbar" in res_login.text
    assert "Sign In" in res_login.text
    
    # 3. Register page
    res_reg = client.get("/register")
    assert res_reg.status_code == 200
    assert "public-navbar" in res_reg.text
    assert "Create Account" in res_reg.text
    
    # 4. Testimonials page
    res_testim = client.get("/testimonials")
    assert res_testim.status_code == 200
    assert "public-navbar" in res_testim.text

def test_protected_pages_redirect_unauthenticated():
    """Unauthenticated access to app pages should redirect to login."""
    client.cookies.clear()
    protected_paths = [
        "/dashboard",
        "/home-planner",
        "/party-planner",
        "/jewelry-planner",
        "/history",
        "/saved",
        "/profile",
        "/settings"
    ]
    for path in protected_paths:
        res = client.get(path, follow_redirects=False)
        assert res.status_code in (302, 307), f"Expected redirect on {path}, got {res.status_code}"
        assert "/login" in res.headers["location"]

def test_authenticated_layout_and_sidebar():
    """Authenticated user sees sidebar layout and new pages."""
    token, email = create_authenticated_session()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Dashboard
    res_dash = client.get("/dashboard", headers=headers)
    assert res_dash.status_code == 200
    assert "app-sidebar" in res_dash.text
    assert "app-top-header" in res_dash.text
    assert "Home Interior" in res_dash.text
    assert "Party &amp; Event" in res_dash.text or "Party & Event" in res_dash.text
    assert "Jewelry &amp; Outfit" in res_dash.text or "Jewelry & Outfit" in res_dash.text
    
    # 2. Saved page
    res_saved = client.get("/saved", headers=headers)
    assert res_saved.status_code == 200
    assert "app-sidebar" in res_saved.text
    assert "Saved Recommendations" in res_saved.text
    
    # 3. Profile page
    res_profile = client.get("/profile", headers=headers)
    assert res_profile.status_code == 200
    assert "app-sidebar" in res_profile.text
    assert "Personal Details" in res_profile.text
    
    # 4. Settings page
    res_settings = client.get("/settings", headers=headers)
    assert res_settings.status_code == 200
    assert "app-sidebar" in res_settings.text
    assert "Application Preferences" in res_settings.text

def test_update_profile_api():
    """Verify PUT /api/profile endpoint."""
    token, email = create_authenticated_session()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Update name
    update_res = client.put("/api/profile", json={"name": "Updated Name"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["data"]["name"] == "Updated Name"
    
    # 2. Update password with wrong current password
    fail_res = client.put("/api/profile", json={
        "current_password": "wrongpassword",
        "new_password": "newpassword123"
    }, headers=headers)
    assert fail_res.status_code == 400
    
    # 3. Update password with correct current password
    succ_res = client.put("/api/profile", json={
        "current_password": "password123",
        "new_password": "newpassword123"
    }, headers=headers)
    assert succ_res.status_code == 200
