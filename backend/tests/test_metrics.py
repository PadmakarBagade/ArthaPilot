from datetime import date

from app.metrics import (
    calculate_credit_utilisation,
    calculate_debt_to_income,
    calculate_emergency_runway,
    calculate_fixed_expense_ratio,
    calculate_income_stability,
    calculate_p2p_outflow_share,
    calculate_savings_rate,
    calculate_spending_volatility,
    compute_health_score,
)
from app.metrics.score import subscore
from app.db import SessionLocal
from app.models import User
from app.main import app
from fastapi.testclient import TestClient


def txn(txn_id, day, amount, category, self_transfer=False):
    return {
        "txn_id": txn_id,
        "date": date.fromisoformat(day),
        "amount_paise": amount,
        "category": category,
        "is_self_transfer": self_transfer,
    }


def three_month_transactions():
    rows = []
    for month in ("2026-01", "2026-02", "2026-03"):
        rows.extend(
            [
                txn(f"{month}-income", f"{month}-01", 100_000, "Salary"),
                txn(f"{month}-rent", f"{month}-02", -20_000, "Rent"),
                txn(f"{month}-food", f"{month}-03", -60_000, "Dining"),
                txn(f"{month}-transfer", f"{month}-04", -50_000, "Transfers"),
                txn(f"{month}-sip", f"{month}-05", -10_000, "Investment/SIP"),
                txn(f"{month}-card", f"{month}-06", -5_000, "Credit Card Payment"),
            ]
        )
    return rows


def test_hand_calculated_metrics_and_exclusions():
    rows = three_month_transactions()
    # Income is 100000 paise; expenses are 20000 + 60000 + 50000 = 130000 paise.
    # Transfers now count as person-to-person spending, so savings rate is -30000 / 100000 = -0.30.
    assert calculate_savings_rate(rows).raw_value == -0.30
    assert calculate_fixed_expense_ratio(rows).raw_value == 0.20
    assert calculate_debt_to_income(rows, [], []).raw_value == 0
    assert calculate_spending_volatility(rows).raw_value == 0
    # Person-to-person outflows are 50000 / 130000 = 0.384615..., excluding SIP and card payment.
    assert calculate_p2p_outflow_share(rows) == 50_000 / 130_000


def test_debt_runway_cards_and_stability():
    rows = three_month_transactions()
    cards = [{"id": "card-1", "limit_paise": 100_000, "balance_paise": 30_000, "min_due_paise": 10_000}]
    accounts = [{"id": "account-1", "type": "savings", "balance_paise": 240_000}]
    # Debt is 10000 paise per month; DTI is 10000 / 100000 = 0.10.
    assert calculate_debt_to_income(rows, [], cards).raw_value == 0.10
    # Average expenses are 130000 paise; 240000 / 130000 = 1.846153... months.
    assert calculate_emergency_runway(rows, accounts).raw_value == 240_000 / 130_000
    assert calculate_credit_utilisation(cards).raw_value == 0.30
    assert calculate_income_stability(rows).raw_value == 1


def test_availability_and_score_renormalisation():
    result = compute_health_score(three_month_transactions(), [], [], [])
    assert result["total_score"] is not None
    assert result["metrics"]["credit_utilisation"]["status"] == "not_applicable"
    assert result["score_coverage"] == 0.65
    assert sum(
        metric["effective_weight"]
        for metric in result["metrics"].values()
        if metric["status"] == "ok"
    ) == 1


def test_thin_coverage_hides_headline_score():
    rows = [
        txn("income", "2026-01-01", 100_000, "Salary"),
        txn("spend", "2026-01-02", -20_000, "Dining"),
    ]
    result = compute_health_score(rows, [], [], [])
    # Savings rate (25) and zero debt-to-income (20) are available: coverage is 45 / 100 = 0.45.
    assert result["score_coverage"] == 0.45
    assert result["total_score"] is None
    assert result["indicative_score"] is not None
    assert result["band"] == "Not enough data"


def test_subscores_are_clamped_and_monotonic():
    for key in ("savings_rate", "emergency_runway_months", "income_stability"):
        points = [subscore(key, value) for value in (-100, -1, 0, 0.5, 1, 100)]
        assert points == sorted(points)
        assert points[0] >= 0 and points[-1] <= 100
    for key in ("debt_to_income", "credit_utilisation", "spending_volatility"):
        points = [subscore(key, value) for value in (-100, 0, 0.1, 0.5, 1, 100)]
        assert points == sorted(points, reverse=True)


