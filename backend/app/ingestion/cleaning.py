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
    value = value.strip()
    for pattern in (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%m/%d/%Y",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        pass
    raise ValueError(f"Invalid transaction date: {value}")


def _number(value: str) -> float:
    normalized = value.strip().replace(",", "").replace("₹", "").replace("Rs.", "")
    if normalized.startswith("(") and normalized.endswith(")"):
        normalized = "-" + normalized[1:-1]
    return float(normalized.replace("CR", "").replace("DR", "").strip())


def _amount_paise(row: dict) -> int:
    amount = _first(row, ("amount_paise",))
    if amount:
        return int(_number(amount))
    amount = _first(row, ("amount", "value", "transaction amount"))
    debit = _first(row, ("debit", "withdrawal", "debit amount"))
    credit = _first(row, ("credit", "deposit", "credit amount"))
    if debit or credit:
        if debit and _number(debit) != 0:
            return -round(abs(_number(debit)) * 100)
        if credit and _number(credit) != 0:
            return round(abs(_number(credit)) * 100)
        return 0
    if not amount:
        raise ValueError("Transaction row has no amount")
    return round(_number(amount) * 100)


def _is_balance_row(row: dict) -> bool:
    values = " ".join(str(value).strip().lower() for value in row.values())
    return any(marker in values for marker in ("opening balance", "closing balance", "opening bal", "closing bal"))


def clean_transactions(
    rows: Iterable[dict], user_id: str, source: str = "real"
) -> list[dict]:
    cleaned: list[dict] = []
    seen: set[str] = set()
    for row in rows:
        if _is_balance_row(row):
            continue
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
