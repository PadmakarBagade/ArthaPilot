from pathlib import Path

from app.ingestion.gpay import load_gpay_csv


def test_gpay_adapter_keeps_paise_account_and_self_transfer(tmp_path: Path):
    source = tmp_path / "gpay.csv"
    source.write_text(
        "txn_id,date,amount_paise,raw_description,bank_account,is_self_transfer\n"
        "a1,2024-01-01,-1250,Paid to SHOP,bank-1,False\n"
        "a2,2024-01-02,2000,Self transfer to SAVINGS,bank-2,True\n",
        encoding="utf-8",
    )
    rows = load_gpay_csv(source, "local")
    assert rows[0]["amount_paise"] == -1250
    assert rows[0]["account_id"] == "bank-1"
    assert rows[1]["is_self_transfer"] is True
