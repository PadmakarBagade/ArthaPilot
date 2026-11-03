from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
import random
from statistics import mean
from typing import Any, Iterable


def _get(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid forecast date: {value!r}") from exc


def build_schedule(
    recurring: Iterable[Any] = (),
    income: dict[str, Any] | None = None,
    loans: Iterable[Any] = (),
    cards: Iterable[Any] = (),
    start_date: date | None = None,
    days: int = 90,
) -> list[dict[str, Any]]:
    """Build dated cash-flow events. Inflows are positive, outflows negative."""
    if days < 1:
        raise ValueError("days must be at least 1")
    start = start_date or date.today()
    end = start + timedelta(days=days - 1)
    events: list[dict[str, Any]] = []

    def add(when: date, amount: int, kind: str, evidence: list[str] | None = None, label: str = ""):
        if start <= when <= end and amount:
            events.append({"date": when, "amount_paise": int(amount), "kind": kind,
                           "label": label, "evidence_ids": evidence or []})

    for item in recurring:
        due = _as_date(_get(item, "next_due_date"))
        interval = int(_get(item, "interval_days", 0))
        if interval <= 0:
            raise ValueError("Recurring schedule interval_days must be positive")
        amount = abs(int(_get(item, "amount_paise", 0)))
        while due <= end:
            add(due, -amount, "recurring", list(_get(item, "txn_ids", [])), str(_get(item, "merchant", "")))
            due += timedelta(days=interval)

    salary = (income or {}).get("salary") if income else None
    if salary:
        amount = int(salary.get("amount_paise", 0))
        if amount <= 0:
            raise ValueError("Salary amount_paise must be positive")
        ids = [str(x) for x in salary.get("txn_ids", [])]
        day = int(salary.get("day_of_month", 1))
        if not 1 <= day <= 31:
            raise ValueError("Salary day_of_month must be between 1 and 31")
        cursor = start
        while cursor <= end:
            if cursor.day == day:
                add(cursor, amount, "salary", ids, str(salary.get("merchant", "salary")))
            cursor += timedelta(days=1)

    for loan in loans:
        due = _get(loan, "next_due_date")
        emi = int(_get(loan, "emi_paise", 0))
        if due and emi > 0:
            add(_as_date(due), -emi, "emi", [str(_get(loan, "id", ""))], str(_get(loan, "type", "loan")))
    for card in cards:
        due = _get(card, "due_date")
        minimum = int(_get(card, "min_due_paise", 0))
        if due and minimum > 0:
            add(_as_date(due), -minimum, "card_due", [str(_get(card, "id", ""))], "card minimum")
    return sorted(events, key=lambda event: (event["date"], event["kind"]))


def variable_spend_model(transactions: Iterable[Any]) -> dict[str, Any]:
    """Return weekday means and the empirical (bootstrap) variable-spend samples."""
    by_weekday: dict[int, list[int]] = defaultdict(list)
    samples: list[int] = []
    for row in transactions:
        amount = int(_get(row, "amount_paise", 0))
        if amount >= 0 or bool(_get(row, "is_recurring", False)) or bool(_get(row, "is_self_transfer", False)):
            continue
        value = abs(amount)
        weekday = _as_date(_get(row, "date")).weekday()
        by_weekday[weekday].append(value)
        samples.append(value)
    averages = {str(day): int(mean(values)) if values else 0 for day, values in by_weekday.items()}
    return {"weekday_averages_paise": averages, "weekday_averages": averages,
            "samples_paise": samples,
            "transaction_count": len(samples)}


def _quantile(values: list[int], fraction: float) -> int:
    if not values:
        return 0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(fraction * (len(ordered) - 1))))
    return int(ordered[index])


