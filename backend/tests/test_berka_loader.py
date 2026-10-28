import csv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import create_tables
from app.models import Account, Transaction, User
from scripts.load_berka import category_for, load_berka_database, select_account_ids


def test_berka_category_mapping():
    assert category_for("VYBER", "") == "cash_withdrawal"
    assert category_for("", "UVER") == "loan_payment"
    assert category_for("UNKNOWN", "UNKNOWN") == "other"


def test_select_accounts_requires_twelve_months(tmp_path: Path):
    path = tmp_path / "trans.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["trans_id", "account_id", "date", "operation", "amount", "k_symbol"],
        )
        writer.writeheader()
        for month in range(12):
            writer.writerow(
                {
                    "trans_id": month,
                    "account_id": "1",
                    "date": f"1995-{month + 1:02d}-01",
                    "operation": "VKLAD",
                    "amount": "100",
                    "k_symbol": "",
                }
            )
        writer.writerow(
            {
                "trans_id": "short",
                "account_id": "2",
                "date": "1995-01-01",
                "operation": "VKLAD",
                "amount": "100",
                "k_symbol": "",
            }
        )

    assert select_account_ids(path, limit=1) == ["1"]


def test_berka_loader_persists_users_accounts_and_transactions(tmp_path: Path):
    path = tmp_path / "trans.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["trans_id", "account_id", "date", "operation", "amount", "k_symbol", "balance"],
        )
        writer.writeheader()
        for account_id in ("1", "2"):
            for month in range(12):
                writer.writerow(
                    {
                        "trans_id": f"{account_id}-{month}",
                        "account_id": account_id,
                        "date": f"1995-{month + 1:02d}-01",
                        "operation": "VKLAD",
                        "amount": "100",
                        "k_symbol": "",
                        "balance": "100",
                    }
                )

    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)
    with Session(engine) as session:
        assert load_berka_database(session, path, account_limit=2) == 2
        assert session.query(User).filter_by(source="berka").count() == 2
        assert session.query(Account).count() == 2
        assert session.query(Transaction).count() == 24
        assert session.query(Transaction).first().category == "deposit"
