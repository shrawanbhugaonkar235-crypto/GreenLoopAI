import io
import uuid
from PIL import Image

def sample_image():
    img = Image.new("RGB", (200, 200), color=(100, 200, 100))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def test_greencoins_and_history_isolation(client):
    # Citizen 1
    email1 = f"user1_{uuid.uuid4().hex[:6]}@example.com"
    reg1 = client.post("/api/v1/auth/register", json={"name": "User One", "email": email1, "password": "pass123456"})
    token1 = reg1.json()["access_token"]
    h1 = {"Authorization": f"Bearer {token1}"}

    # Citizen 2
    email2 = f"user2_{uuid.uuid4().hex[:6]}@example.com"
    reg2 = client.post("/api/v1/auth/register", json={"name": "User Two", "email": email2, "password": "pass123456"})
    token2 = reg2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {token2}"}

    # Initial balance for citizen 1 should be 0
    bal_res1 = client.get("/api/v1/greencoins/balance", headers=h1)
    assert bal_res1.status_code == 200
    assert bal_res1.json()["balance"] == 0

    # Submit verification for citizen 1
    v_res = client.post("/api/v1/verify", headers=h1, files={"image": ("plastic.jpg", sample_image(), "image/jpeg")})
    assert v_res.status_code == 200
    v_id = v_res.json()["id"]

    # History for citizen 1 contains 1 item
    hist1 = client.get("/api/v1/history", headers=h1)
    assert hist1.status_code == 200
    assert len(hist1.json()) >= 1
    assert hist1.json()[0]["id"] == v_id

    # History for citizen 2 must be EMPTY (isolation)
    hist2 = client.get("/api/v1/history", headers=h2)
    assert hist2.status_code == 200
    assert len(hist2.json()) == 0

    # Detail query: citizen 1 can access
    detail1 = client.get(f"/api/v1/history/{v_id}", headers=h1)
    assert detail1.status_code == 200
    assert detail1.json()["id"] == v_id

    # Detail query: citizen 2 cannot access (404)
    detail2 = client.get(f"/api/v1/history/{v_id}", headers=h2)
    assert detail2.status_code == 404

    # Transactions endpoint for citizen 1
    txs = client.get("/api/v1/greencoins/transactions", headers=h1)
    assert txs.status_code == 200
    assert isinstance(txs.json(), list)