def monte_carlo_forecast(
    balance_paise: int,
    schedule: Iterable[dict[str, Any]],
    variable_model: dict[str, Any],
    days: int = 90,
    runs: int = 1000,
    seed: int = 42,
    start_date: date | None = None,
) -> dict[str, Any]:
    if days < 1 or runs < 1:
        raise ValueError("days and runs must be positive")
    start = start_date or date.today()
    by_date: dict[date, int] = defaultdict(int)
    for event in schedule:
        by_date[_as_date(event["date"])] += int(event["amount_paise"])
    samples = [int(x) for x in variable_model.get("samples_paise", []) if int(x) >= 0]
    weekday = variable_model.get("weekday_averages_paise", {})
    rng = random.Random(seed)
    paths: list[list[int]] = []
    for _ in range(runs):
        balance = int(balance_paise)
        path: list[int] = []
        for offset in range(days):
            when = start + timedelta(days=offset)
            spend = rng.choice(samples) if samples else int(weekday.get(str(when.weekday()), 0))
            balance += by_date.get(when, 0) - spend
            path.append(balance)
        paths.append(path)
    dates = [start + timedelta(days=i) for i in range(days)]
    columns = [[p[i] for p in paths] for i in range(days)]
    return {"dates": dates, "p10_paise": [_quantile(values, .10) for values in columns],
            "p50_paise": [_quantile(values, .50) for values in columns],
            "p90_paise": [_quantile(values, .90) for values in columns],
            "probability_below_zero": [sum(value < 0 for value in values) / runs for values in columns],
            "runs": runs, "seed": seed, "start_balance_paise": int(balance_paise)}


def detect_gaps(forecast: dict[str, Any], safe_threshold_paise: int | None = None,
                runs: int = 1000) -> list[dict[str, Any]]:
    threshold = 0 if safe_threshold_paise is None else int(safe_threshold_paise)
    gaps = []
    probabilities = forecast.get("probability_below_zero", [])
    for index, (when, balance) in enumerate(zip(forecast["dates"], forecast["p10_paise"])):
        if int(balance) < threshold:
            gaps.append({"date": when, "expected_balance_paise": int(balance),
                         "probability_below_zero": float(probabilities[index]) if index < len(probabilities)
                         else (1.0 if balance < 0 else 0.0),
                         "evidence": "p10 Monte Carlo balance"})
    return gaps


def stress_test(state: dict[str, Any], scenario: str, days: int = 90,
                runs: int = 1000, seed: int = 42) -> dict[str, Any]:
    """Re-run a forecast under a named shock; state contains forecast inputs."""
    allowed = {"income_stops_1_month", "income_stops_2_months", "income_stops_3_months",
               "expenses_rise_15", "emergency_expense_50000", "new_emi"}
    if scenario not in allowed:
        raise ValueError(f"Unknown stress scenario: {scenario}")
    schedule = [dict(event) for event in state.get("schedule", [])]
    start = state.get("start_date") or date.today()
    if scenario.startswith("income_stops_"):
        months = int(scenario.split("_")[2].replace("months", ""))
        cutoff = start + timedelta(days=months * 30)
        schedule = [event for event in schedule if not (event["kind"] == "salary" and _as_date(event["date"]) < cutoff)]
    model = dict(state.get("variable_model", {}))
    if scenario == "expenses_rise_15":
        model["samples_paise"] = [int(x * 115 // 100) for x in model.get("samples_paise", [])]
    if scenario == "emergency_expense_50000":
        schedule.append({"date": start, "amount_paise": -5_000_000, "kind": "emergency", "evidence_ids": ["scenario"]})
    if scenario == "new_emi":
        schedule.append({"date": start + timedelta(days=30), "amount_paise": -int(state.get("new_emi_paise", 0)),
                         "kind": "emi", "evidence_ids": ["scenario"]})
    result = monte_carlo_forecast(int(state.get("balance_paise", 0)), schedule, model, days, runs, seed, start)
    breaches = [d for d, value in zip(result["dates"], result["p10_paise"]) if value < 0]
    return {"scenario": scenario, "forecast": result, "survival_days": (breaches[0] - start).days if breaches else days,
            "first_breach_date": breaches[0] if breaches else None}
