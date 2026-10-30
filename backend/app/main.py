import csv
from datetime import date
from io import BytesIO
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import create_tables, get_db
from .config import settings
from .ingestion.cleaning import clean_transactions
from .ingestion.parser import parse_file
from .models import Account, Card, Loan, RecurringItem, Transaction, User
from .schemas import HealthResponse, ProcessResponse, RecurringItemRead, UserRead
from .categorise.cascade import categorise
from .categorise.rules import UNCATEGORISED
from .recurring import detect_income, detect_recurring
from .metrics import compute_health_score

app = FastAPI(title="ArthaPilot")
create_tables()
MAX_UPLOAD_BYTES = settings.upload_max_size_mb * 1024 * 1024
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)))


@app.post("/upload")
async def upload_statement(
    file: UploadFile = File(...), db: Session = Depends(get_db)
) -> dict[str, int | str | dict[str, list[str]]]:
    filename = file.filename or ""
    suffix = Path(filename).suffix.lower()
    if suffix not in {".csv", ".xlsx", ".pdf"}:
        raise HTTPException(status_code=415, detail="Only CSV, XLSX, and PDF uploads are supported")
    try:
        payload = await file.read(MAX_UPLOAD_BYTES + 1)
        if len(payload) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"Upload exceeds the {settings.upload_max_size_mb} MB size limit",
            )
        rows = parse_file(BytesIO(payload), filename)
        if not rows:
            raise ValueError("Upload contains no transaction rows")
        columns = {str(column).strip().lower() for column in rows[0]}
        date_columns = {"date", "transaction date", "txn_date"}
        amount_columns = {
            "amount",
            "amount_paise",
            "value",
            "transaction amount",
            "debit",
            "withdrawal",
            "debit amount",
            "credit",
            "deposit",
            "credit amount",
        }
        missing = []
        if not columns.intersection(date_columns):
            missing.append("date")
        if not columns.intersection(amount_columns):
            missing.append("amount or debit/credit")
        if missing:
            return {
                "status": "column_mapping_required",
                "mapping": {
                    "required": missing,
                    "detected": sorted(columns),
                },
            }
        user_id = f"upload-{Path(filename).stem}"
        user = db.get(User, user_id)
        if user is None:
            user = User(id=user_id, name=user_id, source="real")
            db.add(user)
        transactions = clean_transactions(rows, user_id=user_id, source="real")
        account_ids = {transaction["account_id"] for transaction in transactions}
        for account_id in account_ids:
            if db.get(Account, account_id) is None:
                db.add(
                    Account(
                        id=account_id,
                        user_id=user_id,
                        type="savings",
                        institution="Uploaded statement",
                    )
                )
        for transaction in transactions:
            if db.get(Transaction, transaction["txn_id"]) is None:
                db.add(Transaction(**transaction))
        db.commit()
        return {"user_id": user_id, "transactions_loaded": len(transactions)}
    except HTTPException:
        db.rollback()
        raise
    except (ValueError, KeyError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/users/{user_id}/load-persona")
def load_persona(user_id: str, db: Session = Depends(get_db)) -> dict[str, int | str]:
    persona_file = (
        Path(__file__).parents[2]
        / "data"
        / "synthetic"
        / user_id
        / "transactions.csv"
    )
    if not persona_file.exists():
        raise HTTPException(status_code=404, detail="Persona not found")
    persona_dir = persona_file.parent

    with persona_file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    user = db.get(User, user_id) or User(id=user_id, name=user_id.title(), source="synthetic")
    db.add(user)
    transactions = clean_transactions(rows, user_id=user_id, source="synthetic")
    account_id = f"{user_id}-primary"
    accounts_file = persona_dir / "accounts.csv"
    if accounts_file.exists():
        with accounts_file.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                account = db.get(Account, row["id"])
                if account is None:
                    db.add(
                        Account(
                            id=row["id"],
                            user_id=user_id,
                            type=row["type"],
                            institution=row["institution"],
                            balance_paise=int(row["balance_paise"]),
                            credit_limit_paise=(
                                int(row["credit_limit_paise"])
                                if row.get("credit_limit_paise")
                                else None
                            ),
                        )
                    )
                if row["type"] in {"savings", "current"}:
                    account_id = row["id"]
    elif db.get(Account, account_id) is None:
        db.add(Account(id=account_id, user_id=user_id, type="savings", institution="Synthetic bank"))
    for model, filename in ((Loan, "loans.csv"), (Card, "cards.csv")):
        sidecar = persona_dir / filename
        if sidecar.exists():
            with sidecar.open(encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    if db.get(model, row["id"]) is None:
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
                        db.add(model(**values))
    for transaction in transactions:
        transaction["account_id"] = account_id
    for transaction in transactions:
        if db.get(Transaction, transaction["txn_id"]) is None:
            db.add(Transaction(**transaction))
    db.commit()
    return {"user_id": user_id, "transactions_loaded": len(transactions)}


@app.post("/users/{user_id}/process", response_model=ProcessResponse)
def process_user(user_id: str, db: Session = Depends(get_db)) -> ProcessResponse:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user_id)))
    if not transactions:
        raise HTTPException(status_code=422, detail="User has no transactions")
    model_path = Path(__file__).with_name("categorise") / "categoriser.joblib"
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
    return ProcessResponse(
        user_id=user_id,
        transaction_count=len(transactions),
        category_breakdown=dict(breakdown),
        confidence_summary={
            "mean": round(sum(confidences) / len(confidences), 6),
            "uncategorised_rate": round(breakdown.get(UNCATEGORISED, 0) / len(transactions), 6),
        },
        recurring_count=len(recurring),
        income=income,
    )


@app.get("/users/{user_id}/recurring", response_model=list[RecurringItemRead])
def recurring_for_user(user_id: str, db: Session = Depends(get_db)) -> list[RecurringItem]:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return list(
        db.scalars(
            select(RecurringItem)
            .where(RecurringItem.user_id == user_id)
            .order_by(RecurringItem.next_due_date)
        )
    )


@app.get("/users/{user_id}/health", response_model=HealthResponse)
def health_for_user(
    user_id: str,
    months: int = Query(6, ge=3, le=12),
    db: Session = Depends(get_db),
) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = list(
        db.scalars(select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date))
    )
    loans = list(db.scalars(select(Loan).where(Loan.user_id == user_id)))
    cards = list(db.scalars(select(Card).where(Card.user_id == user_id)))
    accounts = list(db.scalars(select(Account).where(Account.user_id == user_id)))
    report = compute_health_score(transactions, loans, cards, accounts, requested_months=months)
    uncategorised = sum(
        1 for transaction in transactions if not transaction.category or transaction.category == UNCATEGORISED
    )
    report["uncategorised_share"] = uncategorised / len(transactions) if transactions else 0.0
    return report
