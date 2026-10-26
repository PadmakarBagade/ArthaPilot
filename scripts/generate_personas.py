"""Generate deterministic synthetic personas for the data layer."""

import csv
import random
from calendar import monthrange
from datetime import date, timedelta
from pathlib import Path


DEFAULT_SEED = 42
MONTHS = 12

Profile = dict[str, object]

PROFILES: dict[str, Profile] = {
    "rahul": {
        "name": "Rahul",
        "age": 28,
        "salary_paise": 6_500_000,
        "income_description": "SALARY CREDIT",
        "rent_paise": 1_800_000,
        "loan_count": 1,
        "loan_type": "vehicle",
        "loan_emi_paise": 425_000,
        "card_limit_paise": 15_000_000,
        "card_balance_paise": 12_500_000,
        "card_apr": 36.0,
        "sip_paise": 0,
        "anomaly": "duplicate",
    },
    "priya": {
        "name": "Priya",
        "age": 34,
        "salary_paise": 12_000_000,
        "income_description": "SALARY CREDIT",
        "rent_paise": 0,
        "loan_count": 1,
        "loan_type": "home",
        "loan_emi_paise": 3_800_000,
        "card_limit_paise": 30_000_000,
        "card_balance_paise": 2_000_000,
        "card_apr": 24.0,
        "sip_paise": 2_000_000,
        "anomaly": "subscription_hike",
    },
    "arjun": {
        "name": "Arjun",
        "age": 26,
        "salary_paise": 7_000_000,
        "income_description": "CLIENT PAYMENT",
        "rent_paise": 1_500_000,
        "loan_count": 0,
        "loan_type": "",
        "loan_emi_paise": 0,
        "card_limit_paise": 8_000_000,
        "card_balance_paise": 1_000_000,
        "card_apr": 30.0,
        "sip_paise": 0,
        "anomaly": "large_spend",
    },
    "meera": {
        "name": "Meera",
        "age": 41,
        "salary_paise": 9_000_000,
        "income_description": "SALARY CREDIT",
        "rent_paise": 0,
        "loan_count": 2,
        "loan_type": "home",
        "loan_emi_paise": 2_500_000,
        "second_loan_emi_paise": 1_500_000,
        "card_limit_paise": 20_000_000,
        "card_balance_paise": 18_500_000,
        "card_apr": 42.0,
        "sip_paise": 0,
        "anomaly": "duplicate",
    },
    "sam": {
        "name": "Sam",
        "age": 23,
        "salary_paise": 3_500_000,
        "income_description": "SALARY CREDIT",
        "rent_paise": 900_000,
        "loan_count": 0,
        "loan_type": "",
        "loan_emi_paise": 0,
        "card_limit_paise": 3_000_000,
        "card_balance_paise": 700_000,
        "card_apr": 30.0,
        "sip_paise": 0,
        "anomaly": "large_spend",
    },
}


def _next_weekend(year: int, month: int, day: int) -> date:
    candidate = date(year, month, day)
    return candidate + timedelta(days=(5 - candidate.weekday()) % 7)


