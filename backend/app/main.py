import csv
from uuid import uuid4
from datetime import date, timedelta
from io import BytesIO
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from collections import Counter
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import create_tables, get_db
from .config import settings
from .auth import create_session, get_current_user, get_user_by_token, hash_password, verify_password
from .ingestion.cleaning import clean_transactions
from .ingestion.parser import parse_file
from .models import Account, Card, ChatMessage, Investment, Loan, RecurringItem, SessionToken, Snapshot, Transaction, User
from .schemas import (
    AffordabilityRequest,
    AuthResponse,
    AuthUserResponse,
    CardCreate,
    CardRead,
    ChatRequest,
    ConfidenceResponse,
    DebtPayoffRequest,
    DebtPayoffResponse,
    GoalRequest,
    HealthResponse,
    InsightResponse,
    InvestmentCreate,
    InvestmentRead,
    ProcessResponse,
    RecurringItemRead,
    SimulationRequest,
    TransactionRead,
    IncomeChange,
    LoanCreate,
    TransactionCreate,
    UserLoginRequest,
    UserRegisterRequest,
    WhatChangedResponse,
    UserRead,
)
from .categorise.cascade import categorise
from .categorise.rules import UNCATEGORISED
from .recurring import detect_income, detect_recurring
from .metrics import compute_health_score
from .metrics.confidence import compute_confidence
from .copilot import Answer, answer_question
from .simulate import affordability, debt_payoff_plan, goal_plan, rank_actions, simulate
from .insights import generate_insights
from .forecast import build_schedule, detect_gaps, monte_carlo_forecast, stress_test, variable_spend_model
from .forecast.schemas import ForecastRead, GapRead, StressRead, StressRequest

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


