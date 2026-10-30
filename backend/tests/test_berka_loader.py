import csv
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import create_tables
from app.models import Account, Transaction, User
from scripts.load_berka import (
    category_for,
    last_balances,
    load_berka_database,
    select_account_ids,
    signed_amount,
)


def test_berka_category_mapping():
    assert category_for("VYBER", "", "-100") == "Cash Withdrawal"
    assert category_for("", "UVER", "-100") == "EMI/Loan"
    assert category_for("", "POJISTNE", "-100") == "Insurance"
    assert category_for("", "SIPO", "-100") == "Utilities"
    assert category_for("", "SANKCE", "-100") == "Fees and Charges"
    assert category_for("VKLAD", "", "100") == "Other Income"
    assert category_for("UNKNOWN", "UNKNOWN", "-100") == "Uncategorised"
    assert signed_amount({"amount": "100", "type": "PRIJEM"}) == "100.0"
    assert signed_amount({"amount": "100", "type": "VYDAJ"}) == "-100.0"


def test_berka_sign_regression_uses_source_type_for_debit_credit_direction():
    assert signed_amount({"amount": "100", "type": "PRIJEM"}) == "100.0"
    assert signed_amount({"amount": "100", "type": "VYDAJ"}) == "-100.0"


def test_berka_uses_last_running_balance_per_account(tmp_path: Path):
    path = tmp_path / "trans.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["trans_id", "account_id", "date", "operation", "amount", "balance", "type", "k_symbol"],
        )
        writer.writeheader()
        writer.writerows(
            [
                {"trans_id": "1", "account_id": "a", "date": "1995-01-01", "operation": "VKLAD", "amount": "100", "balance": "100", "type": "PRIJEM", "k_symbol": ""},
                {"trans_id": "2", "account_id": "a", "date": "1995-02-01", "operation": "VYDAJ", "amount": "20", "balance": "80", "type": "VYDAJ", "k_symbol": ""},
            ]
        )
    assert last_balances(path, {"a"}) == {"a": 8_000}


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
        assert session.query(Transaction).first().category == "Other Income"
