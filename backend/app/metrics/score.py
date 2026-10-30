from __future__ import annotations

from calendar import monthrange
from datetime import date
from typing import Any

from .config import LABELS, MAPPINGS, MAX_MONTHS, WEIGHTS
from .functions import (
    MetricResult,
    _month_data,
    calculate_credit_utilisation,
    calculate_debt_to_income,
    calculate_emergency_runway,
    calculate_fixed_expense_ratio,
    calculate_income_stability,
    calculate_p2p_outflow_share,
    calculate_savings_rate,
    calculate_spending_volatility,
)


def subscore(key: str, raw_value: float) -> float:
    mapping = MAPPINGS[key]
    points = mapping.points
    if mapping.lower_is_better:
        points = tuple((value, score) for value, score in points)
    if raw_value <= points[0][0]:
        return points[0][1]
    if raw_value >= points[-1][0]:
        return points[-1][1]
    for (left_value, left_score), (right_value, right_score) in zip(points, points[1:]):
        if left_value <= raw_value <= right_value:
            fraction = (raw_value - left_value) / (right_value - left_value)
            return left_score + fraction * (right_score - left_score)
    return points[-1][1]


def _format_raw(metric: MetricResult) -> str:
    if metric.raw_value is None:
        return "not available"
    if metric.unit == "ratio":
        return f"{metric.raw_value:.0%}"
    if metric.unit == "months":
        return f"{metric.raw_value:.1f} months"
    return f"{metric.raw_value:.2f}"


def _reason(key: str, metric: MetricResult, points_lost: float) -> str:
    if metric.status != "ok":
        return metric.reason or "This metric is not available."
    targets = {
        "savings_rate": "20% savings",
        "debt_to_income": "under 36% debt payments",
        "emergency_runway_months": "6 months",
        "fixed_expense_ratio": "under 50% fixed expenses",
        "credit_utilisation": "under 30% utilisation",
        "spending_volatility": "10% volatility",
        "income_stability": "100% stability",
    }
    return f"{metric.plain_label}: {_format_raw(metric)}. Target is {targets[key]}. This cost you {points_lost:.1f} points."


def _window_metadata(transactions: list[Any], requested_months: int) -> tuple[int, list[str], date | None, date | None]:
    months, _ = _month_data(transactions)
    if not months:
        return 0, [], None, None
    selected = months[-min(MAX_MONTHS, requested_months):]
    first_date = min(item.date for item in transactions if isinstance(getattr(item, "date", None), date)) if transactions and not isinstance(transactions[0], dict) else min(item["date"] for item in transactions)
    last_date = max(item.date for item in transactions if isinstance(getattr(item, "date", None), date)) if transactions and not isinstance(transactions[0], dict) else max(item["date"] for item in transactions)
    complete = [
        month for month in months
        if first_date <= date(month[0], month[1], 1)
        and last_date >= date(month[0], month[1], monthrange(month[0], month[1])[1])
    ]
    partial = [f"{year:04d}-{month:02d}" for year, month in selected if (year, month) not in complete]
    return len(selected), partial, date(selected[0][0], selected[0][1], 1), date(selected[-1][0], selected[-1][1], monthrange(selected[-1][0], selected[-1][1])[1])


def compute_health_score(
    transactions: list[Any],
    loans: list[Any] | None = None,
    cards: list[Any] | None = None,
    accounts: list[Any] | None = None,
    requested_months: int = MAX_MONTHS,
) -> dict[str, Any]:
    loans, cards, accounts = loans or [], cards or [], accounts or []
    rows = list(transactions)
    months_used, partial_months, window_start, window_end = _window_metadata(rows, requested_months)
    if window_start and window_end:
        rows = [
            row for row in rows
            if window_start <= (row.get("date") if isinstance(row, dict) else row.date) <= window_end
        ]
    metrics = {
        "savings_rate": calculate_savings_rate(rows),
        "debt_to_income": calculate_debt_to_income(rows, loans, cards),
        "emergency_runway_months": calculate_emergency_runway(rows, accounts),
        "fixed_expense_ratio": calculate_fixed_expense_ratio(rows),
        "credit_utilisation": calculate_credit_utilisation(cards),
        "spending_volatility": calculate_spending_volatility(rows),
        "income_stability": calculate_income_stability(rows),
    }
    available_weight = sum(WEIGHTS.get(key, 0) for key, metric in metrics.items() if metric.status == "ok")
    coverage = available_weight / 100
    metric_payload: dict[str, Any] = {}
    weighted_points = 0.0
    issues: list[tuple[float, str]] = []
    for key, metric in metrics.items():
        if metric.status == "ok" and key in MAPPINGS:
            score = max(0.0, min(100.0, subscore(key, metric.raw_value or 0.0)))
            effective_weight = WEIGHTS.get(key, 0) / available_weight if available_weight else 0.0
            points_earned = effective_weight * score
            points_lost = effective_weight * (100 - score)
            weighted_points += points_earned
            issues.append((points_lost, key))
        elif metric.status == "ok":
            score = None
            effective_weight = 0.0
            points_earned = 0.0
            points_lost = 0.0
        else:
            score = None
            effective_weight = 0.0
            points_earned = 0.0
            points_lost = 0.0
        metric_payload[key] = {
            **metric.to_dict(),
            "sub_score": score,
            "effective_weight": effective_weight,
            "points_earned": points_earned,
            "points_lost": points_lost,
            "reason": _reason(key, metric, points_lost),
        }
    indicative_score = round(weighted_points, 2) if available_weight else None
    if indicative_score is None:
        band = "Not enough data"
    elif coverage < 0.5:
        band = "Not enough data"
    elif indicative_score >= 80:
        band = "Strong"
    elif indicative_score >= 60:
        band = "Good"
    elif indicative_score >= 40:
        band = "Fair"
    else:
        band = "Poor"
    top_issues = [key for _, key in sorted(issues, reverse=True)[:2]]
    p2p_outflow_share = calculate_p2p_outflow_share(rows)
    summary = (
        "Coverage is below 50%, so no headline score is shown."
        if coverage < 0.5
        else "Score calculated from available metrics."
    )
    if p2p_outflow_share > 0.30:
        summary += " More than 30% of expenses are payments to individuals and cannot be classified."
    return {
        "total_score": indicative_score if coverage >= 0.5 else None,
        "indicative_score": indicative_score,
        "band": band,
        "score_coverage": coverage,
        "months_used": months_used,
        "partial_months": partial_months,
        "window_start": window_start,
        "window_end": window_end,
        "metrics": metric_payload,
        "top_issues": top_issues,
        "summary": summary,
        "p2p_outflow_share": p2p_outflow_share,
        "fixed_expense_ratio": metric_payload["fixed_expense_ratio"],
    }
