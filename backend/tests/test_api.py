from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app


def test_upload_csv():
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={
            "file": (
                "sample.csv",
                BytesIO(b"date,amount,description,account_id\n2024-01-01,10,Salary,a1\n"),
                "text/csv",
            )
        },
    )
    assert response.status_code == 200
    assert response.json()["transactions_loaded"] == 1


def test_upload_returns_column_mapping_when_required_columns_are_missing():
    client = TestClient(app)
    response = client.post(
        "/upload",
        files={"file": ("unknown.csv", b"when,notes\n2024-01-01,Salary\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "column_mapping_required",
        "mapping": {
            "required": ["date", "amount or debit/credit"],
            "detected": ["notes", "when"],
        },
    }


def test_upload_rejects_unsupported_extension():
    response = TestClient(app).post(
        "/upload",
        files={"file": ("statement.txt", b"date,amount\n2024-01-01,1\n", "text/plain")},
    )

    assert response.status_code == 415


def test_upload_enforces_size_limit():
    response = TestClient(app).post(
        "/upload",
        files={
            "file": (
                "large.csv",
                b"x" * (10 * 1024 * 1024 + 1),
                "text/csv",
            )
        },
    )

    assert response.status_code == 413


def test_load_rahul_persona():
    response = TestClient(app).post("/users/rahul/load-persona")

    assert response.status_code == 200
    assert response.json()["transactions_loaded"] > 0
    users = TestClient(app).get("/users")
    assert users.status_code == 200
    assert any(user["id"] == "rahul" for user in users.json())


def test_load_persona_imports_story_accounts_cards_and_loans():
    response = TestClient(app).post("/users/priya/load-persona")
    assert response.status_code == 200
    from app.db import SessionLocal
    from app.models import Account, Card, Loan

    with SessionLocal() as session:
        assert session.query(Account).filter_by(user_id="priya").count() == 2
        assert session.query(Card).filter_by(user_id="priya").count() == 1
        assert session.query(Loan).filter_by(user_id="priya").count() == 1


def test_transactions_endpoint_supports_category_filter():
    client = TestClient(app)
    client.post("/users/rahul/load-persona")
    response = client.get("/users/rahul/transactions", params={"category": "Salary"})
    assert response.status_code == 200
    if response.json():
        assert all(item["category"] == "Salary" for item in response.json())
    assert client.get("/users/rahul/transactions").json()


def test_what_changed_records_an_emi_scenario():
    client = TestClient(app)
    client.post("/users/rahul/load-persona")
    before = client.get("/users/rahul/what-changed")
    assert before.status_code == 200
    assert before.json()["snapshot_id"] is None
    response = client.post(
        "/users/rahul/loans",
        json={"outstanding_paise": 1200000, "emi_paise": 120000, "type": "Scenario EMI"},
    )
    assert response.status_code == 200
    after = client.get("/users/rahul/what-changed")
    assert after.status_code == 200
    assert after.json()["snapshot_id"]


def test_insights_endpoint():
    client = TestClient(app)
    client.post("/users/rahul/load-persona")
    response = client.get("/users/rahul/insights")
    assert response.status_code == 200
    insights = response.json()
    assert isinstance(insights, list)


def test_debt_payoff_endpoint():
    client = TestClient(app)
    client.post("/users/rahul/load-persona")
    response = client.post(
        "/users/rahul/debt-payoff",
        json={"extra_monthly_paise": 500000, "strategy": "avalanche"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["strategy"] == "avalanche"
    assert "months_saved" in data
    assert "interest_saved_paise" in data

