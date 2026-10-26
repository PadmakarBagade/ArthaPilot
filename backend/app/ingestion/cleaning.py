from datetime import date, datetime
import hashlib
import re
from typing import Iterable


def _first(row: dict, names: tuple[str, ...]) -> str:
    lowered = {str(key).strip().lower(): value for key, value in row.items()}
    for name in names:
        if name in lowered and str(lowered[name]).strip():
            return str(lowered[name]).strip()
    return ""


def _parse_date(value: str) -> date:
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value.strip(), pattern).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid transaction date: {value}")


def _amount_paise(row: dict) -> int:
    amount = _first(row, ("amount_paise",))
    if amount:
        return int(float(amount))
    amount = _first(row, ("amount", "value", "transaction amount"))
    debit = _first(row, ("debit", "withdrawal", "debit amount"))
    credit = _first(row, ("credit", "deposit", "credit amount"))
    if debit or credit:
        if debit:
            return -round(float(debit.replace(",", "").replace("₹", "")) * 100)
        return round(float(credit.replace(",", "").replace("₹", "")) * 100)
    if not amount:
        raise ValueError("Transaction row has no amount")
    return round(float(amount.replace(",", "").replace("₹", "")) * 100)


def clean_transactions(
    rows: Iterable[dict], user_id: str, source: str = "real"
) -> list[dict]:
    cleaned: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        transaction_date = _parse_date(_first(row, ("date", "transaction date", "txn_date")))
        description = _first(row, ("raw_description", "description", "narration", "details"))
        account_id = _first(row, ("account_id", "account", "account number")) or "default"
        amount_paise = _amount_paise(row)
        txn_id = _first(row, ("txn_id", "transaction id", "trans_id"))
        if not txn_id:
            digest = f"{transaction_date.isoformat()}|{amount_paise}|{description}|{account_id}"
            txn_id = hashlib.sha256(digest.encode()).hexdigest()[:32]
        if txn_id in seen:
            continue
        seen.add(txn_id)
        merchant = re.split(r"[/*|]", description, maxsplit=1)[0].strip()
        cleaned.append(
            {
                "txn_id": txn_id,
                "user_id": user_id,
                "account_id": account_id,
                "date": transaction_date,
                "amount_paise": amount_paise,
                "raw_description": description,
                "merchant": merchant,
                "category": _first(row, ("category",)),
                "category_confidence": 0.0,
                "is_recurring": False,
                "source": source,
            }
        )
    return cleaned
