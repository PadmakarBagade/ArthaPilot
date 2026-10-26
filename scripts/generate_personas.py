"""Generate the deterministic Rahul synthetic persona."""

import csv
import random
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path


DEFAULT_SEED = 42
MONTHS = 12
SALARY_PAISE = 6_500_000


def _next_weekend(year: int, month: int, day: int) -> date:
    candidate = date(year, month, day)
    return candidate + timedelta(days=(5 - candidate.weekday()) % 7)


def generate_rahul(seed: int = DEFAULT_SEED, start_year: int = 2024) -> list[dict[str, int | str]]:
    """Return twelve months of Rahul's transactions in integer paise."""
    rng = random.Random(seed)
    transactions: list[dict[str, int | str]] = []

    def add(transaction_date: date, amount_paise: int, description: str) -> None:
        transactions.append(
            {
                "date": transaction_date.isoformat(),
                "amount_paise": amount_paise,
                "description": description,
            }
        )

    for month_offset in range(MONTHS):
        year = start_year + month_offset // 12
        month = month_offset % 12 + 1
        last_day = monthrange(year, month)[1]
        add(date(year, month, 1), SALARY_PAISE, "SALARY CREDIT")
        add(date(year, month, 2), -1_800_000, "RENT PAYMENT")
        add(date(year, month, 5), -4_250_00, "CAR EMI")
        add(date(year, month, 6), -3_500_00, "ELECTRICITY BILL")
        add(date(year, month, 8), -499_00, "AIRTEL MOBILE BILL")
        add(date(year, month, 10), -799_00, "ACT FIBERNET INTERNET")
        add(date(year, month, 12), -999_00, "NETFLIX.COM")
        add(date(year, month, 14), -119_00, "SPOTIFY")
        add(date(year, month, 16), -1_200_00, "FITNESS FIRST GYM MEMBERSHIP")
        add(date(year, month, 20), -2_500_00, "CREDIT CARD PAYMENT")

        # Two weekend food/UPI events per month make weekend spending visibly higher.
        first_weekend = _next_weekend(year, month, 3)
        second_weekend = _next_weekend(year, month, min(17, last_day))
        for weekend_date in (first_weekend, second_weekend):
            add(
                weekend_date,
                -rng.randint(1_200, 2_800) * 100,
                f"SWIGGY*ORDER {rng.randint(1000, 9999)}",
            )
            add(
                weekend_date + timedelta(days=1),
                -rng.randint(800, 2_200) * 100,
                f"UPI/4458221/ZOMATO",
            )

    return transactions


def write_rahul(output_dir: Path = Path("data/synthetic/rahul"), seed: int = DEFAULT_SEED) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    transactions = generate_rahul(seed)

    with (output_dir / "transactions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "amount_paise", "description"])
        writer.writeheader()
        writer.writerows(transactions)

    with (output_dir / "loans.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "user_id",
                "type",
                "principal_paise",
                "outstanding_paise",
                "emi_paise",
                "rate_apr",
                "tenure_left_months",
                "next_due_date",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "rahul-car-loan",
                "user_id": "rahul",
                "type": "vehicle",
                "principal_paise": 800_000_00,
                "outstanding_paise": 520_000_00,
                "emi_paise": 4_250_00,
                "rate_apr": "10.5",
                "tenure_left_months": 36,
                "next_due_date": "2024-01-05",
            }
        )

    with (output_dir / "cards.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "id",
                "user_id",
                "limit_paise",
                "balance_paise",
                "apr",
                "min_due_paise",
                "due_date",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "id": "rahul-credit-card",
                "user_id": "rahul",
                "limit_paise": 150_000_00,
                "balance_paise": 125_000_00,
                "apr": "36.0",
                "min_due_paise": 6_250_00,
                "due_date": "2024-01-20",
            }
        )


if __name__ == "__main__":
    write_rahul()
