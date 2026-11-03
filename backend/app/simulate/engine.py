from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any


def _monthly_expense(state: dict[str, Any]) -> int:
    transactions = state.get("transactions", [])
    expenses = [
        abs(int(row.get("amount_paise", 0)))
        for row in transactions
        if int(row.get("amount_paise", 0)) < 0
        and row.get("category") not in {"Credit Card Payment", "Investment/SIP"}
    ]
    return round(sum(expenses) / max(1, state.get("months", 1)))


def _category_expense(state: dict[str, Any], category: str) -> int:
    return sum(
        abs(int(row.get("amount_paise", 0)))
        for row in state.get("transactions", [])
        if row.get("category") == category and int(row.get("amount_paise", 0)) < 0
    )


def _apply_action(state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(state)
    kind = action.get("type")
    if kind == "cut_category":
        category = str(action["category"])
        percent = int(action["percent"])
        if not 0 <= percent <= 100:
            raise ValueError("percent must be between 0 and 100")
        for row in result.get("transactions", []):
            if row.get("category") == category and int(row.get("amount_paise", 0)) < 0:
                row["amount_paise"] = round(int(row["amount_paise"]) * (100 - percent) / 100)
    elif kind == "cancel_subscription":
        merchant = str(action["merchant"]).upper()
        result["recurring_items"] = [
            item for item in result.get("recurring_items", [])
            if str(item.get("merchant", "")).upper() != merchant
        ]
    elif kind == "extra_debt_payment":
        amount = int(action["amount_paise"])
        if amount < 0:
            raise ValueError("amount_paise must not be negative")
        remaining = amount
        for loan in sorted(result.get("loans", []), key=lambda item: float(item.get("rate_apr", 0)), reverse=True):
            applied = min(remaining, int(loan.get("outstanding_paise", 0)))
            loan["outstanding_paise"] = int(loan.get("outstanding_paise", 0)) - applied
            remaining -= applied
            if remaining == 0:
                break
    else:
        raise ValueError(f"unsupported action type: {kind}")
    return result


def _summary(state: dict[str, Any]) -> dict[str, Any]:
    income = sum(
        int(row.get("amount_paise", 0))
        for row in state.get("transactions", [])
        if int(row.get("amount_paise", 0)) > 0
    )
    expenses = sum(
        abs(int(row.get("amount_paise", 0)))
        for row in state.get("transactions", [])
        if int(row.get("amount_paise", 0)) < 0
        and row.get("category") not in {"Credit Card Payment", "Investment/SIP"}
    )
    return {
        "income_paise": income,
        "expenses_paise": expenses,
        "surplus_paise": income - expenses,
        "formula": "surplus_paise = sum(credits) - sum(included debit amounts)",
    }


def simulate(state: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    before = _summary(state)
    after_state = _apply_action(state, action)
    after = _summary(after_state)
    return {
        "action": action,
        "before": before,
        "after": after,
        "delta": {
            "surplus_paise": after["surplus_paise"] - before["surplus_paise"],
            "expenses_paise": after["expenses_paise"] - before["expenses_paise"],
        },
        "evidence": {
            "transaction_ids": [
                str(row.get("txn_id"))
                for row in state.get("transactions", [])
                if row.get("txn_id") is not None
            ],
            "formula": after["formula"],
        },
    }


def rank_actions(state: dict[str, Any]) -> dict[str, Any]:
    candidates = []
    for category in ("Food Delivery", "Dining", "Shopping", "Subscriptions"):
        amount = _category_expense(state, category)
        if amount:
            action = {"type": "cut_category", "category": category, "percent": 20}
            result = simulate(state, action)
            candidates.append({
                "action": action,
                "impact_paise": result["delta"]["surplus_paise"],
                "effort_score": 3 if category == "Subscriptions" else 6,
                "reason": f"Cutting {category} by 20% increases monthly surplus.",
            })
    candidates.sort(key=lambda item: (item["impact_paise"] / item["effort_score"], item["impact_paise"]), reverse=True)
    return {"best_move": candidates[0] if candidates else None, "alternatives": candidates[1:], "evidence_formula": "impact = simulated surplus delta / effort score"}


def affordability(state: dict[str, Any], amount_paise: int, purchase_date: date | None = None) -> dict[str, Any]:
    if amount_paise <= 0:
        raise ValueError("amount_paise must be positive")
    monthly_surplus = _summary(state)["surplus_paise"] // max(1, state.get("months", 1))
    liquid = sum(int(account.get("balance_paise", 0)) for account in state.get("accounts", []) if account.get("type") in {"savings", "current"})
    after_balance = liquid - amount_paise
    safe_threshold = max(0, _monthly_expense(state) // 4)
    verdict = "Yes" if after_balance >= safe_threshold and monthly_surplus >= 0 else "Risky" if monthly_surplus >= 0 else "No"
    return {
        "verdict": verdict,
        "amount_paise": amount_paise,
        "balance_before_paise": liquid,
        "balance_after_paise": after_balance,
        "safe_threshold_paise": safe_threshold,
        "safer_alternative": "Wait until the next income cycle or choose a lower-cost option." if verdict != "Yes" else None,
        "formula": "balance_after = liquid_balance - purchase_amount; safe_threshold = average_monthly_expense / 4",
        "purchase_date": purchase_date,
    }


def goal_plan(state: dict[str, Any], target_paise: int, deadline: date, today: date | None = None) -> dict[str, Any]:
    if target_paise <= 0:
        raise ValueError("target_paise must be positive")
    today = today or date.today()
    months = max(1, (deadline.year - today.year) * 12 + deadline.month - today.month)
    required = (target_paise + months - 1) // months
    surplus = _summary(state)["surplus_paise"] // max(1, state.get("months", 1))
    return {
        "target_paise": target_paise,
        "deadline": deadline,
        "months": months,
        "required_monthly_paise": required,
        "current_monthly_surplus_paise": surplus,
        "feasible": surplus >= required,
        "formula": "required_monthly = ceil(target_paise / months_until_deadline)",
    }