@app.post("/auth/register", response_model=AuthResponse)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email_clean = request.email.strip().lower()
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="A valid email address is required")
    if len(request.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    existing = db.scalar(select(User).where(User.email == email_clean))
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    user_id = f"user-{uuid4().hex[:10]}"
    user = User(
        id=user_id,
        name=request.name.strip(),
        email=email_clean,
        hashed_password=hash_password(request.password),
        persona_type=request.persona_type or "custom",
        source="user",
    )
    db.add(user)
    # Default primary account
    account_id = f"acc-{uuid4().hex[:8]}"
    db.add(
        Account(
            id=account_id,
            user_id=user_id,
            type="savings",
            institution="Primary Bank Account",
            balance_paise=5000000,
        )
    )
    db.commit()
    db.refresh(user)

    token = create_session(db, user_id=user.id)
    return AuthResponse(token=token, user=user)


@app.post("/auth/login", response_model=AuthResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    email_clean = request.email.strip().lower()
    user = db.scalar(select(User).where(User.email == email_clean))
    if not user or not user.hashed_password or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_session(db, user_id=user.id)
    return AuthResponse(token=token, user=user)


@app.post("/auth/demo-login/{persona_id}", response_model=AuthResponse)
def demo_login(persona_id: str, db: Session = Depends(get_db)) -> AuthResponse:
    user = db.get(User, persona_id)
    if not user:
        persona_path = Path("data/synthetic") / persona_id
        if not persona_path.exists():
            raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
        load_persona(persona_id, db=db)
        user = db.get(User, persona_id)
        if not user:
            raise HTTPException(status_code=404, detail="Could not load persona")

    token = create_session(db, user_id=user.id)
    return AuthResponse(token=token, user=user)


@app.get("/auth/me", response_model=AuthUserResponse)
def get_me(user: User = Depends(get_current_user)) -> User:
    return user


@app.post("/auth/logout")
def logout(
    authorization: str | None = Header(None),
    token: str | None = Query(None),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    raw_token = None
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split("Bearer ", 1)[1].strip()
    elif token:
        raw_token = token
    if raw_token:
        session = db.get(SessionToken, raw_token)
        if session:
            db.delete(session)
            db.commit()
    return {"status": "logged_out"}



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
    db.query(Snapshot).filter(Snapshot.user_id == user_id).delete()
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
    # Load investments for persona if present
    inv_file = persona_dir / "investments.csv"
    if not inv_file.exists():
        inv_file = Path(__file__).parents[2] / "data" / "synthetic" / "investments.csv"
    if inv_file.exists():
        with inv_file.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("user_id") == user_id:
                    inv_id = f"inv-{user_id}-{row.get('name', 'SIP')}"
                    if db.get(Investment, inv_id) is None:
                        val = int(row.get("value_paise", 0)) if row.get("value_paise") else 0
                        db.add(Investment(id=inv_id, user_id=user_id, type=row.get("name", "SIP"), value_paise=val, monthly_sip_paise=max(100000, val // 10)))
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


@app.get("/users/{user_id}/transactions", response_model=list[TransactionRead])
def transactions_for_user(
    user_id: str,
    category: str | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Transaction]:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    query = select(Transaction).where(Transaction.user_id == user_id)
    if category:
        query = query.where(Transaction.category == category)
    return list(
        db.scalars(query.order_by(Transaction.date.desc(), Transaction.txn_id).limit(limit))
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


def _forecast_state(user_id: str, db: Session, days: int = 90) -> dict:
    if db.get(User, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user_id)))
    if not transactions:
        raise HTTPException(status_code=422, detail="User has no transactions")
    income = detect_income(transactions)
    if income.get("salary"):
        salary_rows = [t for t in transactions if t.txn_id in income["salary"]["txn_ids"]]
        income["salary"]["day_of_month"] = min((t.date.day for t in salary_rows), default=1)
    start = max(t.date for t in transactions) + timedelta(days=1)
    accounts = list(db.scalars(select(Account).where(Account.user_id == user_id)))
    schedule = build_schedule(
        list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user_id))),
        income, list(db.scalars(select(Loan).where(Loan.user_id == user_id))),
        list(db.scalars(select(Card).where(Card.user_id == user_id))), start, days,
    )
    return {
        "balance_paise": sum(int(a.balance_paise or 0) for a in accounts),
        "schedule": schedule,
        "variable_model": variable_spend_model(transactions),
        "start_date": start,
    }


@app.get("/users/{user_id}/forecast", response_model=ForecastRead)
def forecast_for_user(user_id: str, days: int = Query(90, ge=1, le=365),
                      runs: int = Query(1000, ge=100, le=10000),
                      seed: int = Query(42), db: Session = Depends(get_db)) -> dict:
    state = _forecast_state(user_id, db, days)
    return monte_carlo_forecast(**state, days=days, runs=runs, seed=seed)


@app.get("/users/{user_id}/gaps", response_model=list[GapRead])
def gaps_for_user(user_id: str, safe_threshold_paise: int = Query(0, ge=0),
                  db: Session = Depends(get_db)) -> list[dict]:
    state = _forecast_state(user_id, db)
    return detect_gaps(monte_carlo_forecast(**state), safe_threshold_paise)


@app.post("/users/{user_id}/stress-test", response_model=StressRead)
def stress_test_for_user(user_id: str, request: StressRequest,
                         db: Session = Depends(get_db)) -> dict:
    state = _forecast_state(user_id, db)
    state["new_emi_paise"] = request.new_emi_paise
    return stress_test(state, request.scenario)


@app.get("/users/{user_id}/confidence", response_model=ConfidenceResponse)
def confidence_for_user(user_id: str, db: Session = Depends(get_db)) -> dict:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = list(
        db.scalars(select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date))
    )
    loans = list(db.scalars(select(Loan).where(Loan.user_id == user_id)))
    cards = list(db.scalars(select(Card).where(Card.user_id == user_id)))
    recurring_items = list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user_id)))
    return compute_confidence(transactions, loans, cards, recurring_items)