def test_evidence_truncates_to_500_ids():
    rows = [
        txn(f"t-{index}", f"2026-{(index % 3) + 1:02d}-01", 100, "Salary")
        for index in range(600)
    ]
    evidence = calculate_savings_rate(rows).evidence
    assert evidence["total_count"] == 600
    assert len(evidence["ids"]) == 500
    assert evidence["truncated"] is True
    assert set(evidence["txn_ids"]).issubset({row["txn_id"] for row in rows})


def test_edge_case_availability_states():
    zero_income = [txn("zero", "2026-01-01", -100, "Dining")]
    assert calculate_savings_rate(zero_income).status == "not_available"
    assert calculate_debt_to_income(zero_income, [], []).status == "not_available"
    assert calculate_credit_utilisation([]).status == "not_applicable"
    assert calculate_emergency_runway(zero_income, []).status == "not_available"
    one_month = [txn("one", "2026-01-01", 100, "Salary")]
    two_months = [
        txn("two-a", "2026-01-01", 100, "Salary"),
        txn("two-b", "2026-02-01", 100, "Salary"),
    ]
    assert calculate_spending_volatility(one_month).status == "not_available"
    assert calculate_income_stability(two_months).status == "not_available"
    negative = [txn("negative", "2026-01-01", 100, "Salary"), txn("spend", "2026-01-02", -200, "Dining")]
    assert calculate_savings_rate(negative).raw_value == -1


def test_one_partial_month_is_reported_without_dropping_rows():
    rows = [
        txn("income", "2026-04-10", 100_000, "Salary"),
        txn("spend", "2026-04-11", -20_000, "Dining"),
    ]
    report = compute_health_score(rows, [], [], [])
    assert report["months_used"] == 1
    assert len(report["partial_months"]) == 1


def test_runway_is_available_and_ordered_by_story_balance():
    rows = [
        txn("income", "2026-01-01", 100_000, "Salary"),
        txn("spend", "2026-01-02", -50_000, "Dining"),
    ]
    reports = {
        "sam": compute_health_score(rows, accounts=[{"id": "sam", "type": "savings", "balance_paise": 1_000}]),
        "rahul": compute_health_score(rows, accounts=[{"id": "rahul", "type": "savings", "balance_paise": 2_000}]),
        "meera": compute_health_score(rows, accounts=[{"id": "meera", "type": "savings", "balance_paise": 3_000}]),
        "arjun": compute_health_score(rows, accounts=[{"id": "arjun", "type": "current", "balance_paise": 4_000}]),
        "priya": compute_health_score(rows, accounts=[{"id": "priya", "type": "savings", "balance_paise": 5_000}]),
    }
    runway = {
        key: report["metrics"]["emergency_runway_months"]
        for key, report in reports.items()
    }
    assert all(value["status"] == "ok" for value in runway.values())
    assert reports["sam"]["metrics"]["emergency_runway_months"]["sub_score"] < reports["priya"]["metrics"]["emergency_runway_months"]["sub_score"]
    assert reports["priya"]["metrics"]["emergency_runway_months"]["raw_value"] > reports["sam"]["metrics"]["emergency_runway_months"]["raw_value"]
    assert all(
        reports[left]["metrics"]["emergency_runway_months"]["sub_score"]
        <= reports[right]["metrics"]["emergency_runway_months"]["sub_score"]
        for left, right in zip(("sam", "rahul", "meera", "arjun"), ("rahul", "meera", "arjun", "priya"))
    )


def test_health_api_unknown_and_empty_user():
    client = TestClient(app)
    assert client.get("/users/does-not-exist/health").status_code == 404
    with SessionLocal() as session:
        if session.get(User, "empty-metrics-user") is None:
            session.add(User(id="empty-metrics-user", name="Empty", source="synthetic"))
            session.commit()
    response = client.get("/users/empty-metrics-user/health")
    assert response.status_code == 200
    assert response.json()["total_score"] is None
    assert all(item["status"] != "ok" for item in response.json()["metrics"].values())
