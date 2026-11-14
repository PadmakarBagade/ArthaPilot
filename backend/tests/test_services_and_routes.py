"""Unit tests for services, finance defs, evidence resolver, and new Master Plan routes."""

from fastapi.testclient import TestClient

from app.finance.defs import (
    is_expense,
    is_income,
    liquid_balance_paise,
    monthly_debt_service_paise,
)
from app.main import app
from app.services import build_user_state, list_demo_personas


def test_ready_endpoint():
    client = TestClient(app)
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_demo_personas_endpoint():
    client = TestClient(app)
    resp = client.get("/demo/personas")
    assert resp.status_code == 200
    personas = resp.json()
    assert len(personas) >= 5
    ids = [p["id"] for p in personas]
    assert "rahul" in ids
    assert "priya" in ids


def test_finance_definitions():
    # Income & Expense tests
    assert is_income("Salary", 5000000) is True
    assert is_income("Other Income", 100000) is True
    assert is_income("Food Delivery", -50000) is False

    assert is_expense("Groceries", -250000) is True
    assert is_expense("Transfers", -50000, is_self_transfer=True) is False
    assert is_expense("Salary", 5000000) is False

    # Liquid balance tests (DEC-10: savings & current only)
    accounts = [
        {"type": "savings", "balance_paise": 5000000},
        {"type": "current", "balance_paise": 1000000},
        {"type": "credit", "balance_paise": 8000000},  # Never liquid
    ]
    assert liquid_balance_paise(accounts) == 6000000

    # Monthly debt service tests (F5)
    loans = [{"emi_paise": 1500000}]
    cards = [{"min_due_paise": 250000}]
    assert monthly_debt_service_paise(loans, cards) == 1750000


def test_overview_endpoint():
    client = TestClient(app)
    # Ensure rahul is loaded
    client.post("/users/rahul/load-persona")
    client.post("/users/rahul/process")

    resp = client.get("/users/rahul/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "rahul"
    assert "health" in data
    assert "confidence" in data
    assert "liquid_balance_paise" in data
    assert "debt_service_paise" in data


def test_spending_endpoint():
    client = TestClient(app)
    resp = client.get("/users/rahul/spending")
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == "rahul"
    assert "by_category" in data
    assert "by_month" in data
    assert data["total_spend_paise"] > 0


def test_add_expense_and_snapshots():
    client = TestClient(app)
    resp = client.post(
        "/users/rahul/expenses",
        json={"amount_paise": 500000, "category": "Shopping", "description": "New Headphones"},
    )
    assert resp.status_code == 200
    txn = resp.json()
    assert txn["amount_paise"] == -500000

    # Check snapshots
    snap_resp = client.get("/users/rahul/snapshots")
    assert snap_resp.status_code == 200
    snaps = snap_resp.json()
    assert len(snaps) >= 1


def test_evidence_endpoint():
    client = TestClient(app)
    resp = client.get("/users/rahul/evidence?ids=savings_rate,debt_to_income")
    assert resp.status_code == 200
    data = resp.json()
    assert "formulas" in data
    assert "savings_rate" in data["formulas"]
    assert "debt_to_income" in data["formulas"]


def test_validation_endpoint():
    client = TestClient(app)
    resp = client.get("/validation")
    assert resp.status_code == 200
    data = resp.json()
    assert "framework" in data

