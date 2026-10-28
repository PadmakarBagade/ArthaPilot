import csv

from scripts.anonymise_statement import anonymise_statement


def test_anonymise_statement_preserves_merchant_dates_and_amounts(tmp_path):
    source = tmp_path / "fake.csv"
    destination = tmp_path / "anonymous.csv"
    with source.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "amount", "description", "account_holder"])
        writer.writerow(
            [
                "2024-01-02",
                "-1200",
                "SWIGGY*ORDER 4482 UPI rahul@okbank",
                "Name: Rahul Sharma",
            ]
        )
        writer.writerow(
            [
                "2024-01-03",
                "65000",
                "SALARY CREDIT",
                "Name: Rahul Sharma",
            ]
        )

    anonymise_statement(source, destination)
    with destination.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert rows[0]["date"] == "2024-01-02"
    assert rows[0]["amount"] == "-1200"
    assert "SWIGGY*ORDER 4482" in rows[0]["description"]
    assert "UPI_ID_1" in rows[0]["description"]
    assert rows[0]["account_holder"] == "Name: PERSON_1"
    assert rows[1]["account_holder"] == "Name: PERSON_1"


def test_anonymise_statement_replaces_account_and_phone_numbers(tmp_path):
    source = tmp_path / "fake.csv"
    destination = tmp_path / "anonymous.csv"
    source.write_text(
        "date,amount,description\n"
        "2024-02-01,100,Call +919876543210 account 1234 5678\n",
        encoding="utf-8",
    )

    anonymise_statement(source, destination)
    output = destination.read_text(encoding="utf-8")

    assert "PHONE_1" in output
    assert "ACCOUNT_1" in output
    assert "2024-02-01" in output
    assert ",100," in output
