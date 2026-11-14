from datetime import date

import pytest

from app.forecast import (
    build_schedule,
    detect_gaps,
    monte_carlo_forecast,
    stress_test,
    variable_spend_model,
)


def test_schedule_has_recurring_and_salary_events():
    events = build_schedule(
        [{"next_due_date": date(2024, 1, 2), "interval_days": 30,
          "amount_paise": 1000, "txn_ids": ["bill"]}],
        {"salary": {"amount_paise": 10000, "day_of_month": 3, "txn_ids": ["salary"]}},
        start_date=date(2024, 1, 1), days=35,
    )
    assert [(event["date"], event["amount_paise"]) for event in events] == [
        (date(2024, 1, 2), -1000), (date(2024, 1, 3), 10000),
        (date(2024, 2, 1), -1000), (date(2024, 2, 3), 10000),
    ]


def test_seeded_forecast_is_reproducible_and_gaps_are_explicit():
    model = variable_spend_model([
        {"date": date(2024, 1, 1), "amount_paise": -100, "is_recurring": False},
        {"date": date(2024, 1, 2), "amount_paise": -200, "is_recurring": False},
    ])
    kwargs = {"balance_paise": 250, "schedule": [], "variable_model": model,
              "days": 3, "runs": 100, "seed": 7, "start_date": date(2024, 1, 1)}
    first = monte_carlo_forecast(**kwargs)
    assert first == monte_carlo_forecast(**kwargs)
    gaps = detect_gaps(first)
    assert gaps and gaps[0]["expected_balance_paise"] < 0


def test_stress_unknown_scenario_errors_and_income_stop_survives():
    state = {"balance_paise": 1000, "schedule": [
        {"date": date(2024, 1, 1), "amount_paise": 5000, "kind": "salary"},
    ], "variable_model": {"samples_paise": []}, "start_date": date(2024, 1, 1)}
    with pytest.raises(ValueError):
        stress_test(state, "unknown")
    result = stress_test(state, "income_stops_2_months", days=10, runs=100)
    assert result["survival_days"] == 10


def test_forecast_backtest_runs():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from backtest import run_backtest_for_persona
    res = run_backtest_for_persona("rahul", holdout_days=10)
    assert res
    assert "mae_rupees" in res
    assert "band_coverage_pct" in res

