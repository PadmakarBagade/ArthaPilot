from __future__ import annotations

from calendar import monthrange
from dataclasses import asdict, dataclass
from datetime import date
from math import sqrt
from statistics import mean
from typing import Any, Iterable

from .config import (
    EXCLUDED_EXPENSE_CATEGORIES,
    FIXED_EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    LABELS,
    MIN_MONTHS_FOR_VARIABILITY,
)


@dataclass
class MetricResult:
    key: str
    plain_label: str
    raw_value: float | None
    unit: str
    status: str
    reason: str | None
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _id(item: Any, name: str) -> str | None:
    value = _value(item, name)
    return str(value) if value is not None else None


def _month(value: date) -> tuple[int, int]:
    return value.year, value.month


def _months(transactions: Iterable[Any]) -> list[tuple[int, int]]:
    dates = [_value(item, "date") for item in transactions]
    dates = [value for value in dates if isinstance(value, date)]
    if not dates:
        return []
    first, last = min(dates), max(dates)
    result: list[tuple[int, int]] = []
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        result.append((year, month))
        month += 1
        if month == 13:
            year, month = year + 1, 1
    complete = [
        item
        for item in result
        if first <= date(item[0], item[1], 1)
        and last >= date(item[0], item[1], monthrange(item[0], item[1])[1])
    ]
    return complete if len(complete) >= 3 else result


def _month_data(
    transactions: Iterable[Any],
) -> tuple[list[tuple[int, int]], dict[tuple[int, int], list[Any]]]:
    rows = list(transactions)
    months = _months(rows)
    grouped = {month: [] for month in months}
    for transaction in rows:
        transaction_month = _value(transaction, "date")
        if _month(transaction_month) in grouped:
            grouped[_month(transaction_month)].append(transaction)
    return months, grouped


def _evidence(items: Iterable[Any], id_name: str = "txn_id") -> dict[str, Any]:
    ids = []
    for item in items:
        item_id = _id(item, id_name)
        if item_id:
            ids.append(item_id)
    truncated = len(ids) > 500
    key = {
        "txn_id": "txn_ids",
        "id": "account_ids",
    }.get(id_name, f"{id_name}s")
    return {
        "ids": ids[-500:] if truncated else ids,
        key: ids[-500:] if truncated else ids,
        "total_count": len(ids),
        "truncated": truncated,
    }


def _result(
    key: str,
    raw_value: float | None,
    unit: str,
    status: str,
    reason: str | None,
    evidence: dict[str, Any],
) -> MetricResult:
    return MetricResult(key, LABELS[key], raw_value, unit, status, reason, evidence)


def _income_expenses(transactions: Iterable[Any]) -> tuple[dict[tuple[int, int], int], dict[tuple[int, int], int]]:
    months, grouped = _month_data(transactions)
    income: dict[tuple[int, int], int] = {month: 0 for month in months}
    expenses: dict[tuple[int, int], int] = {month: 0 for month in months}
    for month, rows in grouped.items():
        for transaction in rows:
            amount = int(_value(transaction, "amount_paise", 0))
            category = _value(transaction, "category", "")
            if amount > 0 and category in INCOME_CATEGORIES and not _value(transaction, "is_self_transfer", False):
                income[month] += amount
            elif (
                amount < 0
                and not _value(transaction, "is_self_transfer", False)
                and category not in EXCLUDED_EXPENSE_CATEGORIES
            ):
                expenses[month] += -amount
    return income, expenses


def calculate_p2p_outflow_share(transactions: Iterable[Any]) -> float:
    rows = list(transactions)
    _, grouped = _month_data(rows)
    total = 0
    p2p = 0
    for month_rows in grouped.values():
        for transaction in month_rows:
            amount = int(_value(transaction, "amount_paise", 0))
            if (
                amount < 0
                and not _value(transaction, "is_self_transfer", False)
                and _value(transaction, "category") not in EXCLUDED_EXPENSE_CATEGORIES
            ):
                total += -amount
                if _value(transaction, "category") == "Transfers":
                    p2p += -amount
    return p2p / total if total else 0.0


def calculate_savings_rate(transactions: Iterable[Any]) -> MetricResult:
    rows = list(transactions)
    income, expenses = _income_expenses(rows)
    if not income or sum(income.values()) == 0:
        return _result("savings_rate", None, "ratio", "not_available", "Income is zero or missing.", _evidence(rows))
    values = [(income[month] - expenses[month]) / income[month] for month in income if income[month]]
    return _result("savings_rate", mean(values), "ratio", "ok", None, _evidence(rows))