def _simulation_state(user: User) -> dict:
    return {
        "months": max(1, len({(item.date.year, item.date.month) for item in user.transactions})),
        "transactions": [
            {"txn_id": item.txn_id, "amount_paise": item.amount_paise, "category": item.category}
            for item in user.transactions
        ],
        "accounts": [{"type": item.type, "balance_paise": item.balance_paise} for item in user.accounts],
        "loans": [{"outstanding_paise": item.outstanding_paise, "rate_apr": item.rate_apr, "id": item.id, "emi_paise": item.emi_paise, "type": item.type} for item in user.loans],
        "cards": [{"outstanding_paise": item.balance_paise, "rate_apr": item.apr, "id": item.id, "min_due_paise": item.min_due_paise, "type": "Credit Card"} for item in user.cards],
        "recurring_items": [{"merchant": item.merchant, "txn_ids": item.txn_ids, "amount_paise": item.amount_paise} for item in user.recurring_items],
    }


def _require_user(user_id: str, db: Session) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/users/{user_id}/chat", response_model=Answer)
def chat_for_user(user_id: str, request: ChatRequest, db: Session = Depends(get_db)) -> Answer:
    if not request.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date)))
    loans = list(db.scalars(select(Loan).where(Loan.user_id == user_id)))
    cards = list(db.scalars(select(Card).where(Card.user_id == user_id)))
    accounts = list(db.scalars(select(Account).where(Account.user_id == user_id)))
    recurring_items = list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user_id)))
    health = compute_health_score(transactions, loans, cards, accounts)
    confidence = compute_confidence(transactions, loans, cards, recurring_items)
    
    gaps_list = []
    try:
        fstate = _forecast_state(user_id, db, days=90)
        fforecast = monte_carlo_forecast(**fstate, days=90, runs=200, seed=42)
        gaps_list = detect_gaps(fforecast)
    except Exception:
        pass

    sim_state = _simulation_state(user)

    answer = answer_question(
        request.question,
        health=health,
        confidence=confidence,
        recurring=[{
            "id": item.id,
            "merchant": item.merchant,
            "amount_paise": item.amount_paise,
            "txn_ids": item.txn_ids,
            "next_due_date": item.next_due_date.isoformat(),
        } for item in recurring_items],
        simulation_state=sim_state,
        gaps=gaps_list,
        language=request.language or "en",
    )
    db.add(ChatMessage(
        id=f"{user_id}-{len(user.chat_messages) + 1}",
        user_id=user_id,
        role="assistant",
        content=answer.summary,
        answer_json=answer.model_dump(mode="json"),
    ))
    db.commit()
    return answer


@app.get("/users/{user_id}/insights", response_model=list[InsightResponse])
def insights_for_user(user_id: str, db: Session = Depends(get_db)) -> list[dict]:
    user = _require_user(user_id, db)
    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user_id).order_by(Transaction.date)))
    recurring_items = list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user_id)))
    income = detect_income(transactions) if transactions else None
    return generate_insights(transactions, recurring_items, income)


@app.post("/users/{user_id}/debt-payoff", response_model=DebtPayoffResponse)
def debt_payoff_for_user(user_id: str, request: DebtPayoffRequest, db: Session = Depends(get_db)) -> dict:
    user = _require_user(user_id, db)
    loans = [
        {"id": item.id, "type": item.type, "outstanding_paise": item.outstanding_paise,
         "rate_apr": item.rate_apr, "emi_paise": item.emi_paise}
        for item in user.loans
    ]
    cards = [
        {"id": item.id, "type": "Credit Card", "outstanding_paise": item.balance_paise,
         "apr": item.apr, "min_due_paise": item.min_due_paise}
        for item in user.cards
    ]
    return debt_payoff_plan(loans, cards, extra_monthly_paise=request.extra_monthly_paise, strategy=request.strategy)



@app.post("/users/{user_id}/simulate")
def simulate_for_user(user_id: str, request: SimulationRequest, db: Session = Depends(get_db)) -> dict:
    user = _require_user(user_id, db)
    action = request.model_dump(exclude_none=True)
    return simulate(_simulation_state(user), action)


@app.get("/users/{user_id}/best-moves")
def best_moves_for_user(user_id: str, db: Session = Depends(get_db)) -> dict:
    return rank_actions(_simulation_state(_require_user(user_id, db)))