def generate_persona(
    persona_id: str, seed: int = DEFAULT_SEED, start_year: int = 2024
) -> list[dict[str, int | str]]:
    profile = PROFILES[persona_id]
    rng = random.Random(seed + list(PROFILES).index(persona_id))
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
        income = int(profile["salary_paise"])
        if persona_id == "arjun":
            income = rng.randint(4_000_000, 10_000_000)
        add(date(year, month, 1), income, str(profile["income_description"]))

        rent = int(profile["rent_paise"])
        if rent:
            add(date(year, month, 2), -rent, "RENT PAYMENT")
        if int(profile["loan_count"]):
            add(date(year, month, 5), -int(profile["loan_emi_paise"]), "HOME LOAN EMI" if persona_id == "priya" else "CAR EMI")
        if int(profile["loan_count"]) > 1:
            add(date(year, month, 7), -int(profile["second_loan_emi_paise"]), "PERSONAL LOAN EMI")
        add(date(year, month, 6), -350_000, "ELECTRICITY BILL")
        add(date(year, month, 8), -49_900, "AIRTEL MOBILE BILL")
        add(date(year, month, 10), -79_900, "ACT FIBERNET INTERNET")
        netflix = -99_900
        if profile["anomaly"] == "subscription_hike" and month >= 7:
            netflix = -149_900
        add(date(year, month, 12), netflix, "NETFLIX.COM")
        add(date(year, month, 14), -11_900, "SPOTIFY")
        if persona_id in {"rahul", "arjun"}:
            add(date(year, month, 16), -120_000, "FITNESS FIRST GYM MEMBERSHIP")
        if int(profile["sip_paise"]):
            add(date(year, month, 18), -int(profile["sip_paise"]), "MUTUAL FUND SIP")
        if int(profile["card_balance_paise"]):
            add(date(year, month, 20), -max(50_000, int(profile["card_balance_paise"]) // 50), "CREDIT CARD PAYMENT")

        for weekend_date in (
            _next_weekend(year, month, 3),
            _next_weekend(year, month, min(17, last_day)),
        ):
            add(weekend_date, -rng.randint(1_200, 2_800) * 100, f"SWIGGY*ORDER {rng.randint(1000, 9999)}")
            add(weekend_date + timedelta(days=1), -rng.randint(800, 2_200) * 100, "UPI/4458221/ZOMATO")

        if month == 6 and profile["anomaly"] == "duplicate":
            add(date(year, month, 25), -250_000, "DUPLICATE GROCERY CHARGE")
            add(date(year, month, 25), -250_000, "DUPLICATE GROCERY CHARGE")
        if month == 9 and profile["anomaly"] == "large_spend":
            add(date(year, month, 23), -1_500_000, "EMERGENCY LAPTOP PURCHASE")

    return transactions


def generate_rahul(seed: int = DEFAULT_SEED, start_year: int = 2024) -> list[dict[str, int | str]]:
    return generate_persona("rahul", seed, start_year)


def _write_loan_rows(persona_id: str, output_dir: Path) -> None:
    profile = PROFILES[persona_id]
    fields = [
        "id", "user_id", "type", "principal_paise", "outstanding_paise",
        "emi_paise", "rate_apr", "tenure_left_months", "next_due_date",
    ]
    with (output_dir / "loans.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for index in range(int(profile["loan_count"])):
            emi = int(profile["loan_emi_paise"]) if index == 0 else int(profile["second_loan_emi_paise"])
            writer.writerow(
                {
                    "id": f"{persona_id}-loan-{index + 1}",
                    "user_id": persona_id,
                    "type": str(profile["loan_type"]) if index == 0 else "personal",
                    "principal_paise": emi * 160,
                    "outstanding_paise": emi * 100,
                    "emi_paise": emi,
                    "rate_apr": "10.5" if index == 0 else "16.0",
                    "tenure_left_months": 36 if index == 0 else 24,
                    "next_due_date": "2024-01-05",
                }
            )


def _write_card_row(persona_id: str, output_dir: Path) -> None:
    profile = PROFILES[persona_id]
    with (output_dir / "cards.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["id", "user_id", "limit_paise", "balance_paise", "apr", "min_due_paise", "due_date"]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow(
            {
                "id": f"{persona_id}-credit-card",
                "user_id": persona_id,
                "limit_paise": int(profile["card_limit_paise"]),
                "balance_paise": int(profile["card_balance_paise"]),
                "apr": profile["card_apr"],
                "min_due_paise": max(50_000, int(profile["card_balance_paise"]) // 20),
                "due_date": "2024-01-20",
            }
        )


def write_persona(
    persona_id: str, output_dir: Path | None = None, seed: int = DEFAULT_SEED
) -> None:
    output_dir = output_dir or Path("data/synthetic") / persona_id
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "transactions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "amount_paise", "description"])
        writer.writeheader()
        writer.writerows(generate_persona(persona_id, seed))
    _write_loan_rows(persona_id, output_dir)
    _write_card_row(persona_id, output_dir)


def write_rahul(output_dir: Path = Path("data/synthetic/rahul"), seed: int = DEFAULT_SEED) -> None:
    write_persona("rahul", output_dir, seed)


def write_all_personas(output_root: Path = Path("data/synthetic"), seed: int = DEFAULT_SEED) -> None:
    for persona_id in PROFILES:
        write_persona(persona_id, output_root / persona_id, seed)


if __name__ == "__main__":
    write_all_personas()
