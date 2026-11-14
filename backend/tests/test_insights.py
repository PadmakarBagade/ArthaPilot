from datetime import date
from app.insights.detector import (
    analyze_weekday_vs_weekend,
    detect_post_salary_spike,
    detect_month_end_squeeze,
    detect_duplicate_charges,
    detect_merchant_anomalies,
    detect_subscription_price_hikes,
    detect_overlapping_subscriptions,
    generate_insights,
)


def test_duplicate_charges_detection():
    txns = [
        {"txn_id": "t1", "date": "2024-05-10", "amount_paise": -29900, "merchant": "NETFLIX"},
        {"txn_id": "t2", "date": "2024-05-10", "amount_paise": -29900, "merchant": "NETFLIX"},
        {"txn_id": "t3", "date": "2024-05-11", "amount_paise": -15000, "merchant": "SWIGGY"},
    ]
    dups = detect_duplicate_charges(txns)
    assert len(dups) == 1
    assert dups[0]["type"] == "duplicate_charge"
    assert dups[0]["severity"] == "high"
    assert dups[0]["evidence_ids"] == ["t1", "t2"]
    assert dups[0]["data"]["amount_paise"] == 29900


def test_overlapping_subscriptions_detection():
    recurring = [
        {"id": "r1", "merchant": "NETFLIX", "amount_paise": 64900},
        {"id": "r2", "merchant": "AMAZON PRIME", "amount_paise": 29900},
        {"id": "r3", "merchant": "DISNEY HOTSTAR", "amount_paise": 14900},
        {"id": "r4", "merchant": "SPOTIFY", "amount_paise": 11900},
    ]
    overlaps = detect_overlapping_subscriptions(recurring)
    assert len(overlaps) == 1
    assert overlaps[0]["type"] == "overlapping_subscription"
    assert overlaps[0]["data"]["category"] == "Video Streaming"
    assert len(overlaps[0]["data"]["merchants"]) == 3
    assert overlaps[0]["evidence_ids"] == ["r1", "r2", "r3"]


def test_subscription_price_hikes_detection():
    recurring = [
        {"id": "r1", "merchant": "GYM", "txn_ids": ["t1", "t2", "t3"], "amount_paise": 250000}
    ]
    txns = [
        {"txn_id": "t1", "date": "2024-01-05", "amount_paise": -200000, "merchant": "GYM"},
        {"txn_id": "t2", "date": "2024-02-05", "amount_paise": -200000, "merchant": "GYM"},
        {"txn_id": "t3", "date": "2024-03-05", "amount_paise": -250000, "merchant": "GYM"},
    ]
    hikes = detect_subscription_price_hikes(recurring, txns)
    assert len(hikes) == 1
    assert hikes[0]["type"] == "subscription_price_hike"
    assert hikes[0]["data"]["old_paise"] == 200000
    assert hikes[0]["data"]["new_paise"] == 250000
    assert hikes[0]["data"]["hike_percent"] == 25


def test_weekday_vs_weekend_analysis():
    # 2024-05-08 is Wednesday (weekday), 2024-05-11 is Saturday (weekend)
    txns = [
        {"txn_id": f"w{i}", "date": "2024-05-08", "amount_paise": -50000, "category": "Dining"}
        for i in range(10)
    ] + [
        {"txn_id": f"we{i}", "date": "2024-05-11", "amount_paise": -150000, "category": "Dining"}
        for i in range(5)
    ]
    insight = analyze_weekday_vs_weekend(txns)
    assert insight is not None
    assert insight["type"] == "weekend_spending_spike"
    assert insight["data"]["ratio"] >= 2.0


def test_post_salary_spike_detection():
    income = {"salary": {"day_of_month": 1, "amount_paise": 8000000}}
    # Salary is on 1st. Post-salary spike on 2nd vs low spend on 15th
    txns = [
        {"txn_id": f"sp{i}", "date": "2024-05-02", "amount_paise": -200000, "category": "Shopping"}
        for i in range(5)
    ] + [
        {"txn_id": f"reg{i}", "date": "2024-05-15", "amount_paise": -50000, "category": "Shopping"}
        for i in range(10)
    ]
    insight = detect_post_salary_spike(txns, income)
    assert insight is not None
    assert insight["type"] == "post_salary_spike"
    assert insight["data"]["ratio"] >= 2.0


def test_month_end_squeeze_detection():
    # Regular spend mid month (₹2,000 avg) vs tiny spend end month (₹400 avg)
    txns = [
        {"txn_id": f"mid{i}", "date": "2024-05-10", "amount_paise": -200000, "category": "Food"}
        for i in range(10)
    ] + [
        {"txn_id": f"end{i}", "date": "2024-05-28", "amount_paise": -40000, "category": "Food"}
        for i in range(5)
    ]
    insight = detect_month_end_squeeze(txns)
    assert insight is not None
    assert insight["type"] == "month_end_squeeze"
    assert insight["data"]["drop_percent"] >= 50


def test_merchant_anomalies_detection():
    txns = [
        {"txn_id": "m1", "date": "2024-01-01", "amount_paise": -50000, "merchant": "ZOMATO"},
        {"txn_id": "m2", "date": "2024-01-10", "amount_paise": -55000, "merchant": "ZOMATO"},
        {"txn_id": "m3", "date": "2024-01-20", "amount_paise": -52000, "merchant": "ZOMATO"},
        {"txn_id": "m4", "date": "2024-02-01", "amount_paise": -180000, "merchant": "ZOMATO"},  # Anomaly!
    ]
    anomalies = detect_merchant_anomalies(txns)
    assert len(anomalies) == 1
    assert anomalies[0]["type"] == "merchant_anomaly"
    assert anomalies[0]["evidence_ids"] == ["m4"]


def test_generate_insights_combines_detectors():
    txns = [
        {"txn_id": "t1", "date": "2024-05-10", "amount_paise": -29900, "merchant": "NETFLIX"},
        {"txn_id": "t2", "date": "2024-05-10", "amount_paise": -29900, "merchant": "NETFLIX"},
    ]
    insights = generate_insights(txns)
    assert len(insights) >= 1
    assert any(i["type"] == "duplicate_charge" for i in insights)

