from datetime import date, timedelta

from app.recurring.detector import detect_recurring
from app.recurring.income import detect_income


def _rows(interval=30, count=5, amount=-10000):
    return [
        {
            "txn_id": f"t{index}",
            "date": date(2024, 1, 1) + timedelta(days=interval * index),
            "amount_paise": amount,
            "merchant": "NETFLIX",
            "is_self_transfer": False,
        }
        for index in range(count)
    ]


def test_recurring_requires_three_and_returns_evidence():
    assert detect_recurring(_rows(count=2)) == []
    result = detect_recurring(_rows())[0]
    assert result["interval_days"] == 30
    assert result["amount_paise"] == 10000
    assert len(result["txn_ids"]) == 5


def test_irregular_gaps_are_not_recurring():
    rows = _rows()
    rows[3]["date"] += timedelta(days=20)
    assert detect_recurring(rows) == []


def test_income_detects_monthly_salary_and_irregular_remainder():
    rows = [
        {
            "txn_id": f"s{month}",
            "date": date(2024, month, 1),
            "amount_paise": 500000,
            "merchant": "SALARY",
            "is_self_transfer": False,
        }
        for month in range(1, 6)
    ]
    rows.append(
        {
            "txn_id": "other",
            "date": date(2024, 3, 10),
            "amount_paise": 1000,
            "merchant": "CLIENT",
            "is_self_transfer": False,
        }
    )
    result = detect_income(rows)
    assert result["salary"]["amount_paise"] == 500000
    assert result["irregular_income_txn_ids"] == ["other"]
