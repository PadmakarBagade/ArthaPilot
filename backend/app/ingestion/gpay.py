import csv
from pathlib import Path

from .cleaning import clean_transactions


def load_gpay_csv(path: str | Path, user_id: str) -> list[dict]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    cleaned = clean_transactions(rows, user_id=user_id, source="real")
    for transaction, row in zip(cleaned, rows):
        transaction["is_self_transfer"] = str(row.get("is_self_transfer", "")).lower() == "true"
        transaction["account_id"] = row.get("bank_account") or transaction["account_id"]
    return cleaned
