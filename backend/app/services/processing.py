"""ArthaPilot Processing & Demo Seeding Service (DEC-05, F2, F3).

Idempotent loading, processing, resetting, and management of demo personas and users.
"""

import csv
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.categorise.cascade import categorise
from app.categorise.rules import UNCATEGORISED
from app.config import settings
from app.ingestion.cleaning import clean_transactions
from app.models import (
    Account,
    Card,
    ChatMessage,
    Goal,
    Investment,
    Loan,
    RecurringItem,
    Snapshot,
    Transaction,
    User,
)
from app.recurring import detect_income, detect_recurring

PERSONA_METADATA: List[Dict[str, Any]] = [
    {
        "id": "rahul",
        "name": "Rahul Sharma",
        "role": "Young Professional (Salaried)",
        "income": "₹65,000/mo",
        "focus": "Food Delivery, High-APR Card, Month-end low balance",
        "scenario": "Month-end cash gap before salary on the 27th; high credit card APR",
    },
    {
        "id": "priya",
        "name": "Priya Nair",
        "role": "Senior Consultant (Salaried + Home Loan)",
        "income": "₹1,20,000/mo",
        "focus": "₹38,000 Home Loan EMI + Solid Savings Rate",
        "scenario": "Healthy Strong financial baseline with high emergency runway",
    },
    {
        "id": "arjun",
        "name": "Arjun Mehta",
        "role": "Freelance Designer (Variable Income)",
        "income": "Variable (₹40,000 - ₹95,000/mo)",
        "focus": "Irregular cash flow, invoice delays, variable runway",
        "scenario": "Medium confidence due to income instability; irregular cash gaps",
    },
    {
        "id": "meera",
        "name": "Meera Patel",
        "role": "Retail Business Owner (High Debt)",
        "income": "₹85,000/mo",
        "focus": "Multiple high-interest personal loans & 70%+ card utilisation",
        "scenario": "Debt stress test with Avalanche vs Snowball payoff payoff",
    },
    {
        "id": "sam",
        "name": "Samarth Kulkarni",
        "role": "Entry-level Associate (Zero Buffer)",
        "income": "₹35,000/mo",
        "focus": "Zero emergency savings, paycheck-to-paycheck living",
        "scenario": "Immediate buffer building required before any investments",
    },
]


def list_demo_personas() -> List[Dict[str, Any]]:
    """Return available synthetic persona profiles."""
    return PERSONA_METADATA


