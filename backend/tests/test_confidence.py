from datetime import date

from app.metrics.confidence import compute_confidence


def _rows(months: int = 6, uncategorised: bool = False):
    return [
        {"date": date(2025, month, 5), "amount_paise": 100000, "category": "Salary"}
        for month in range(1, months + 1)
    ] + [
        {
            "date": date(2025, month, 10),
            "amount_paise": -20000,
            "category": "Uncategorised" if uncategorised else "Groceries",
        }
        for month in range(1, months + 1)
    ]


def test_complete_data_has_high_confidence():
    result = compute_confidence(_rows(), loans=[{"id": "l1"}], cards=[{"id": "c1"}])
    assert result["score"] == 100
    assert result["level"] == "High"


def test_short_and_incomplete_data_is_low_confidence():
    result = compute_confidence(_rows(2, uncategorised=True))
    assert result["score"] < 55
    assert result["level"] == "Low"
    assert result["reasons"]
    assert result["how_to_improve"]


def test_large_date_gap_is_reported():
    rows = _rows()
    rows.append({"date": date(2027, 1, 1), "amount_paise": -1, "category": "Fees and Charges"})
    result = compute_confidence(rows, loans=[{"id": "l1"}], cards=[{"id": "c1"}])
    assert "large gap" in " ".join(result["reasons"])