@app.post("/users/{user_id}/affordability")
def affordability_for_user(user_id: str, request: AffordabilityRequest, db: Session = Depends(get_db)) -> dict:
    return affordability(_simulation_state(_require_user(user_id, db)), request.amount_paise)


@app.post("/users/{user_id}/goal")
def goal_for_user(user_id: str, request: GoalRequest, db: Session = Depends(get_db)) -> dict:
    return goal_plan(_simulation_state(_require_user(user_id, db)), request.target_paise, request.deadline)


def _snapshot_payload(user: User, db: Session) -> dict:
    transactions = list(db.scalars(select(Transaction).where(Transaction.user_id == user.id).order_by(Transaction.date)))
    loans = list(db.scalars(select(Loan).where(Loan.user_id == user.id)))
    cards = list(db.scalars(select(Card).where(Card.user_id == user.id)))
    accounts = list(db.scalars(select(Account).where(Account.user_id == user.id)))
    health = compute_health_score(transactions, loans, cards, accounts)
    confidence = compute_confidence(
        transactions, loans, cards,
        list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user.id))),
    )
    try:
        forecast = monte_carlo_forecast(**_forecast_state(user.id, db, 30), days=30, runs=250, seed=42)
        forecast = {key: ([value.isoformat() for value in value_list] if key == "dates" else value_list) for key, value_list in forecast.items()}
        gaps = [item["date"].isoformat() for item in detect_gaps(forecast)]
    except HTTPException:
        forecast = {}
        gaps = []
    moves = rank_actions(_simulation_state(user))
    return {
        "health": {"total_score": health.get("total_score"), "band": health.get("band")},
        "confidence": {"score": confidence.get("score")},
        "forecast": forecast,
        "gaps": gaps,
        "recommendation": moves.get("best_move", {}).get("reason") if moves.get("best_move") else None,
    }


def _save_snapshot(user: User, db: Session) -> Snapshot:
    snapshot = Snapshot(
        id=str(uuid4()),
        user_id=user.id,
        metrics_json=_snapshot_payload(user, db),
        forecast_json={},
        recommendations_json={},
    )
    db.add(snapshot)
    db.flush()
    return snapshot


