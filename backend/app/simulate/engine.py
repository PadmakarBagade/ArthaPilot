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
    elif kind == "move_savings":
        amount = int(action.get("amount_paise", 0))
        if amount < 0:
            raise ValueError("amount_paise must not be negative")
        # Adds monthly savings outflow to transactions
        result.setdefault("transactions", []).append({
            "txn_id": "sim-savings",
            "amount_paise": -amount,
            "category": "Investment/SIP",
        })
    elif kind == "delay_purchase":
        # Shifts outflow or reduces immediate pressure
        pass
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
    # 1. Subscriptions cancellation candidate
    recurring = state.get("recurring_items", [])
    for item in recurring:
        merchant = str(item.get("merchant", ""))
        amount = abs(int(item.get("amount_paise", 0)))
        if amount > 0:
            candidates.append({
                "action": {"type": "cancel_subscription", "merchant": merchant},
                "impact_paise": amount,
                "effort_score": 2,
                "reason": f"Cancel unused {merchant} subscription to save ₹{amount // 100:,}/month.",
            })

    # 2. Category cuts
    for category in ("Food Delivery", "Dining", "Shopping", "Subscriptions"):
        amount = _category_expense(state, category)
        if amount:
            action = {"type": "cut_category", "category": category, "percent": 20}
            result = simulate(state, action)
            candidates.append({
                "action": action,
                "impact_paise": result["delta"]["surplus_paise"],
                "effort_score": 3 if category == "Subscriptions" else 6,
                "reason": f"Cutting {category} by 20% increases monthly surplus by ₹{result['delta']['surplus_paise'] // 100:,}.",
            })

    # 3. Debt prepayment if loans exist
    loans = state.get("loans", [])
    total_debt = sum(int(l.get("outstanding_paise", 0)) for l in loans)
    if total_debt > 0:
        candidates.append({
            "action": {"type": "extra_debt_payment", "amount_paise": 500000},
            "impact_paise": 500000,
            "effort_score": 4,
            "reason": "Pay extra ₹5,000/month towards high-interest debt to eliminate interest and reduce tenure.",
        })

    candidates.sort(key=lambda item: (item["impact_paise"] / item["effort_score"], item["impact_paise"]), reverse=True)
    return {
        "best_move": candidates[0] if candidates else None,
        "alternatives": candidates[1:5],
        "evidence_formula": "impact = simulated surplus delta / effort score",
    }


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


def _simulate_debt_schedule(debts: list[dict[str, Any]], extra_monthly_paise: int, strategy: str = "avalanche") -> dict[str, Any]:
    """Pure amortisation engine for debt payoff."""
    active_debts = [
        {
            "id": str(d.get("id", "")),
            "type": str(d.get("type", "Debt")),
            "balance": int(d.get("outstanding_paise", 0)),
            "apr": float(d.get("rate_apr", d.get("apr", 0))),
            "emi": int(d.get("emi_paise", d.get("min_due_paise", 0))),
        }
        for d in debts
        if int(d.get("outstanding_paise", 0)) > 0
    ]

    if not active_debts:
        return {"months": 0, "total_interest_paise": 0, "order": []}

    total_interest = 0
    month = 0
    payoff_order: list[str] = []

    # Sort priorities
    def sort_key(item: dict[str, Any]):
        if strategy == "avalanche":
            return -item["apr"], item["balance"]
        return item["balance"], -item["apr"]

    while any(d["balance"] > 0 for d in active_debts) and month < 360:
        month += 1
        # 1. Accrue interest
        for d in active_debts:
            if d["balance"] > 0:
                monthly_interest = round(d["balance"] * (d["apr"] / 100) / 12)
                total_interest += monthly_interest
                d["balance"] += monthly_interest

        # 2. Pay minimum EMIs
        for d in active_debts:
            if d["balance"] > 0:
                payment = min(d["balance"], max(d["emi"], 0))
                d["balance"] -= payment
                if d["balance"] == 0 and d["id"] not in payoff_order:
                    payoff_order.append(d["id"])

        # 3. Pay extra amount
        extra_left = extra_monthly_paise
        sorted_debts = sorted([d for d in active_debts if d["balance"] > 0], key=sort_key)
        for d in sorted_debts:
            if extra_left <= 0:
                break
            payment = min(d["balance"], extra_left)
            d["balance"] -= payment
            extra_left -= payment
            if d["balance"] == 0 and d["id"] not in payoff_order:
                payoff_order.append(d["id"])

    return {
        "months": month,
        "total_interest_paise": total_interest,
        "order": payoff_order,
    }


def debt_payoff_plan(
    loans: list[dict[str, Any]],
    cards: list[dict[str, Any]] = (),
    extra_monthly_paise: int = 0,
    strategy: str = "avalanche",
) -> dict[str, Any]:
    """Calculate avalanche and snowball payoff plans with interest and months saved."""
    all_debts = list(loans) + list(cards)
    if not all_debts:
        return {
            "strategy": strategy,
            "baseline_months": 0,
            "accelerated_months": 0,
            "months_saved": 0,
            "baseline_interest_paise": 0,
            "accelerated_interest_paise": 0,
            "interest_saved_paise": 0,
            "payoff_order": [],
            "formula": "monthly_interest = balance * APR / 12",
        }

    baseline = _simulate_debt_schedule(all_debts, extra_monthly_paise=0, strategy=strategy)
    accelerated = _simulate_debt_schedule(all_debts, extra_monthly_paise=extra_monthly_paise, strategy=strategy)

    months_saved = max(0, baseline["months"] - accelerated["months"])
    interest_saved = max(0, baseline["total_interest_paise"] - accelerated["total_interest_paise"])

    return {
        "strategy": strategy,
        "baseline_months": baseline["months"],
        "accelerated_months": accelerated["months"],
        "months_saved": months_saved,
        "baseline_interest_paise": baseline["total_interest_paise"],
        "accelerated_interest_paise": accelerated["total_interest_paise"],
        "interest_saved_paise": interest_saved,
        "payoff_order": accelerated["order"],
        "formula": "Monthly interest = balance * (APR / 100) / 12. Extra payments apply to top-priority debt principal.",
        "evidence_debt_ids": [str(d.get("id")) for d in all_debts if d.get("id")],
    }
