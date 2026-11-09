import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_auth_register_and_login_flow():
    # Register a new user with unique email
    email = f"test.{uuid.uuid4().hex[:8]}@example.com"
    password = "secretpassword123"
    reg_res = client.post(
        "/auth/register",
        json={"name": "Test User", "email": email, "password": password},
    )
    assert reg_res.status_code == 200, reg_res.text
    data = reg_res.json()
    assert "token" in data
    assert data["user"]["email"] == email
    token = data["token"]

    # Verify /auth/me with Bearer token
    me_res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # Duplicate register should fail
    dup_res = client.post(
        "/auth/register",
        json={"name": "Duplicate User", "email": email, "password": password},
    )
    assert dup_res.status_code == 400

    # Login with valid credentials
    login_res = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_res.status_code == 200
    assert "token" in login_res.json()

    # Login with bad password should fail
    bad_login = client.post(
        "/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert bad_login.status_code == 401

    # Logout
    logout_res = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout_res.status_code == 200
    assert logout_res.json()["status"] == "logged_out"


def test_demo_login():
    res = client.post("/auth/demo-login/rahul")
    assert res.status_code == 200
    data = res.json()
    assert "token" in data
    assert data["user"]["id"] == "rahul"


def test_cards_and_investments_endpoints():
    client.post("/users/rahul/load-persona")
    cards_res = client.get("/users/rahul/cards")
    assert cards_res.status_code == 200
    assert isinstance(cards_res.json(), list)

    inv_res = client.get("/users/rahul/investments")
    assert inv_res.status_code == 200
    assert isinstance(inv_res.json(), list)

    # Add new investment
    new_inv = client.post(
        "/users/rahul/investments",
        json={"type": "Gold ETF", "value_paise": 2500000, "monthly_sip_paise": 200000},
    )
    assert new_inv.status_code == 200
    assert new_inv.json()["type"] == "Gold ETF"
    assert new_inv.json()["value_paise"] == 2500000