@app.post("/users/{user_id}/transactions", response_model=TransactionRead)
def add_transaction(user_id: str, request: TransactionCreate, db: Session = Depends(get_db)) -> Transaction:
    user = _require_user(user_id, db)
    account = user.accounts[0] if user.accounts else None
    if account is None:
        raise HTTPException(status_code=422, detail="User has no account for this transaction")
    _save_snapshot(user, db)
    transaction = Transaction(
        txn_id=str(uuid4()),
        user_id=user.id,
        account_id=account.id,
        date=request.date,
        amount_paise=request.amount_paise,
        raw_description=request.description,
        merchant=request.merchant,
        category=request.category,
        category_confidence=1.0,
        source="manual",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/users/{user_id}/loans")
def list_loans(user_id: str, db: Session = Depends(get_db)) -> list[dict]:
    user = _require_user(user_id, db)
    return [
        {
            "id": loan.id,
            "type": loan.type,
            "principal_paise": loan.principal_paise,
            "outstanding_paise": loan.outstanding_paise,
            "emi_paise": loan.emi_paise,
            "rate_apr": loan.rate_apr,
            "tenure_left_months": loan.tenure_left_months,
            "next_due_date": loan.next_due_date.isoformat() if loan.next_due_date else None,
        }
        for loan in user.loans
    ]


@app.post("/users/{user_id}/loans")
def add_loan(user_id: str, request: LoanCreate, db: Session = Depends(get_db)) -> dict:
    user = _require_user(user_id, db)
    if request.outstanding_paise < 0 or request.emi_paise < 0:
        raise HTTPException(status_code=422, detail="Loan amounts must not be negative")
    _save_snapshot(user, db)
    loan = Loan(
        id=str(uuid4()), user_id=user.id, type=request.type,
        principal_paise=request.outstanding_paise, outstanding_paise=request.outstanding_paise,
        emi_paise=request.emi_paise, rate_apr=request.rate_apr, next_due_date=request.next_due_date,
    )
    db.add(loan)
    db.commit()
    return {"id": loan.id, "status": "created"}


@app.get("/users/{user_id}/cards", response_model=list[CardRead])
def list_cards(user_id: str, db: Session = Depends(get_db)) -> list[Card]:
    user = _require_user(user_id, db)
    return list(db.scalars(select(Card).where(Card.user_id == user.id)))


@app.post("/users/{user_id}/cards", response_model=CardRead)
def add_card(user_id: str, request: CardCreate, db: Session = Depends(get_db)) -> Card:
    user = _require_user(user_id, db)
    _save_snapshot(user, db)
    card = Card(
        id=str(uuid4()),
        user_id=user.id,
        limit_paise=request.limit_paise,
        balance_paise=request.balance_paise,
        apr=request.apr,
        min_due_paise=request.min_due_paise,
        due_date=request.due_date,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@app.get("/users/{user_id}/investments", response_model=list[InvestmentRead])
def list_investments(user_id: str, db: Session = Depends(get_db)) -> list[Investment]:
    user = _require_user(user_id, db)
    return list(db.scalars(select(Investment).where(Investment.user_id == user.id)))


@app.post("/users/{user_id}/investments", response_model=InvestmentRead)
def add_investment(user_id: str, request: InvestmentCreate, db: Session = Depends(get_db)) -> Investment:
    user = _require_user(user_id, db)
    _save_snapshot(user, db)
    inv = Investment(
        id=str(uuid4()),
        user_id=user.id,
        type=request.type,
        value_paise=request.value_paise,
        monthly_sip_paise=request.monthly_sip_paise,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


@app.post("/users/{user_id}/income-change", response_model=TransactionRead)
def add_income_change(user_id: str, request: IncomeChange, db: Session = Depends(get_db)) -> Transaction:
    user = _require_user(user_id, db)
    account = user.accounts[0] if user.accounts else None
    if account is None:
        raise HTTPException(status_code=422, detail="User has no account for this income change")
    if request.amount_paise <= 0:
        raise HTTPException(status_code=422, detail="Income amount must be positive")
    _save_snapshot(user, db)
    transaction = Transaction(
        txn_id=str(uuid4()), user_id=user.id, account_id=account.id, date=request.date,
        amount_paise=request.amount_paise, raw_description=request.description,
        merchant="Manual income", category="Other Income", category_confidence=1.0, source="manual",
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@app.get("/users/{user_id}/what-changed", response_model=WhatChangedResponse)
def what_changed(user_id: str, db: Session = Depends(get_db)) -> dict:
    user = _require_user(user_id, db)
    latest = db.scalars(
        select(Snapshot).where(Snapshot.user_id == user.id).order_by(Snapshot.created_at.desc())
    ).first()
    if latest is None:
        return {
            "snapshot_id": None, "score_before": None, "score_after": None, "score_delta": None,
            "confidence_before": None, "confidence_after": None, "new_gaps": [], "removed_gaps": [],
            "recommendation_changed": False, "summary": "No changes have been recorded yet.",
            "evidence": [],
        }
    before = latest.metrics_json
    after = _snapshot_payload(user, db)
    before_gaps = set(before.get("gaps", []))
    after_gaps = set(after.get("gaps", []))
    before_score = before.get("health", {}).get("total_score")
    after_score = after.get("health", {}).get("total_score")
    delta = round(after_score - before_score, 2) if before_score is not None and after_score is not None else None
    summary = "Your latest change was applied and the analysis was recalculated."
    if delta is not None:
        summary += f" Health score changed from {before_score} to {after_score}."
    return {
        "snapshot_id": latest.id, "score_before": before_score, "score_after": after_score,
        "score_delta": delta, "confidence_before": before.get("confidence", {}).get("score"),
        "confidence_after": after.get("confidence", {}).get("score"),
        "new_gaps": sorted(after_gaps - before_gaps), "removed_gaps": sorted(before_gaps - after_gaps),
        "recommendation_changed": before.get("recommendation") != after.get("recommendation"),
        "summary": summary, "evidence": [latest.id],
    }
