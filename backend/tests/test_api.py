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
