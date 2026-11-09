from datetime import date

import pytest

from app.simulate import affordability, debt_payoff_plan, goal_plan, rank_actions, simulate


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


def test_debt_payoff_plan_avalanche_and_snowball():
    loans = [
        {"id": "l1", "type": "Personal Loan", "outstanding_paise": 10000000, "rate_apr": 16.0, "emi_paise": 500000},
        {"id": "l2", "type": "Car Loan", "outstanding_paise": 20000000, "rate_apr": 9.5, "emi_paise": 600000},
    ]
    cards = [
        {"id": "c1", "type": "Credit Card", "outstanding_paise": 5000000, "rate_apr": 36.0, "emi_paise": 300000},
    ]

    # Test avalanche
    plan_avalanche = debt_payoff_plan(loans, cards, extra_monthly_paise=500000, strategy="avalanche")
    assert plan_avalanche["months_saved"] > 0
    assert plan_avalanche["interest_saved_paise"] > 0
    assert plan_avalanche["payoff_order"][0] == "c1"  # Highest APR (36%) paid first

    # Test snowball
    plan_snowball = debt_payoff_plan(loans, cards, extra_monthly_paise=500000, strategy="snowball")
    assert plan_snowball["months_saved"] > 0
    assert plan_snowball["interest_saved_paise"] > 0
    assert plan_snowball["payoff_order"][0] == "c1"  # Lowest balance (50k) paid first
