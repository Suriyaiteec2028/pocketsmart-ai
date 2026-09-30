import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

import uuid

@pytest.fixture
def auth_headers():
    unique = uuid.uuid4().hex[:8]
    email = f"jewelry_tester_{unique}@example.com"
    res = client.post("/api/register", json={
        "name": "Jewelry Tester",
        "email": email,
        "password": "Password123!",
        "confirm_password": "Password123!"
    })
    token = res.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_jewelry_image_upload_and_generation(auth_headers):
    # 1. Create a dummy test image in memory
    img = Image.new("RGB", (100, 100), color=(10, 25, 120))  # Royal Blue
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    # Upload image
    files = {"file": ("test_outfit.jpg", img_bytes, "image/jpeg")}
    upload_res = client.post("/api/upload-image", files=files, headers=auth_headers)
    assert upload_res.status_code == 200
    upload_data = upload_res.json()
    assert upload_data["success"] is True
    image_url = upload_data["data"]["image_url"]

    # 2. Plan with uploaded image
    payload = {
        "budget": 5000,
        "currency": "INR",
        "occasion": "Wedding",
        "jewelry_type": "Earrings",
        "preferred_style": "Elegant",
        "preferred_material": "Silver",
        "preferred_color": "Silver",
        "outfit_description": "Navy blue saree with silver border",
        "image_url": image_url
    }

    gen_res = client.post("/api/generate-jewelry", json=payload, headers=auth_headers)
    assert gen_res.status_code == 200
    data = gen_res.json()
    assert data["success"] is True
    plan = data["data"]
    assert plan["budget"] == 5000
    assert plan["estimated_total"] <= 5000
    assert "outfit_analysis" in plan
    assert len(plan["outfit_analysis"]["dominant_colors"]) > 0

def test_jewelry_invalid_image_upload(auth_headers):
    # Try uploading non-image file
    fake_file = io.BytesIO(b"this is a text file pretending to be an exe")
    files = {"file": ("script.exe", fake_file, "application/octet-stream")}
    res = client.post("/api/upload-image", files=files, headers=auth_headers)
    assert res.status_code == 400
