from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any

INTERVALS = (7, 14, 30, 90, 365)


def _value(row: Any, name: str):
    return row.get(name) if isinstance(row, dict) else getattr(row, name)


def detect_recurring(transactions: list[Any]) -> list[dict[str, Any]]:
    groups: dict[str, list[Any]] = defaultdict(list)
    for row in transactions:
        merchant = str(_value(row, "merchant") or "").strip().upper()
        if merchant and _value(row, "amount_paise") < 0:
            groups[merchant].append(row)
    results = []
    for merchant, rows in groups.items():
        rows.sort(key=lambda row: _value(row, "date"))
        if len(rows) < 3:
            continue
        dates = [_value(row, "date") for row in rows]
        gaps = [(right - left).days for left, right in zip(dates, dates[1:])]
        interval = max(INTERVALS, key=lambda candidate: sum(abs(g - candidate) <= 3 for g in gaps))
        matching = [g for g in gaps if abs(g - interval) <= 3]
        if len(matching) < max(2, len(gaps) - 1):
            continue
        amounts = [abs(int(_value(row, "amount_paise"))) for row in rows]
        typical = int(median(amounts))
        tolerance = 0.20 if any(word in merchant for word in ("ELECTRIC", "GAS", "UTILITY", "MSEB")) else 0.10
        if any(abs(amount - typical) > typical * tolerance for amount in amounts):
            continue
        regularity = len(matching) / len(gaps)
        occurrence_score = min(1.0, len(rows) / 6)
        confidence = round(0.5 * regularity + 0.5 * occurrence_score, 4)
        next_due = dates[-1] + timedelta(days=interval)
        results.append(
            {
                "merchant": merchant,
                "interval_days": interval,
                "amount_paise": typical,
                "next_due_date": next_due,
                "occurrences": len(rows),
                "confidence": confidence,
                "txn_ids": [str(_value(row, "txn_id")) for row in rows],
            }
        )
    return sorted(results, key=lambda item: item["merchant"])
