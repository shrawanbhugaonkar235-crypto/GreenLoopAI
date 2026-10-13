import io
import uuid
from PIL import Image, ImageDraw

def create_sample_image(text="Plastic Bottle"):
    img = Image.new("RGB", (320, 240), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 270, 190], fill=(76, 175, 80), outline=(0, 0, 0))
    draw.text((70, 90), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def test_verify_waste_flow(client):
    unique_email = f"citizen_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/v1/auth/register", json={
        "name": "Pooja Patel",
        "email": unique_email,
        "password": "mypassword123"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Verification with invalid file extension fails
    bad_file = io.BytesIO(b"fake txt content")
    res_bad = client.post(
        "/api/v1/verify",
        headers=headers,
        files={"image": ("sample.txt", bad_file, "text/plain")}
    )
    assert res_bad.status_code == 400

    # 2. Verification with valid JPEG image
    img_buf = create_sample_image("Coca-Cola PET bottle")
    res_verify = client.post(
        "/api/v1/verify",
        headers=headers,
        files={"image": ("bottle.jpg", img_buf, "image/jpeg")}
    )
    assert res_verify.status_code == 200
    data = res_verify.json()
    assert "id" in data
    assert data["file_name"] == "bottle.jpg"
    assert "score" in data
    assert "breakdown" in data
    assert "status" in data
    assert "balance" in data
    assert data["status"] in ("verified", "rejected")

    # 3. Unauthorized request fails
    res_unauth = client.post(
        "/api/v1/verify",
        files={"image": ("bottle.jpg", create_sample_image(), "image/jpeg")}
    )
    assert res_unauth.status_code == 401