def _debt_payments(transactions: list[Any], loans: list[Any], cards: list[Any]) -> tuple[dict[tuple[int, int], int], dict[str, Any]]:
    months, grouped = _month_data(transactions)
    payments = {month: 0 for month in months}
    evidence: list[Any] = []
    has_loan_transaction = False
    for month, rows in grouped.items():
        for transaction in rows:
            if _value(transaction, "amount_paise", 0) < 0 and _value(transaction, "category") == "EMI/Loan":
                payments[month] += -int(_value(transaction, "amount_paise"))
                evidence.append(transaction)
                has_loan_transaction = True
    if months:
        for card in cards:
            for month in months:
                payments[month] += int(_value(card, "min_due_paise", 0))
            evidence.append(card)
        if not has_loan_transaction:
            for loan in loans:
                for month in months:
                    payments[month] += int(_value(loan, "emi_paise", 0))
                evidence.append(loan)
    txn_ids = [_id(item, "txn_id") for item in evidence if _id(item, "txn_id")]
    card_ids = [_id(card, "id") for card in cards if _id(card, "id")]
    loan_ids = [_id(loan, "id") for loan in loans if _id(loan, "id")]
    all_ids = txn_ids + card_ids + loan_ids
    return payments, {
        "txn_ids": txn_ids[-500:],
        "card_ids": card_ids[-500:],
        "loan_ids": loan_ids[-500:],
        "account_ids": [],
        "total_count": len(all_ids),
        "truncated": len(all_ids) > 500,
    }


def calculate_debt_to_income(transactions: Iterable[Any], loans: list[Any] | None = None, cards: list[Any] | None = None) -> MetricResult:
    rows, loans, cards = list(transactions), loans or [], cards or []
    income, _ = _income_expenses(rows)
    if not income or sum(income.values()) == 0:
        return _result("debt_to_income", None, "ratio", "not_available", "Income is zero or missing.", _evidence(rows))
    payments, evidence = _debt_payments(rows, loans, cards)
    value = mean(payments.values()) / mean(income.values())
    return _result("debt_to_income", value, "ratio", "ok", None, evidence)


def calculate_emergency_runway(transactions: Iterable[Any], accounts: list[Any] | None = None) -> MetricResult:
    rows, accounts = list(transactions), accounts or []
    _, expenses = _income_expenses(rows)
    average_expenses = mean(expenses.values()) if expenses else 0
    liquid = [account for account in accounts if _value(account, "type", "").lower() in {"savings", "current"}]
    if not liquid:
        return _result("emergency_runway_months", None, "months", "not_available", "No liquid account balance is recorded.", _evidence(rows))
    if average_expenses == 0:
        return _result("emergency_runway_months", None, "months", "not_available", "Average monthly expenses are zero.", _evidence(liquid, "id"))
    return _result("emergency_runway_months", sum(int(_value(account, "balance_paise", 0)) for account in liquid) / average_expenses, "months", "ok", None, _evidence(liquid, "id"))


def calculate_fixed_expense_ratio(transactions: Iterable[Any]) -> MetricResult:
    rows = list(transactions)
    income, _ = _income_expenses(rows)
    if not income or sum(income.values()) == 0:
        return _result("fixed_expense_ratio", None, "ratio", "not_available", "Income is zero or missing.", _evidence(rows))
    months, grouped = _month_data(rows)
    fixed = {
        month: sum(-int(_value(item, "amount_paise", 0)) for item in items if _value(item, "amount_paise", 0) < 0 and _value(item, "category") in FIXED_EXPENSE_CATEGORIES)
        for month, items in grouped.items()
    }
    return _result("fixed_expense_ratio", mean(fixed.values()) / mean(income.values()), "ratio", "ok", None, _evidence(rows))


def calculate_credit_utilisation(cards: list[Any]) -> MetricResult:
    cards = list(cards)
    evidence = _evidence(cards, "id")
    evidence["card_ids"] = evidence.pop("account_ids")
    if not cards:
        return _result("credit_utilisation", None, "ratio", "not_applicable", "No credit cards are recorded.", evidence)
    limits = sum(int(_value(card, "limit_paise", 0)) for card in cards)
    if limits == 0:
        return _result("credit_utilisation", None, "ratio", "not_available", "Credit card limits are zero or missing.", evidence)
    return _result("credit_utilisation", sum(int(_value(card, "balance_paise", 0)) for card in cards) / limits, "ratio", "ok", None, evidence)


def _coefficient(values: list[float]) -> float:
    average = mean(values)
    return 0.0 if average == 0 else sqrt(sum((value - average) ** 2 for value in values) / len(values)) / average


def calculate_spending_volatility(transactions: Iterable[Any]) -> MetricResult:
    rows = list(transactions)
    months, grouped = _month_data(rows)
    if len(months) < MIN_MONTHS_FOR_VARIABILITY:
        return _result("spending_volatility", None, "ratio", "not_available", "Fewer than three months of data are available.", _evidence(rows))
    values = [
        sum(-int(_value(item, "amount_paise", 0)) for item in grouped[month] if _value(item, "amount_paise", 0) < 0 and _value(item, "category") not in EXCLUDED_EXPENSE_CATEGORIES and _value(item, "category") not in FIXED_EXPENSE_CATEGORIES)
        for month in months
    ]
    return _result("spending_volatility", _coefficient([float(value) for value in values]), "ratio", "ok", None, _evidence(rows))


def calculate_income_stability(transactions: Iterable[Any]) -> MetricResult:
    rows = list(transactions)
    income, _ = _income_expenses(rows)
    values = [value for value in income.values() if value > 0]
    if len(values) < MIN_MONTHS_FOR_VARIABILITY:
        return _result("income_stability", None, "ratio", "not_available", "Fewer than three months with income are available.", _evidence(rows))
    return _result("income_stability", max(0.0, min(1.0, 1 - _coefficient([float(value) for value in values]))), "ratio", "ok", None, _evidence(rows))
