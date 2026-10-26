"""Pure scenario transformations for synthetic persona transaction data."""

from copy import deepcopy
from datetime import date
from typing import Iterable


Transaction = dict[str, object]


def _copy(data: Iterable[Transaction]) -> list[Transaction]:
    return deepcopy(list(data))


def stop_income(data: Iterable[Transaction], months: int) -> list[Transaction]:
    """Remove income transactions from the first ``months`` calendar months."""
    if months < 0:
        raise ValueError("months must be non-negative")
    result = _copy(data)
    if not result or months == 0:
        return result
    income_dates = sorted(
        {
            date.fromisoformat(str(row["date"]))
            for row in result
            if int(row["amount_paise"]) > 0
        }
    )
    cutoff = income_dates[0].replace(day=1)
    month_index = cutoff.month - 1 + months
    cutoff = date(cutoff.year + month_index // 12, month_index % 12 + 1, 1)
    return [
        row
        for row in result
        if not (
            int(row["amount_paise"]) > 0
            and date.fromisoformat(str(row["date"])) < cutoff
        )
    ]


def add_emi(
    data: Iterable[Transaction],
    amount_paise: int,
    description: str = "SCENARIO EMI",
) -> list[Transaction]:
    """Add a monthly EMI on the first transaction date of each month."""
    if amount_paise < 0:
        raise ValueError("amount_paise must be non-negative")
    result = _copy(data)
    months = sorted(
        {
            date.fromisoformat(str(row["date"])).replace(day=1)
            for row in result
        }
    )
    result.extend(
        {
            "date": month.isoformat(),
            "amount_paise": -amount_paise,
            "description": description,
        }
        for month in months
    )
    return result


def raise_expenses(data: Iterable[Transaction], percent: int | float) -> list[Transaction]:
    """Increase every outgoing transaction by ``percent`` without changing income."""
    if percent < 0:
        raise ValueError("percent must be non-negative")
    result = _copy(data)
    for row in result:
        amount = int(row["amount_paise"])
        if amount < 0:
            row["amount_paise"] = -(abs(amount) * (100 + percent) // 100)
    return result


def add_big_purchase(
    data: Iterable[Transaction],
    amount_paise: int,
    purchase_date: str | date,
    description: str = "SCENARIO BIG PURCHASE",
) -> list[Transaction]:
    """Append one purchase transaction on the supplied date."""
    if amount_paise < 0:
        raise ValueError("amount_paise must be non-negative")
    result = _copy(data)
    transaction_date = (
        purchase_date.isoformat()
        if isinstance(purchase_date, date)
        else date.fromisoformat(purchase_date).isoformat()
    )
    result.append(
        {
            "date": transaction_date,
            "amount_paise": -amount_paise,
            "description": description,
        }
    )
    return result
