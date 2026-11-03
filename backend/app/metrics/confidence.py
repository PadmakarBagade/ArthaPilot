from __future__ import annotations

from collections import defaultdict
from datetime import date
from math import ceil
from statistics import mean, pstdev
from typing import Any


def _value(row: Any, name: str) -> Any:
    return row.get(name) if isinstance(row, dict) else getattr(row, name, None)


def _months(rows: list[Any]) -> set[tuple[int, int]]:
    return {
        (value.year, value.month)
        for row in rows
        if isinstance((value := _value(row, "date")), date)
    }


def _income_cv(rows: list[Any]) -> float | None:
    monthly: dict[tuple[int, int], int] = defaultdict(int)
    for row in rows:
        value = _value(row, "date")
        amount = int(_value(row, "amount_paise") or 0)
        category = str(_value(row, "category") or "")
        if isinstance(value, date) and amount > 0 and category in {"Salary", "Other Income"}:
            monthly[(value.year, value.month)] += amount
    values = [amount for amount in monthly.values() if amount > 0]
    if len(values) < 2 or mean(values) == 0:
        return None
    return pstdev(values) / mean(values)


def compute_confidence(
    transactions: list[Any],
    loans: list[Any] | None = None,
    cards: list[Any] | None = None,
    recurring_items: list[Any] | None = None,
) -> dict[str, Any]:
    loans = loans or []
    cards = cards or []
    recurring_items = recurring_items or []
    rows = list(transactions)
    months = _months(rows)
    penalties: list[tuple[int, str, str]] = []

    month_count = len(months)
    if month_count < 6:
        penalties.append(
            (min(30, 10 * (6 - month_count)), f"Only {month_count} month(s) of data", "Upload at least 6 months of transactions")
        )

    cv = _income_cv(rows)
    if cv is not None and cv > 0.15:
        penalties.append(
            (min(20, ceil((cv - 0.15) * 40)), "Income is irregular", "Add more months covering normal income cycles")
        )

    if rows:
        uncategorised = sum(
            1 for row in rows if str(_value(row, "category") or "").lower() in {"", "uncategorised"}
        ) / len(rows)
        if uncategorised > 0.05:
            penalties.append(
                (min(15, ceil((uncategorised - 0.05) * 100)), f"{uncategorised:.0%} of transactions are uncategorised", "Review or label uncategorised transactions")
            )
    else:
        uncategorised = 0.0

    if not loans:
        penalties.append((10, "No loan accounts were provided", "Link loan data if you have outstanding debt"))
    if not cards:
        penalties.append((10, "No credit card accounts were provided", "Link card data if you use credit cards"))

    dates = sorted(
        _value(row, "date") for row in rows if isinstance(_value(row, "date"), date)
    )
    if len(dates) > 1:
        gaps = [(right - left).days for left, right in zip(dates, dates[1:])]
        if max(gaps, default=0) > 45:
            penalties.append((10, "There is a large gap in transaction dates", "Upload transactions covering the missing period"))

    sparse_recurring = [
        item for item in recurring_items
        if len(_value(item, "txn_ids") or []) < 3
    ]
    if sparse_recurring:
        penalties.append((min(10, len(sparse_recurring) * 2), "Some recurring patterns have few observations", "Keep collecting transactions before relying on recurring predictions"))

    score = max(0, 100 - sum(item[0] for item in penalties))
    level = "High" if score >= 80 else "Medium" if score >= 55 else "Low"
    return {
        "score": score,
        "level": level,
        "reasons": [item[1] for item in penalties],
        "how_to_improve": list(dict.fromkeys(item[2] for item in penalties)),
        "months_of_data": month_count,
        "uncategorised_share": round(uncategorised, 4),
        "income_variability": round(cv, 4) if cv is not None else None,
    }
