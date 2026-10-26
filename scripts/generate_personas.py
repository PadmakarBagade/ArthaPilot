from datetime import date
from pathlib import Path
import csv
import random


PERSONAS = [
    ("rahul", "Rahul", 65000, "credit card debt"),
    ("priya", "Priya", 120000, "healthy"),
    ("arjun", "Arjun", 70000, "irregular income"),
    ("meera", "Meera", 90000, "dual loans"),
    ("sam", "Sam", 35000, "no savings"),
]


def generate_persona(name: str, income: int, profile: str, seed: int = 42) -> list[dict]:
    rng = random.Random(seed + len(name))
    rows = []
    for month in range(12):
        month_date = date(2024 + month // 12, month % 12 + 1, 1)
        salary = income if profile != "irregular income" or month % 3 else income // 2
        rows.append({"date": month_date.isoformat(), "amount": salary, "description": "SALARY CREDIT"})
        rows.extend(
            [
                {"date": month_date.replace(day=2).isoformat(), "amount": -12000, "description": "RENT PAYMENT"},
                {"date": month_date.replace(day=5).isoformat(), "amount": -3500, "description": "SWIGGY*ORDER 4482"},
                {"date": month_date.replace(day=10).isoformat(), "amount": -1800, "description": "UPI/4458221/ZOMATO"},
                {"date": month_date.replace(day=15).isoformat(), "amount": -999, "description": "NETFLIX.COM"},
                {"date": month_date.replace(day=20).isoformat(), "amount": -2500, "description": "AMZN PAY IN"},
            ]
        )
        if profile in {"credit card debt", "dual loans"}:
            rows.append({"date": month_date.replace(day=7).isoformat(), "amount": -9000, "description": "EMI LOAN"})
        if rng.random() < 0.25:
            rows.append({"date": month_date.replace(day=25).isoformat(), "amount": -5000, "description": "DUPLICATE CHARGE"})
    return rows


def write_personas(output_dir: Path = Path("data/synthetic"), seed: int = 42) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for user_id, name, income, profile in PERSONAS:
        with (output_dir / f"{user_id}.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["date", "amount", "description"])
            writer.writeheader()
            writer.writerows(generate_persona(name, income, profile, seed))
        for filename, headers, values in (
            ("loans.csv", ["user_id", "amount_paise", "monthly_payment_paise"], [user_id, 10000000, 900000]),
            ("cards.csv", ["user_id", "limit_paise", "balance_paise"], [user_id, 15000000, 4000000]),
            ("investments.csv", ["user_id", "name", "value_paise"], [user_id, "SIP", 500000]),
        ):
            path = output_dir / filename
            write_header = not path.exists()
            with path.open("a", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                if write_header:
                    writer.writerow(headers)
                writer.writerow(values)


if __name__ == "__main__":
    write_personas()
