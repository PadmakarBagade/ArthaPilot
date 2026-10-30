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
    "SIPO": "Utilities",
    "POJISTNE": "Insurance",
    "SANKCE": "Fees and Charges",
    "UVER": "EMI/Loan",
    "LEASING": "EMI/Loan",
}

OPERATION_CATEGORY = {
    "VYBER": "Cash Withdrawal",
    "PREVOD Z UCTU": "Transfers",
    "PREVOD NA UCET": "Transfers",
    "VYBER KARTOU": "Credit Card Payment",
}


def category_for(operation: str, k_symbol: str, amount: str | float | None = None) -> str:
    """Map Berka codes to canonical categories; credits are always Other Income."""
    if amount is not None and float(amount) > 0:
        return "Other Income"
    if k_symbol in CATEGORY_BY_CODE:
        return CATEGORY_BY_CODE[k_symbol]
    if operation in OPERATION_CATEGORY:
        return OPERATION_CATEGORY[operation]
    return "Uncategorised"


def signed_amount(row: dict[str, str]) -> str:
    amount = abs(float(row["amount"]))
    if row.get("type", "").upper() in {"VYDAJ", "VYBER"}:
        return str(-amount)
    return str(amount)


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


def last_balances(path: Path, account_ids: set[str]) -> dict[str, int]:
    balances: dict[str, int] = {}
    for row in _read_transactions(path):
        if row["account_id"] in account_ids:
            balances[row["account_id"]] = round(float(row["balance"]) * 100)
    return balances


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
                "amount": signed_amount(row),
                "description": " ".join(
                    value
                    for value in (row.get("operation", ""), row.get("k_symbol", ""))
                    if value
                )
                or row.get("type", "Berka transaction"),
                "category": category_for(
                    row.get("operation", ""), row.get("k_symbol", ""), signed_amount(row)
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
    balances = last_balances(trans_path, selected)
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
            balance_paise=balances[account_id],
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
                "amount": signed_amount(row),
                "description": " ".join(
                    value
                    for value in (row.get("operation", ""), row.get("k_symbol", ""))
                    if value
                )
                or row.get("type", "Berka transaction"),
                "category": category_for(
                    row.get("operation", ""), row.get("k_symbol", ""), signed_amount(row)
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
