#!/usr/bin/env python3
"""Hold-out backtest for cash-flow forecast.

Hides the last 30 days of transactions for each synthetic persona,
forecasts them from historical data, and measures:
- MAE (Mean Absolute Error) between actual balance and p50 likely balance
- Calibration: percentage of days actual balance fell within the 10-90 band
"""

import csv
from datetime import date, timedelta
from pathlib import Path
import sys

# Ensure backend can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.forecast.engine import build_schedule, monte_carlo_forecast, variable_spend_model
from app.recurring.income import detect_income


def run_backtest_for_persona(persona_name: str, holdout_days: int = 30) -> dict:
    persona_dir = Path(__file__).resolve().parents[1] / "data" / "synthetic" / persona_name
    txns_path = persona_dir / "transactions.csv"
    if not txns_path.exists():
        return {}

    with txns_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        all_txns = sorted(list(reader), key=lambda r: r["date"])

    if not all_txns:
        return {}

    # Convert amounts to int and dates to date
    for t in all_txns:
        t["amount_paise"] = int(t.get("amount_paise", 0))
        t["date"] = date.fromisoformat(t["date"])
        t["is_recurring"] = str(t.get("is_recurring", "")).lower() == "true"
        t["is_self_transfer"] = str(t.get("is_self_transfer", "")).lower() == "true"

    max_date = all_txns[-1]["date"]
    split_date = max_date - timedelta(days=holdout_days)

    train_txns = [t for t in all_txns if t["date"] <= split_date]
    test_txns = [t for t in all_txns if t["date"] > split_date]

    if not train_txns or not test_txns:
        return {}

    # Load initial balance from accounts.csv
    accounts_path = persona_dir / "accounts.csv"
    start_balance = 5000000  # Default 50k
    if accounts_path.exists():
        with accounts_path.open("r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("balance_paise"):
                    start_balance = int(row["balance_paise"])
                    break

    # Calculate actual cumulative balance on split_date
    actual_balance = start_balance + sum(t["amount_paise"] for t in train_txns)

    # Calculate actual daily balances for the holdout period
    daily_actuals: dict[date, int] = {}
    curr_balance = actual_balance
    test_by_date: dict[date, int] = {}
    for t in test_txns:
        d = t["date"]
        test_by_date[d] = test_by_date.get(d, 0) + t["amount_paise"]

    for i in range(1, holdout_days + 1):
        target_day = split_date + timedelta(days=i)
        curr_balance += test_by_date.get(target_day, 0)
        daily_actuals[target_day] = curr_balance

    # Build forecast inputs
    income = detect_income(train_txns)
    if income.get("salary"):
        salary_rows = [t for t in train_txns if t.get("txn_id") in income["salary"]["txn_ids"]]
        income["salary"]["day_of_month"] = min((t["date"].day for t in salary_rows), default=1)

    start_date = split_date + timedelta(days=1)
    schedule = build_schedule(
        recurring=[],
        income=income,
        loans=[],
        cards=[],
        start_date=start_date,
        days=holdout_days,
    )
    vmodel = variable_spend_model(train_txns)

    forecast = monte_carlo_forecast(
        balance_paise=actual_balance,
        schedule=schedule,
        variable_model=vmodel,
        days=holdout_days,
        runs=500,
        seed=42,
        start_date=start_date,
    )

    errors: list[float] = []
    in_band_count = 0

    for i, target_day in enumerate(forecast["dates"]):
        if target_day in daily_actuals:
            actual = daily_actuals[target_day]
            p10 = forecast["p10_paise"][i]
            p50 = forecast["p50_paise"][i]
            p90 = forecast["p90_paise"][i]

            errors.append(abs(actual - p50))
            if p10 <= actual <= p90:
                in_band_count += 1

    total_evaluated = len(errors)
    mae_paise = sum(errors) / total_evaluated if total_evaluated else 0
    mae_rupees = round(mae_paise / 100, 2)
    band_coverage_pct = round((in_band_count / total_evaluated) * 100, 2) if total_evaluated else 0

    return {
        "persona": persona_name,
        "holdout_days": total_evaluated,
        "mae_rupees": mae_rupees,
        "band_coverage_pct": band_coverage_pct,
    }


def main():
    personas = ["rahul", "priya", "arjun", "meera", "sam"]
    results = []
    for p in personas:
        res = run_backtest_for_persona(p)
        if res:
            results.append(res)

    print("\n--- FORECAST BACKTEST RESULTS (30-day holdout) ---")
    print(f"{'Persona':<12} | {'Holdout Days':<12} | {'MAE (₹)':<12} | {'10-90 Band Coverage':<18}")
    print("-" * 62)
    for r in results:
        print(f"{r['persona']:<12} | {r['holdout_days']:<12} | ₹{r['mae_rupees']:<11} | {r['band_coverage_pct']}%")

    avg_mae = round(sum(r["mae_rupees"] for r in results) / len(results), 2)
    avg_coverage = round(sum(r["band_coverage_pct"] for r in results) / len(results), 2)
    print("-" * 62)
    print(f"{'Average':<12} | {'30':<12} | ₹{avg_mae:<11} | {avg_coverage}%")

    # Update docs/validation_report.md
    report_path = Path(__file__).resolve().parents[1] / "docs" / "validation_report.md"
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        if "## Forecast backtesting" not in content:
            section = f"""

## Forecast backtesting

30-day holdout backtesting across synthetic personas:
- Overall 10-90 band coverage: {avg_coverage}% (target ~80%)
- Overall Mean Absolute Error (MAE): ₹{avg_mae:,.2f}

| Persona | Holdout Days | MAE (₹) | 10-90 Band Coverage |
|---|---:|---:|---:|
"""
            for r in results:
                section += f"| {r['persona'].title()} | {r['holdout_days']} | ₹{r['mae_rupees']:,.2f} | {r['band_coverage_pct']}% |\n"
            report_path.write_text(content + section, encoding="utf-8")
            print("\nUpdated docs/validation_report.md with verified forecast numbers.")


if __name__ == "__main__":
    main()
