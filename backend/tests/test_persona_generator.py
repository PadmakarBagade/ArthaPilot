import csv
from datetime import date

from scripts.generate_personas import DEFAULT_SEED, generate_rahul, write_rahul


def test_rahul_generation_is_deterministic_and_has_expected_shape(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_rahul(first, seed=7)
    write_rahul(second, seed=7)

    assert (first / "transactions.csv").read_bytes() == (second / "transactions.csv").read_bytes()
    with (first / "transactions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 168
    assert {"transactions.csv", "loans.csv", "cards.csv"} == {
        path.name for path in first.iterdir()
    }


def test_rahul_income_and_recurring_bills_use_expected_dates():
    rows = generate_rahul(seed=DEFAULT_SEED)
    by_date = {(row["date"], row["description"]): row["amount_paise"] for row in rows}

    assert by_date[("2024-01-01", "SALARY CREDIT")] == 6_500_000
    assert by_date[("2024-01-02", "RENT PAYMENT")] == -1_800_000
    assert by_date[("2024-01-05", "CAR EMI")] == -425_000
    assert by_date[("2024-01-12", "NETFLIX.COM")] == -99_900
    assert by_date[("2024-01-14", "SPOTIFY")] == -11_900
    assert by_date[("2024-01-16", "FITNESS FIRST GYM MEMBERSHIP")] == -120_000
    assert sum(row["description"] == "SALARY CREDIT" for row in rows) == 12
    assert all(isinstance(row["amount_paise"], int) for row in rows)
