"""Load a representative slice of Berka into ArthaPilot.

Berka is a Czech banking dataset whose amounts are in the source currency
(Czech koruna), not rupees. We preserve the source unit but store each value
as integer "paise-like" subunits (amount * 100) so the canonical money type
remains an integer. These values must not be presented as Indian rupees.
"""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from app.ingestion.cleaning import clean_transactions
from app.models import Account, Transaction, User


DEFAULT_ACCOUNT_LIMIT = 20
MIN_MONTHS = 12

CATEGORY_BY_CODE = {
    "SIPO": "household",
    "POJISTNE": "insurance",
    "SANKCE": "fees",
    "UVER": "loan_payment",
    "DUCHOD": "income",
    "懒": "other",
}

OPERATION_CATEGORY = {
    "VYBER": "cash_withdrawal",
    "VKLAD": "deposit",
    "PREVOD Z UCTU": "transfer",
    "PREVOD NA UCET": "transfer",
    "VYBER KARTOU": "card_payment",
}


def category_for(operation: str, k_symbol: str) -> str:
    return CATEGORY_BY_CODE.get(k_symbol, OPERATION_CATEGORY.get(operation, "other"))


def _read_transactions(path: Path) -> Iterable[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        yield from csv.DictReader(handle)


def select_account_ids(
    path: Path, limit: int = DEFAULT_ACCOUNT_LIMIT, minimum_months: int = MIN_MONTHS
) -> list[str]:
    months_by_account: defaultdict[str, set[str]] = defaultdict(set)
    for row in _read_transactions(path):
        months_by_account[row["account_id"]].add(row["date"][:7])
    eligible = sorted(
        account_id
        for account_id, months in months_by_account.items()
        if len(months) >= minimum_months
    )
    if len(eligible) < limit:
        raise ValueError(
            f"Berka contains only {len(eligible)} accounts with {minimum_months}+ months"
        )
    return eligible[:limit]


def load_berka_rows(
    path: Path,
    user_id: str = "berka",
    account_ids: set[str] | None = None,
) -> list[dict]:
    selected = account_ids or set(select_account_ids(path, limit=1))
    converted: list[dict] = []
    for row in _read_transactions(path):
        if row["account_id"] not in selected:
            continue
        converted.append(
            {
                "trans_id": f"berka-{row['trans_id']}",
                "account_id": f"berka-{row['account_id']}",
                "date": row["date"],
                "amount": row["amount"],
                "description": " ".join(
                    value
                    for value in (row.get("operation", ""), row.get("k_symbol", ""))
                    if value
                )
                or row.get("type", "Berka transaction"),
                "category": category_for(
                    row.get("operation", ""), row.get("k_symbol", "")
                ),
            }
        )
    cleaned = clean_transactions(converted, user_id=user_id, source="berka")
    for transaction, row in zip(cleaned, converted):
        transaction["category"] = row["category"]
    return cleaned


def load_berka_database(
    db,
    trans_path: Path,
    account_limit: int = DEFAULT_ACCOUNT_LIMIT,
) -> int:
    selected = set(select_account_ids(trans_path, limit=account_limit))
    account_rows = {
        row["account_id"]: row
        for row in _read_transactions(trans_path)
        if row["account_id"] in selected
    }
    users = {
        f"berka-{account_id}": User(
            id=f"berka-{account_id}",
            name=f"Berka account {account_id}",
            source="berka",
        )
        for account_id in selected
    }
    db.add_all(users.values())
    db.add_all(
        Account(
            id=f"berka-{account_id}",
            user_id=f"berka-{account_id}",
            type="savings",
            institution="Berka (Czech koruna source data)",
            balance_paise=round(float(row["balance"]) * 100),
        )
        for account_id, row in account_rows.items()
    )
    rows_by_account: defaultdict[str, list[dict]] = defaultdict(list)
    for row in _read_transactions(trans_path):
        if row["account_id"] in selected:
            rows_by_account[row["account_id"]].append(row)
    for account_id, rows in rows_by_account.items():
        converted = [
            {
                "trans_id": f"berka-{row['trans_id']}",
                "account_id": f"berka-{row['account_id']}",
                "date": row["date"],
                "amount": row["amount"],
                "description": " ".join(
                    value
                    for value in (row.get("operation", ""), row.get("k_symbol", ""))
                    if value
                )
                or row.get("type", "Berka transaction"),
                "category": category_for(
                    row.get("operation", ""), row.get("k_symbol", "")
                ),
            }
            for row in rows
        ]
        transactions = clean_transactions(
            converted, user_id=f"berka-{account_id}", source="berka"
        )
        for transaction, row in zip(transactions, converted):
            transaction["category"] = row["category"]
            db.add(Transaction(**transaction))
    db.commit()
    return len(selected)


if __name__ == "__main__":
    from app.db import SessionLocal, create_tables

    create_tables()
    with SessionLocal() as session:
        print(load_berka_database(session, Path("data/berka/trans.csv")))
