import csv
from io import BytesIO
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import create_tables, get_db
from .config import settings
from .ingestion.cleaning import clean_transactions
from .ingestion.parser import parse_file
from .models import Account, Transaction, User
from .schemas import UserRead

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

    with persona_file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    user = db.get(User, user_id) or User(id=user_id, name=user_id.title(), source="synthetic")
    db.add(user)
    transactions = clean_transactions(rows, user_id=user_id, source="synthetic")
    account_id = f"{user_id}-primary"
    if db.get(Account, account_id) is None:
        db.add(
            Account(
                id=account_id,
                user_id=user_id,
                type="savings",
                institution="Synthetic bank",
            )
        )
    for transaction in transactions:
        transaction["account_id"] = account_id
    for transaction in transactions:
        if db.get(Transaction, transaction["txn_id"]) is None:
            db.add(Transaction(**transaction))
    db.commit()
    return {"user_id": user_id, "transactions_loaded": len(transactions)}
