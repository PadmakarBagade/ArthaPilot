import csv
from datetime import date

from scripts.generate_personas import (
    DEFAULT_SEED,
    generate_rahul,
    write_all_personas,
    write_rahul,
)


def test_rahul_generation_is_deterministic_and_has_expected_shape(tmp_path):
    first = tmp_path / "first"
    second = tmp_path / "second"
    write_rahul(first, seed=7)
    write_rahul(second, seed=7)

    assert (first / "transactions.csv").read_bytes() == (second / "transactions.csv").read_bytes()
    with (first / "transactions.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 182
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


def test_all_personas_have_three_csv_files_and_planted_anomalies(tmp_path):
    write_all_personas(tmp_path)
    assert {path.name for path in tmp_path.iterdir()} == {
        "rahul", "priya", "arjun", "meera", "sam"
    }
    for persona_dir in tmp_path.iterdir():
        assert {path.name for path in persona_dir.iterdir()} == {
            "transactions.csv", "loans.csv", "cards.csv"
        }
        with (persona_dir / "transactions.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert len(rows) >= 144
        assert all(int(row["amount_paise"]) == int(row["amount_paise"]) for row in rows)

    descriptions_by_persona = {}
    rows_by_persona = {}
    for persona in ("rahul", "priya", "arjun", "meera", "sam"):
        with (tmp_path / persona / "transactions.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows_by_persona[persona] = list(csv.DictReader(handle))
            descriptions_by_persona[persona] = [
                row["description"] for row in rows_by_persona[persona]
            ]
    assert descriptions_by_persona["rahul"].count("DUPLICATE GROCERY CHARGE") == 2
    assert descriptions_by_persona["priya"].count("NETFLIX.COM") == 12
    netflix_amounts = {
        int(row["amount_paise"])
        for row in rows_by_persona["priya"]
        if row["description"] == "NETFLIX.COM"
    }
    assert netflix_amounts == {-99_900, -149_900}
    assert "EMERGENCY LAPTOP PURCHASE" in descriptions_by_persona["arjun"]
    assert descriptions_by_persona["meera"].count("DUPLICATE GROCERY CHARGE") == 2
    assert "EMERGENCY LAPTOP PURCHASE" in descriptions_by_persona["sam"]


def test_synthetic_labels_have_required_columns_and_no_duplicate_rows(tmp_path):
    write_all_personas(tmp_path / "synthetic")
    labels = tmp_path / "labeled" / "labeled_synthetic.csv"
    assert labels.exists()
    with labels.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    assert reader.fieldnames == ["raw_description", "true_category", "is_recurring"]
    assert len(rows) >= 200
    assert len(rows) == len(
        {
            (
                row["raw_description"],
                row["true_category"],
                row["is_recurring"],
            )
            for row in rows
        }
    )
    assert len(
        {row["raw_description"] for row in rows if "SWIGGY" in row["raw_description"]}
    ) >= 2
    assert any("UPI" in row["raw_description"] for row in rows)
    assert any("ORDR" in row["raw_description"] or "ZOMATOE" in row["raw_description"] for row in rows)
