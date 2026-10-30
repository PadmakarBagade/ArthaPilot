from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class SchemaBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserRead(SchemaBase):
    id: str
    name: str
    persona_type: str | None = None
    created_at: datetime
    source: str = "synthetic"


class AccountRead(SchemaBase):
    id: str
    user_id: str
    type: str
    institution: str
    balance_paise: int
    credit_limit_paise: int | None = None


class TransactionRead(SchemaBase):
    txn_id: str
    user_id: str
    account_id: str
    date: date
    amount_paise: int
    raw_description: str
    merchant: str
    category: str
    category_confidence: float
    is_recurring: bool
    source: str
    is_self_transfer: bool = False


class LoanRead(SchemaBase):
    id: str
    user_id: str
    type: str
    principal_paise: int
    outstanding_paise: int
    emi_paise: int
    rate_apr: float
    tenure_left_months: int
    next_due_date: date | None = None


class CardRead(SchemaBase):
    id: str
    user_id: str
    limit_paise: int
    balance_paise: int
    apr: float
    min_due_paise: int
    due_date: date | None = None


class InvestmentRead(SchemaBase):
    id: str
    user_id: str
    type: str
    value_paise: int
    monthly_sip_paise: int


class RecurringItemRead(SchemaBase):
    id: str
    user_id: str
    merchant: str
    amount_paise: int
    interval_days: int
    next_due_date: date
    confidence: float
    txn_ids: list[str]


class ProcessResponse(BaseModel):
    user_id: str
    transaction_count: int
    category_breakdown: dict[str, int]
    confidence_summary: dict[str, float]
    recurring_count: int
    income: dict[str, Any]


class GoalRead(SchemaBase):
    id: str
    user_id: str
    name: str
    target_paise: int
    deadline: date


class SnapshotRead(SchemaBase):
    id: str
    user_id: str
    created_at: datetime
    metrics_json: dict[str, Any]
    forecast_json: dict[str, Any]
    recommendations_json: dict[str, Any]


class ChatMessageRead(SchemaBase):
    id: str
    user_id: str
    role: str
    content: str
    answer_json: dict[str, Any] | None = None
    created_at: datetime