def load_persona_core(user_id: str, db: Session) -> int:
    """Load transactions, accounts, loans, cards, and investments for a persona."""
    data_dir = settings.resolved_data_dir
    persona_dir = data_dir / "synthetic" / user_id
    txn_file = persona_dir / "transactions.csv"

    if not txn_file.exists():
        # Fallback to single csv file if folder structure is flat
        txn_file = data_dir / "synthetic" / f"{user_id}.csv"
        if not txn_file.exists():
            raise FileNotFoundError(f"Persona '{user_id}' transactions not found at {txn_file}")
        persona_dir = data_dir / "synthetic"

    with txn_file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    user = db.get(User, user_id)
    if user is None:
        user_name = next((p["name"] for p in PERSONA_METADATA if p["id"] == user_id), user_id.title())
        user = User(id=user_id, name=user_name, source="synthetic")
        db.add(user)

    # Clean existing persona data before reloading
    db.query(Snapshot).filter(Snapshot.user_id == user_id).delete()
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(RecurringItem).filter(RecurringItem.user_id == user_id).delete()
    db.query(Loan).filter(Loan.user_id == user_id).delete()
    db.query(Card).filter(Card.user_id == user_id).delete()
    db.query(Investment).filter(Investment.user_id == user_id).delete()

    transactions = clean_transactions(rows, user_id=user_id, source="synthetic")

    account_id = f"{user_id}-primary"
    accounts_file = persona_dir / "accounts.csv"
    if accounts_file.exists():
        with accounts_file.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                acc = db.get(Account, row["id"])
                if acc is None:
                    db.add(
                        Account(
                            id=row["id"],
                            user_id=user_id,
                            type=row.get("type", "savings"),
                            institution=row.get("institution", "Synthetic Bank"),
                            balance_paise=int(row.get("balance_paise", 0)),
                            credit_limit_paise=(
                                int(row["credit_limit_paise"])
                                if row.get("credit_limit_paise")
                                else None
                            ),
                        )
                    )
                if row.get("type") in {"savings", "current"}:
                    account_id = row["id"]
    elif db.get(Account, account_id) is None:
        db.add(Account(id=account_id, user_id=user_id, type="savings", institution="Synthetic Bank"))

    # Load loans and cards
    for model, filename in ((Loan, "loans.csv"), (Card, "cards.csv")):
        sidecar = persona_dir / filename
        if not sidecar.exists():
            sidecar = data_dir / "synthetic" / filename
        if sidecar.exists():
            with sidecar.open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    row_user = row.get("user_id", user_id)
                    if row_user == user_id:
                        values = dict(row)
                        for field in ("principal_paise", "outstanding_paise", "emi_paise", "limit_paise", "balance_paise", "min_due_paise"):
                            if field in values and values[field] != "":
                                values[field] = int(values[field])
                        for field in ("rate_apr", "apr"):
                            if field in values and values[field] != "":
                                values[field] = float(values[field])
                        for field in ("next_due_date", "due_date"):
                            if field in values and values[field]:
                                values[field] = date.fromisoformat(values[field])
                        values["user_id"] = user_id
                        if db.get(model, values["id"]) is None:
                            db.add(model(**values))

    # Load investments
    inv_file = persona_dir / "investments.csv"
    if not inv_file.exists():
        inv_file = data_dir / "synthetic" / "investments.csv"
    if inv_file.exists():
        with inv_file.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("user_id") == user_id:
                    inv_id = f"inv-{user_id}-{row.get('name', 'SIP')}"
                    if db.get(Investment, inv_id) is None:
                        val = int(row.get("value_paise", 0)) if row.get("value_paise") else 0
                        db.add(Investment(
                            id=inv_id,
                            user_id=user_id,
                            type=row.get("name", "SIP"),
                            value_paise=val,
                            monthly_sip_paise=max(100000, val // 10)
                        ))

    for transaction in transactions:
        transaction["account_id"] = account_id
        if db.get(Transaction, transaction["txn_id"]) is None:
            db.add(Transaction(**transaction))

    db.commit()
    return len(transactions)


def process_user_core(user_id: str, db: Session) -> Dict[str, Any]:
    """Execute rule cascade, ML categorisation, and recurring/income detection."""
    user = db.get(User, user_id)
    if user is None:
        raise ValueError("User not found")

    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user_id)))
    if not transactions:
        raise ValueError("User has no transactions")

    model_path = Path(__file__).resolve().parents[1] / "categorise" / "categoriser.joblib"
    llm_client = None

    for transaction in transactions:
        raw_upper = transaction.raw_description.upper()
        received_person = raw_upper.startswith("RECEIVED FROM")
        income_hint = any(token in raw_upper for token in ("SALARY", "PAYROLL", "INCOME", "CLIENT PAYMENT"))
        if transaction.is_self_transfer or (received_person and not income_hint):
            result = ("Transfers", 1.0, transaction.merchant)
        else:
            classified = categorise(transaction.raw_description, model_path, llm_client)
            result = (classified.category, classified.confidence, classified.merchant)
        transaction.category, transaction.category_confidence, transaction.merchant = result

    recurring = detect_recurring(transactions)
    db.query(RecurringItem).filter(RecurringItem.user_id == user_id).delete()
    for item in recurring:
        db.add(
            RecurringItem(
                id=f"{user_id}-{item['merchant']}".lower().replace(" ", "-"),
                user_id=user_id,
                merchant=item["merchant"],
                amount_paise=item["amount_paise"],
                interval_days=item["interval_days"],
                next_due_date=item["next_due_date"],
                confidence=item["confidence"],
                txn_ids=item["txn_ids"],
            )
        )
        for transaction in transactions:
            if transaction.txn_id in item["txn_ids"]:
                transaction.is_recurring = True

    db.commit()

    breakdown = Counter(transaction.category or UNCATEGORISED for transaction in transactions)
    confidences = [transaction.category_confidence for transaction in transactions]
    income = detect_income(transactions)

    return {
        "user_id": user_id,
        "transaction_count": len(transactions),
        "category_breakdown": dict(breakdown),
        "confidence_summary": {
            "mean": round(sum(confidences) / len(confidences), 6),
            "uncategorised_rate": round(breakdown.get(UNCATEGORISED, 0) / len(transactions), 6),
        },
        "recurring_count": len(recurring),
        "income": income,
    }


def seed_demo(db: Session) -> Dict[str, int]:
    """F2: Idempotently seed and process the 5 synthetic demo personas."""
    results: Dict[str, int] = {}
    data_dir = settings.resolved_data_dir / "synthetic"

    for persona in PERSONA_METADATA:
        pid = persona["id"]
        persona_folder = data_dir / pid
        persona_csv = data_dir / f"{pid}.csv"
        if not persona_folder.exists() and not persona_csv.exists():
            continue

        existing_user = db.get(User, pid)
        existing_txns = db.query(Transaction).filter(Transaction.user_id == pid).count()

        if existing_user is None or existing_txns == 0:
            count = load_persona_core(pid, db)
            process_user_core(pid, db)
            results[pid] = count
        else:
            results[pid] = existing_txns

    return results


def reset_user(user_id: str, db: Session) -> Dict[str, Any]:
    """F2: Restore a user's data back to their original clean persona state."""
    count = load_persona_core(user_id, db)
    process_result = process_user_core(user_id, db)
    return {
        "user_id": user_id,
        "status": "reset_successful",
        "transactions_restored": count,
        "process_summary": process_result,
    }


def delete_user_data(user_id: str, db: Session) -> bool:
    """DEC-12, 5.2: Delete a user and all their associated local data."""
    user = db.get(User, user_id)
    if not user:
        return False
    db.query(Snapshot).filter(Snapshot.user_id == user_id).delete()
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(RecurringItem).filter(RecurringItem.user_id == user_id).delete()
    db.query(Loan).filter(Loan.user_id == user_id).delete()
    db.query(Card).filter(Card.user_id == user_id).delete()
    db.query(Investment).filter(Investment.user_id == user_id).delete()
    db.query(Account).filter(Account.user_id == user_id).delete()
    db.query(Goal).filter(Goal.user_id == user_id).delete()
    db.query(ChatMessage).filter(ChatMessage.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return True
