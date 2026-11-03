from datetime import date

import pytest

from app.simulate import affordability, goal_plan, rank_actions, simulate


def state():
    return {
        "months": 1,
        "accounts": [{"type": "savings", "balance_paise": 1000000}],
        "transactions": [
            {"txn_id": "salary", "amount_paise": 1000000, "category": "Salary"},
            {"txn_id": "food", "amount_paise": -200000, "category": "Food Delivery"},
            {"txn_id": "rent", "amount_paise": -300000, "category": "Rent"},
        ],
    }


def test_simulation_is_pure_and_reports_delta():
    original = state()
    result = simulate(original, {"type": "cut_category", "category": "Food Delivery", "percent": 50})
    assert original["transactions"][1]["amount_paise"] == -200000
    assert result["delta"]["surplus_paise"] == 100000
    assert result["evidence"]["formula"]


def test_rank_actions_returns_best_move():
    result = rank_actions(state())
    assert result["best_move"]["action"]["category"] == "Food Delivery"


def test_affordability_has_safe_threshold():
    result = affordability(state(), 500000)
    assert result["verdict"] == "Yes"
    assert result["balance_after_paise"] == 500000


def test_goal_plan_uses_integer_ceiling():
    result = goal_plan(state(), 100001, date(2026, 6, 1), today=date(2026, 1, 1))
    assert result["required_monthly_paise"] == 20001


def test_invalid_action_is_explicit():
    with pytest.raises(ValueError):
        simulate(state(), {"type": "unknown"})
