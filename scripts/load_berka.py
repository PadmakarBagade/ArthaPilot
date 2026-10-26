import csv
from pathlib import Path

from app.ingestion.cleaning import clean_transactions


def load_berka_rows(path: Path, user_id: str = "berka") -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    converted = [
        {
            "trans_id": row["trans_id"],
            "account_id": row["account_id"],
            "date": row["date"],
            "amount": row["amount"],
            "description": " ".join(
                value for value in (row.get("operation", ""), row.get("k_symbol", "")) if value
            ),
        }
        for row in rows
    ]
    return clean_transactions(converted, user_id=user_id, source="berka")


if __name__ == "__main__":
    print(len(load_berka_rows(Path("data/berka/trans.csv"))))
