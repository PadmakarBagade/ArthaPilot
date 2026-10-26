from io import BytesIO

import pytest

from app.ingestion.anonymise import anonymise_text
from app.ingestion.cleaning import clean_transactions
from app.ingestion.parser import parse_csv


def test_csv_parser_and_cleaning_deduplicate_and_sign_debit():
    rows = parse_csv(
        BytesIO(
            b"Date,Description,Debit,Credit,Account\n"
            b"01/02/2024,UPI/1234567890/ZOMATO,100.50,,a1\n"
            b"01/02/2024,UPI/1234567890/ZOMATO,100.50,,a1\n"
        )
    )
    transactions = clean_transactions(rows, "u1")
    assert len(transactions) == 1
    assert transactions[0]["amount_paise"] == -10050
    assert transactions[0]["date"].isoformat() == "2024-02-01"


def test_cleaning_rejects_bad_dates():
    with pytest.raises(ValueError, match="Invalid transaction date"):
        clean_transactions([{"date": "not-a-date", "amount": "1", "description": "x"}], "u1")


def test_anonymise_masks_personal_data():
    value = anonymise_text("Call +919876543210 or email person@example.com, account 1234 5678")
    assert "[PHONE]" in value
    assert "[EMAIL]" in value
    assert "[ACCOUNT]" in value
