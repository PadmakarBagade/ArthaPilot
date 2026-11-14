"""ArthaPilot Formula Registry and Evidence Resolver (DEC-07, B5).

Every number produced by analytics, forecast, simulation, insights, or copilot
is associated with verifiable evidence (transaction IDs, entity IDs, formula ID, and formula text).
"""

from typing import Any, Dict, List, Optional

FORMULAS: Dict[str, Dict[str, str]] = {
    "savings_rate": {
        "id": "savings_rate",
        "name": "Savings Rate",
        "formula": "(monthly_income - monthly_expenses) / monthly_income",
        "inputs": "monthly_income_paise, monthly_expenses_paise",
        "plain_text": "Percentage of net income saved after all operating expenses.",
    },
    "debt_to_income": {
        "id": "debt_to_income",
        "name": "Debt-to-Income (DTI)",
        "formula": "monthly_debt_payments / monthly_income",
        "inputs": "monthly_debt_service_paise, monthly_income_paise",
        "plain_text": "Ratio of total monthly debt obligations (loans + card minimum dues) to monthly income.",
    },
    "emergency_runway_months": {
        "id": "emergency_runway_months",
        "name": "Emergency Fund Runway",
        "formula": "liquid_savings / average_monthly_expenses",
        "inputs": "liquid_balance_paise, average_monthly_expenses_paise",
        "plain_text": "Number of months liquid savings (savings + current accounts) can support current living expenses.",
    },
    "fixed_expense_ratio": {
        "id": "fixed_expense_ratio",
        "name": "Fixed Expense Ratio",
        "formula": "fixed_expenses / total_income",
        "inputs": "fixed_expenses_paise, total_income_paise",
        "plain_text": "Proportion of monthly income committed to non-negotiable obligations (rent, utilities, EMIs, insurance).",
    },
    "credit_utilisation": {
        "id": "credit_utilisation",
        "name": "Credit Card Utilisation",
        "formula": "total_card_balance / total_credit_limit",
        "inputs": "card_balance_paise, card_limit_paise",
        "plain_text": "Percentage of available revolving credit currently in use.",
    },
    "spending_volatility": {
        "id": "spending_volatility",
        "name": "Spending Volatility",
        "formula": "stdev(monthly_variable_spend) / mean(monthly_variable_spend)",
        "inputs": "monthly_variable_spend_series",
        "plain_text": "Standard deviation divided by the mean of variable monthly spending.",
    },
    "income_stability": {
        "id": "income_stability",
        "name": "Income Stability",
        "formula": "clamp(1 - stdev(monthly_income) / mean(monthly_income), 0, 1)",
        "inputs": "monthly_income_series",
        "plain_text": "Degree of predictability in monthly income, from 0 (very irregular) to 1 (steady salary).",
    },
    "monte_carlo_forecast": {
        "id": "monte_carlo_forecast",
        "name": "Monte Carlo Cashflow Projection",
        "formula": "liquid_balance + sum(scheduled_income) - sum(scheduled_obligations) - sum(bootstrap_daily_spend)",
        "inputs": "liquid_balance_paise, recurring_items, weekday_spend_empirical_distribution",
        "plain_text": "1,000-iteration empirical bootstrap simulation projecting 10th (worst case), 50th (likely), and 90th percentile balances.",
    },
    "debt_avalanche": {
        "id": "debt_avalanche",
        "name": "Debt Avalanche Payoff",
        "formula": "order_by(apr DESC, min_due); pay_extra_to_highest_apr(extra_amount)",
        "inputs": "card_balances, card_aprs, loan_outstanding, loan_aprs, extra_paise",
        "plain_text": "Optimal debt reduction strategy paying maximum extra principal toward highest interest APR debts first.",
    },
    "composite_health_score": {
        "id": "composite_health_score",
        "name": "Composite Financial Health Score (0-100)",
        "formula": "sum(subscore_i * weight_i) / sum(weight_i)",
        "inputs": "savings_rate_subscore (25), dti_subscore (20), runway_subscore (20), utilisation_subscore (15), volatility_subscore (10), stability_subscore (10)",
        "plain_text": "Renormalised weighted composite metric mapping subscores to standard bands: Strong (80+), Good (60-79), Fair (40-59), Poor (<40).",
    },
}


def get_formula(formula_id: str) -> Optional[Dict[str, str]]:
    """Retrieve registered formula definition."""
    return FORMULAS.get(formula_id)


def build_evidence(
    formula_id: Optional[str] = None,
    txn_ids: Optional[List[str]] = None,
    entity_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Helper to build a standard evidence packet (DEC-07)."""
    t_ids = list(txn_ids or [])
    truncated = len(t_ids) > 500
    if truncated:
        t_ids = t_ids[:500]

    formula_text = ""
    if formula_id and formula_id in FORMULAS:
        formula_text = FORMULAS[formula_id]["formula"]

    return {
        "formula_id": formula_id or "",
        "formula_text": formula_text,
        "txn_ids": t_ids,
        "entity_ids": list(entity_ids or []),
        "truncated": truncated,
        "total_txn_count": len(txn_ids or []),
    }

