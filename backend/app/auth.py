import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import SessionToken, User


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"{salt}${key.hex()}"


def verify_password(password: str, stored_hash: str | None) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt, expected_hex = stored_hash.split("$", 1)
    key = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return hmac.compare_digest(key.hex(), expected_hex)


def create_session(db: Session, user_id: str, days: int = 30) -> str:
    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(days=days)
    session = SessionToken(token=token, user_id=user_id, created_at=now, expires_at=expires_at)
    db.add(session)
    db.commit()
    return token


def get_user_by_token(db: Session, token: str | None) -> User | None:
    if not token:
        return None
    session = db.get(SessionToken, token)
    if session is None:
        return None
    now = datetime.now(timezone.utc)
    # Ensure session expires_at is compared timezone-aware
    expires = session.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if expires < now:
        db.delete(session)
        db.commit()
        return None
    return session.user


def get_current_user(
    authorization: str | None = Header(None),
    token: str | None = Query(None),
    db: Session = Depends(get_db),
) -> User:
    raw_token = None
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.split("Bearer ", 1)[1].strip()
    elif token:
        raw_token = token

    user = get_user_by_token(db, raw_token)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token",
        )
    return user

