from fastapi.testclient import TestClient

from server.main import app


client = TestClient(app)


def test_register_login_me_and_protected_routes():
    # Register
    r = client.post("/common/auth/register", json={"email": "user@example.com", "password": "secret123"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["email"] == "user@example.com"
    assert "user" in data["roles"]

    # Login
    r = client.post("/common/auth/login", data={"username": "user@example.com", "password": "secret123"})
    assert r.status_code == 200, r.text
    tokens = r.json()
    assert tokens["access_token"] and tokens["refresh_token"]

    # Me
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    r = client.get("/common/auth/me", headers=headers)
    assert r.status_code == 200, r.text

    # Analytics protected requires analyst/admin role
    r = client.post("/yutotkg/analytics/events", headers=headers)
    assert r.status_code == 403

    # Billing protected requires billing/admin role
    r = client.get("/common/payments/invoices", headers=headers)
    assert r.status_code == 403
