from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    persona_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    source: Mapped[str] = mapped_column(String(20), default="synthetic")

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    loans: Mapped[list["Loan"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    cards: Mapped[list["Card"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    investments: Mapped[list["Investment"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    recurring_items: Mapped[list["RecurringItem"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    goals: Mapped[list["Goal"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["Snapshot"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    chat_messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(20))
    institution: Mapped[str] = mapped_column(String(120))
    balance_paise: Mapped[int] = mapped_column(Integer, default=0)
    credit_limit_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user: Mapped[User] = relationship(back_populates="accounts")


class Transaction(Base):
    __tablename__ = "transactions"

    txn_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    date: Mapped[date] = mapped_column(Date)
    amount_paise: Mapped[int] = mapped_column(Integer)
    raw_description: Mapped[str] = mapped_column(String(500))
    merchant: Mapped[str] = mapped_column(String(200), default="")
    category: Mapped[str] = mapped_column(String(80), default="")
    category_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(String(20))
    user: Mapped[User] = relationship(back_populates="transactions")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(40))
    principal_paise: Mapped[int] = mapped_column(Integer, default=0)
    outstanding_paise: Mapped[int] = mapped_column(Integer, default=0)
    emi_paise: Mapped[int] = mapped_column(Integer, default=0)
    rate_apr: Mapped[float] = mapped_column(Float, default=0.0)
    tenure_left_months: Mapped[int] = mapped_column(Integer, default=0)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    user: Mapped[User] = relationship(back_populates="loans")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    limit_paise: Mapped[int] = mapped_column(Integer, default=0)
    balance_paise: Mapped[int] = mapped_column(Integer, default=0)
    apr: Mapped[float] = mapped_column(Float, default=0.0)
    min_due_paise: Mapped[int] = mapped_column(Integer, default=0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    user: Mapped[User] = relationship(back_populates="cards")


class Investment(Base):
    __tablename__ = "investments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(40))
    value_paise: Mapped[int] = mapped_column(Integer, default=0)
    monthly_sip_paise: Mapped[int] = mapped_column(Integer, default=0)
    user: Mapped[User] = relationship(back_populates="investments")


class RecurringItem(Base):
    __tablename__ = "recurring_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    merchant: Mapped[str] = mapped_column(String(200))
    amount_paise: Mapped[int] = mapped_column(Integer)
    interval_days: Mapped[int] = mapped_column(Integer)
    next_due_date: Mapped[date] = mapped_column(Date)
    confidence: Mapped[float] = mapped_column(Float)
    txn_ids: Mapped[list[str]] = mapped_column(JSON)
    user: Mapped[User] = relationship(back_populates="recurring_items")


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    target_paise: Mapped[int] = mapped_column(Integer)
    deadline: Mapped[date] = mapped_column(Date)
    user: Mapped[User] = relationship(back_populates="goals")


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    metrics_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    forecast_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    recommendations_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    user: Mapped[User] = relationship(back_populates="snapshots")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))
    content: Mapped[str] = mapped_column(String(10000))
    answer_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    user: Mapped[User] = relationship(back_populates="chat_messages")
