from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import median
from typing import Any, Iterable


def _get(item: Any, key: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(key, default)
    return getattr(item, key, default)


def _as_date(value: Any) -> date:
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def analyze_weekday_vs_weekend(transactions: Iterable[Any]) -> dict[str, Any] | None:
    """Compare weekday vs weekend variable spending."""
    weekday_spends: list[int] = []
    weekend_spends: list[int] = []
    weekday_txns: list[str] = []
    weekend_txns: list[str] = []

    for txn in transactions:
        amount = int(_get(txn, "amount_paise", 0))
        if amount >= 0 or bool(_get(txn, "is_recurring", False)) or bool(_get(txn, "is_self_transfer", False)):
            continue
        category = str(_get(txn, "category", ""))
        if category in {"Credit Card Payment", "Investment/SIP", "EMI/Loan"}:
            continue

        txn_date = _as_date(_get(txn, "date"))
        txn_id = str(_get(txn, "txn_id", ""))
        val = abs(amount)

        if txn_date.weekday() in (5, 6):  # Saturday, Sunday
            weekend_spends.append(val)
            if txn_id:
                weekend_txns.append(txn_id)
        else:
            weekday_spends.append(val)
            if txn_id:
                weekday_txns.append(txn_id)

    if not weekday_spends or not weekend_spends:
        return None

    avg_weekday = sum(weekday_spends) // max(1, len(weekday_spends))
    avg_weekend = sum(weekend_spends) // max(1, len(weekend_spends))

    if avg_weekday > 0 and avg_weekend > int(avg_weekday * 1.3):
        ratio = round(avg_weekend / avg_weekday, 1)
        weekday_rs = avg_weekday // 100
        weekend_rs = avg_weekend // 100
        return {
            "type": "weekend_spending_spike",
            "title": "Weekend Spending Spike",
            "message": f"Your weekend spending averages ₹{weekend_rs:,} per transaction, {ratio}x higher than weekdays (₹{weekday_rs:,}).",
            "severity": "medium",
            "evidence_ids": weekend_txns[:10],
            "data": {
                "avg_weekday_paise": avg_weekday,
                "avg_weekend_paise": avg_weekend,
                "ratio": ratio,
            },
        }
    return None


def detect_post_salary_spike(transactions: Iterable[Any], income: dict[str, Any] | None = None) -> dict[str, Any] | None:
    """Detect if spending significantly spikes in the 3 days after salary arrival."""
    salary_info = (income or {}).get("salary")
    if not salary_info:
        return None

    salary_day = int(salary_info.get("day_of_month", 1))
    spike_txns: list[str] = []
    spike_spends: list[int] = []
    regular_spends: list[int] = []

    for txn in transactions:
        amount = int(_get(txn, "amount_paise", 0))
        if amount >= 0 or bool(_get(txn, "is_recurring", False)) or bool(_get(txn, "is_self_transfer", False)):
            continue
        category = str(_get(txn, "category", ""))
        if category in {"Credit Card Payment", "Investment/SIP", "EMI/Loan"}:
            continue

        txn_date = _as_date(_get(txn, "date"))
        txn_id = str(_get(txn, "txn_id", ""))
        val = abs(amount)

        # Days after salary: [salary_day, salary_day + 1, salary_day + 2]
        days_after = (txn_date.day - salary_day) % 30
        if 0 <= days_after <= 3:
            spike_spends.append(val)
            if txn_id:
                spike_txns.append(txn_id)
        else:
            regular_spends.append(val)

    if not spike_spends or not regular_spends:
        return None

    avg_spike = sum(spike_spends) // len(spike_spends)
    avg_regular = sum(regular_spends) // len(regular_spends)

    if avg_regular > 0 and avg_spike > int(avg_regular * 1.5):
        ratio = round(avg_spike / avg_regular, 1)
        spike_rs = avg_spike // 100
        regular_rs = avg_regular // 100
        return {
            "type": "post_salary_spike",
            "title": "Post-Salary Spending Surge",
            "message": f"In the 3 days after salary hits, you spend an average of ₹{spike_rs:,} per transaction ({ratio}x your rest-of-month average of ₹{regular_rs:,}).",
            "severity": "medium",
            "evidence_ids": spike_txns[:10],
            "data": {
                "avg_spike_paise": avg_spike,
                "avg_regular_paise": avg_regular,
                "ratio": ratio,
            },
        }
    return None


def detect_month_end_squeeze(transactions: Iterable[Any]) -> dict[str, Any] | None:
    """Detect if spending drops drastically in the last 5 days of months."""
    end_spends: list[int] = []
    mid_spends: list[int] = []
    end_txns: list[str] = []

    for txn in transactions:
        amount = int(_get(txn, "amount_paise", 0))
        if amount >= 0 or bool(_get(txn, "is_recurring", False)) or bool(_get(txn, "is_self_transfer", False)):
            continue
        category = str(_get(txn, "category", ""))
        if category in {"Credit Card Payment", "Investment/SIP", "EMI/Loan"}:
            continue

        txn_date = _as_date(_get(txn, "date"))
        txn_id = str(_get(txn, "txn_id", ""))
        val = abs(amount)

        if txn_date.day >= 25:
            end_spends.append(val)
            if txn_id:
                end_txns.append(txn_id)
        else:
            mid_spends.append(val)

    if not end_spends or not mid_spends:
        return None

    avg_end = sum(end_spends) // len(end_spends)
    avg_mid = sum(mid_spends) // len(mid_spends)

    if avg_mid > 0 and avg_end < int(avg_mid * 0.6):
        drop_pct = round((1 - avg_end / avg_mid) * 100)
        end_rs = avg_end // 100
        mid_rs = avg_mid // 100
        return {
            "type": "month_end_squeeze",
            "title": "Month-End Cash Squeeze",
            "message": f"Spending drops by {drop_pct}% in the final 5 days of the month (₹{end_rs:,} vs ₹{mid_rs:,}), indicating cash-flow pressure before payday.",
            "severity": "high",
            "evidence_ids": end_txns[:10],
            "data": {
                "avg_end_paise": avg_end,
                "avg_mid_paise": avg_mid,
                "drop_percent": drop_pct,
            },
        }
    return None


def detect_duplicate_charges(transactions: Iterable[Any]) -> list[dict[str, Any]]:
    """Detect duplicate debit charges (same merchant, same amount, same date)."""
    groups: dict[tuple[date, int, str], list[str]] = defaultdict(list)

    for txn in transactions:
        amount = int(_get(txn, "amount_paise", 0))
        if amount >= 0:
            continue
        txn_date = _as_date(_get(txn, "date"))
        merchant = str(_get(txn, "merchant", "")).strip().upper()
        if not merchant or merchant == "UNKNOWN":
            continue
        txn_id = str(_get(txn, "txn_id", ""))
        groups[(txn_date, abs(amount), merchant)].append(txn_id)

    duplicates: list[dict[str, Any]] = []
    for (txn_date, amount_paise, merchant), txn_ids in groups.items():
        if len(txn_ids) >= 2:
            rs = amount_paise // 100
            duplicates.append({
                "type": "duplicate_charge",
                "title": "Potential Duplicate Charge",
                "message": f"Duplicate debit of ₹{rs:,} at {merchant} detected on {txn_date.strftime('%d %b %Y')}.",
                "severity": "high",
                "evidence_ids": txn_ids,
                "data": {
                    "merchant": merchant,
                    "amount_paise": amount_paise,
                    "date": txn_date.isoformat(),
                    "count": len(txn_ids),
                },
            })
    return duplicates


def detect_merchant_anomalies(transactions: Iterable[Any]) -> list[dict[str, Any]]:
    """Detect charges > 30% above the median for merchants with at least 3 transactions."""
    by_merchant: dict[str, list[tuple[date, int, str]]] = defaultdict(list)

    for txn in transactions:
        amount = int(_get(txn, "amount_paise", 0))
        if amount >= 0 or bool(_get(txn, "is_recurring", False)):
            continue
        merchant = str(_get(txn, "merchant", "")).strip().upper()
        if not merchant or merchant in {"UNKNOWN", "CASH WITHDRAWAL", "TRANSFERS"}:
            continue
        txn_date = _as_date(_get(txn, "date"))
        txn_id = str(_get(txn, "txn_id", ""))
        by_merchant[merchant].append((txn_date, abs(amount), txn_id))

    anomalies: list[dict[str, Any]] = []
    for merchant, rows in by_merchant.items():
        if len(rows) < 3:
            continue
        amounts = [r[1] for r in rows]
        med = int(median(amounts))
        if med < 10000:  # Skip trivial amounts < ₹100
            continue
        for txn_date, val, txn_id in rows:
            if val > int(med * 1.35):
                excess_pct = round(((val - med) / med) * 100)
                val_rs = val // 100
                med_rs = med // 100
                anomalies.append({
                    "type": "merchant_anomaly",
                    "title": "Unusual Merchant Charge",
                    "message": f"Charge of ₹{val_rs:,} at {merchant} on {txn_date.strftime('%d %b %Y')} is {excess_pct}% above your typical ₹{med_rs:,}.",
                    "severity": "medium",
                    "evidence_ids": [txn_id],
                    "data": {
                        "merchant": merchant,
                        "amount_paise": val,
                        "median_paise": med,
                        "date": txn_date.isoformat(),
                        "excess_percent": excess_pct,
                    },
                })
    return anomalies[:5]


def detect_subscription_price_hikes(recurring_items: Iterable[Any], transactions: Iterable[Any]) -> list[dict[str, Any]]:
    """Detect if a recurring charge increased in amount over time."""
    txns_by_id = {str(_get(t, "txn_id")): t for t in transactions}
    hikes: list[dict[str, Any]] = []

    for item in recurring_items:
        txn_ids = list(_get(item, "txn_ids", []))
        if len(txn_ids) < 3:
            continue
        matched_txns = [txns_by_id[tid] for tid in txn_ids if tid in txns_by_id]
        if len(matched_txns) < 3:
            continue

        sorted_txns = sorted(matched_txns, key=lambda t: _as_date(_get(t, "date")))
        earliest_amount = abs(int(_get(sorted_txns[0], "amount_paise", 0)))
        latest_amount = abs(int(_get(sorted_txns[-1], "amount_paise", 0)))

        if earliest_amount > 0 and latest_amount > int(earliest_amount * 1.08):
            merchant = str(_get(item, "merchant", "Subscription"))
            old_rs = earliest_amount // 100
            new_rs = latest_amount // 100
            hike_pct = round(((latest_amount - earliest_amount) / earliest_amount) * 100)
            hikes.append({
                "type": "subscription_price_hike",
                "title": "Subscription Price Increase",
                "message": f"{merchant} recurring bill increased by {hike_pct}% (from ₹{old_rs:,} to ₹{new_rs:,}).",
                "severity": "medium",
                "evidence_ids": [str(_get(sorted_txns[0], "txn_id")), str(_get(sorted_txns[-1], "txn_id"))],
                "data": {
                    "merchant": merchant,
                    "old_paise": earliest_amount,
                    "new_paise": latest_amount,
                    "hike_percent": hike_pct,
                },
            })
    return hikes


def detect_overlapping_subscriptions(recurring_items: Iterable[Any]) -> list[dict[str, Any]]:
    """Detect overlapping services in the same category (e.g. multiple streaming video / audio)."""
    streaming_video_keywords = {"NETFLIX", "PRIME", "HOTSTAR", "DISNEY", "SONYLIV", "ZEE5", "JIOCINEMA", "APPLE TV"}
    music_keywords = {"SPOTIFY", "APPLE MUSIC", "YOUTUBE MUSIC", "GAANA", "WYNK"}
    gym_keywords = {"CULT", "FITNESS", "GYM", "GOLD"}

    found_video: list[tuple[str, str, int]] = []
    found_music: list[tuple[str, str, int]] = []
    found_gym: list[tuple[str, str, int]] = []

    for item in recurring_items:
        merchant = str(_get(item, "merchant", "")).upper()
        item_id = str(_get(item, "id", ""))
        amount = abs(int(_get(item, "amount_paise", 0)))

        for kw in streaming_video_keywords:
            if kw in merchant:
                found_video.append((merchant, item_id, amount))
                break
        for kw in music_keywords:
            if kw in merchant:
                found_music.append((merchant, item_id, amount))
                break
        for kw in gym_keywords:
            if kw in merchant:
                found_gym.append((merchant, item_id, amount))
                break

    overlaps: list[dict[str, Any]] = []

    def check_overlap(category_name: str, items: list[tuple[str, str, int]]):
        if len(items) >= 2:
            merchants = [i[0] for i in items]
            total_monthly_paise = sum(i[2] for i in items)
            total_rs = total_monthly_paise // 100
            evidence = [i[1] for i in items]
            overlaps.append({
                "type": "overlapping_subscription",
                "title": f"Multiple {category_name} Subscriptions",
                "message": f"You are currently paying for {len(items)} {category_name.lower()} services ({', '.join(merchants)}), costing ₹{total_rs:,}/month total.",
                "severity": "low",
                "evidence_ids": evidence,
                "data": {
                    "category": category_name,
                    "merchants": merchants,
                    "total_monthly_paise": total_monthly_paise,
                },
            })

    check_overlap("Video Streaming", found_video)
    check_overlap("Music Streaming", found_music)
    check_overlap("Fitness & Gym", found_gym)

    return overlaps


def generate_insights(
    transactions: Iterable[Any],
    recurring_items: Iterable[Any] = (),
    income: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Run all behavioural and anomaly detectors and return combined insights."""
    insights: list[dict[str, Any]] = []

    # 1. Duplicate charges
    duplicates = detect_duplicate_charges(transactions)
    insights.extend(duplicates)

    # 2. Subscription price hikes
    hikes = detect_subscription_price_hikes(recurring_items, transactions)
    insights.extend(hikes)

    # 3. Overlapping subscriptions
    overlaps = detect_overlapping_subscriptions(recurring_items)
    insights.extend(overlaps)

    # 4. Weekend vs weekday spend
    weekend = analyze_weekday_vs_weekend(transactions)
    if weekend:
        insights.append(weekend)

    # 5. Post-salary spike
    post_salary = detect_post_salary_spike(transactions, income)
    if post_salary:
        insights.append(post_salary)

    # 6. Month-end squeeze
    squeeze = detect_month_end_squeeze(transactions)
    if squeeze:
        insights.append(squeeze)

    # 7. Merchant anomalies
    anomalies = detect_merchant_anomalies(transactions)
    insights.extend(anomalies)

    return insights

