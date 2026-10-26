from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import create_tables, get_db
from .ingestion.cleaning import clean_transactions
from .ingestion.parser import parse_file
from .models import Transaction, User
from .schemas import UserRead

app = FastAPI(title="ArthaPilot")
create_tables()
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
) -> dict[str, int | str]:
    try:
        rows = parse_file(file.file, file.filename or Path(file.file.name).name)
        user_id = f"upload-{Path(file.filename or 'statement').stem}"
        user = db.get(User, user_id)
        if user is None:
            user = User(id=user_id, name=user_id, source="real")
            db.add(user)
        transactions = clean_transactions(rows, user_id=user_id, source="real")
        for transaction in transactions:
            if db.get(Transaction, transaction["txn_id"]) is None:
                db.add(Transaction(**transaction))
        db.commit()
        return {"user_id": user_id, "transactions_loaded": len(transactions)}
    except (ValueError, KeyError) as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/users/{user_id}/load-persona")
def load_persona(user_id: str, db: Session = Depends(get_db)) -> dict[str, int | str]:
    persona_file = Path(__file__).parents[2] / "data" / "synthetic" / f"{user_id}.csv"
    if not persona_file.exists():
        raise HTTPException(status_code=404, detail="Persona not found")
    import csv

    with persona_file.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    user = db.get(User, user_id) or User(id=user_id, name=user_id.title(), source="synthetic")
    db.add(user)
    transactions = clean_transactions(rows, user_id=user_id, source="synthetic")
    for transaction in transactions:
        if db.get(Transaction, transaction["txn_id"]) is None:
            db.add(Transaction(**transaction))
    db.commit()
    return {"user_id": user_id, "transactions_loaded": len(transactions)}
