from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base, create_tables
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


def test_all_database_models_persist_one_row_each():
    engine = create_engine("sqlite:///:memory:")
    create_tables(engine)

    with Session(engine) as session:
        user = User(id="u1", name="Test User", persona_type="test")
        account = Account(
            id="a1",
            user=user,
            type="savings",
            institution="Test Bank",
            balance_paise=10000,
        )
        session.add_all(
            [
                user,
                account,
                Transaction(
                    txn_id="t1",
                    user=user,
                    account_id="a1",
                    date=date(2026, 1, 1),
                    amount_paise=-100,
                    raw_description="Test",
                    source="synthetic",
                ),
                Loan(
                    id="l1",
                    user=user,
                    type="personal",
                    principal_paise=100000,
                    outstanding_paise=90000,
                    emi_paise=5000,
                    rate_apr=12.0,
                    tenure_left_months=24,
                    next_due_date=date(2026, 2, 1),
                ),
                Card(
                    id="c1",
                    user=user,
                    limit_paise=200000,
                    balance_paise=10000,
                    apr=24.0,
                    min_due_paise=500,
                    due_date=date(2026, 2, 5),
                ),
                Investment(
                    id="i1",
                    user=user,
                    type="mutual_fund",
                    value_paise=50000,
                    monthly_sip_paise=5000,
                ),
                RecurringItem(
                    id="r1",
                    user=user,
                    merchant="Streaming",
                    amount_paise=999,
                    interval_days=30,
                    next_due_date=date(2026, 2, 1),
                    confidence=0.9,
                    txn_ids=["t1"],
                ),
                Goal(
                    id="g1",
                    user=user,
                    name="Emergency fund",
                    target_paise=1000000,
                    deadline=date(2026, 12, 31),
                ),
                Snapshot(
                    id="s1",
                    user=user,
                    metrics_json={"score": 80},
                    forecast_json={"months": 3},
                    recommendations_json={"items": []},
                ),
                ChatMessage(
                    id="m1",
                    user=user,
                    role="user",
                    content="How am I doing?",
                    answer_json={"sections": []},
                ),
            ]
        )
        session.commit()

        assert session.query(User).count() == 1
        assert session.query(Account).count() == 1
        assert session.query(Transaction).count() == 1
        assert session.query(Loan).count() == 1
        assert session.query(Card).count() == 1
        assert session.query(Investment).count() == 1
        assert session.query(RecurringItem).count() == 1
        assert session.query(Goal).count() == 1
        assert session.query(Snapshot).count() == 1
        assert session.query(ChatMessage).count() == 1
