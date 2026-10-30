"""Single source of truth for health metric definitions and score mappings."""

from dataclasses import dataclass


MAX_MONTHS = 6
MIN_REQUESTED_MONTHS = 3
MAX_REQUESTED_MONTHS = 12
MIN_MONTHS_FOR_VARIABILITY = 3

INCOME_CATEGORIES = frozenset({"Salary", "Other Income"})
EXCLUDED_EXPENSE_CATEGORIES = frozenset({"Credit Card Payment", "Investment/SIP"})
FIXED_EXPENSE_CATEGORIES = frozenset(
    {"Rent", "Utilities", "EMI/Loan", "Insurance", "Subscriptions"}
)

WEIGHTS = {
    "savings_rate": 25,
    "debt_to_income": 20,
    "emergency_runway_months": 20,
    "credit_utilisation": 15,
    "spending_volatility": 10,
    "income_stability": 10,
}


@dataclass(frozen=True)
class Mapping:
    points: tuple[tuple[float, float], ...]
    lower_is_better: bool = False


MAPPINGS = {
    "savings_rate": Mapping(((-0.10, 0), (0.00, 25), (0.10, 60), (0.20, 100))),
    "debt_to_income": Mapping(
        ((0.10, 100), (0.20, 85), (0.36, 60), (0.50, 25), (0.60, 0)),
        lower_is_better=True,
    ),
    "emergency_runway_months": Mapping(((0, 0), (1, 25), (3, 60), (6, 100))),
    "credit_utilisation": Mapping(
        ((0.10, 100), (0.30, 75), (0.50, 40), (0.75, 10), (1.00, 0)),
        lower_is_better=True,
    ),
    "spending_volatility": Mapping(
        ((0.10, 100), (0.25, 75), (0.50, 40), (1.00, 0)),
        lower_is_better=True,
    ),
    "income_stability": Mapping(((0.50, 0), (0.75, 35), (0.95, 70), (1.00, 100))),
}

LABELS = {
    "savings_rate": "Share of income you keep",
    "debt_to_income": "Debt payments vs income",
    "emergency_runway_months": "Months you could last without income",
    "fixed_expense_ratio": "Fixed bills vs income",
    "credit_utilisation": "Credit card used",
    "spending_volatility": "How much your spending swings",
    "income_stability": "How steady your income is",
}
