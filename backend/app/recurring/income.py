from collections import defaultdict
from datetime import date
from statistics import mean, pstdev
from typing import Any


def _value(row: Any, name: str):
    return row.get(name) if isinstance(row, dict) else getattr(row, name)


def detect_income(transactions: list[Any]) -> dict[str, Any]:
    credits = [row for row in transactions if int(_value(row, "amount_paise")) > 0 and not _value(row, "is_self_transfer")]
    by_month: dict[tuple[int, int], list[Any]] = defaultdict(list)
    for row in credits:
        when = _value(row, "date")
        by_month[(when.year, when.month)].append(row)
    monthly = [sum(int(_value(row, "amount_paise")) for row in rows) for rows in by_month.values()]
    regularity = (pstdev(monthly) / mean(monthly)) if len(monthly) > 1 and mean(monthly) else 0.0
    by_merchant: dict[str, list[Any]] = defaultdict(list)
    for row in credits:
        by_merchant[str(_value(row, "merchant") or _value(row, "raw_description")).upper()].append(row)
    candidates = []
    for merchant, rows in by_merchant.items():
        if len(rows) < 3:
            continue
        days = [_value(row, "date").day for row in rows]
        if max(days) - min(days) <= 5:
            candidates.append((sum(int(_value(row, "amount_paise")) for row in rows) / len(rows), merchant, rows))
    salary = None
    if candidates:
        _, merchant, rows = max(candidates, key=lambda item: item[0])
        salary = {
            "merchant": merchant,
            "amount_paise": int(mean([int(_value(row, "amount_paise")) for row in rows])),
            "txn_ids": [str(_value(row, "txn_id")) for row in rows],
            "confidence": round(max(0.0, min(1.0, 0.8 - regularity)), 4),
        }
    salary_ids = set(salary["txn_ids"]) if salary else set()
    return {
        "salary": salary,
        "irregular_income_txn_ids": [
            str(_value(row, "txn_id")) for row in credits if str(_value(row, "txn_id")) not in salary_ids
        ],
        "monthly_income_regularity": round(regularity, 6),
    }
