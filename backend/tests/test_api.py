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
