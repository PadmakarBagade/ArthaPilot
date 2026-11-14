"""ArthaPilot UserState (DEC-05, DEC-06, F3).

One UserState dataclass is built once per request by this service and passed to engines.
The simulator works on immutable copies.
All time logic uses injected `as_of` date (DEC-05).
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.finance.defs import is_expense, is_income, liquid_balance_paise, monthly_debt_service_paise
from app.models import Account, Card, Goal, Investment, Loan, RecurringItem, Transaction, User


@dataclass
class UserState:
    user_id: str
    user_name: str
    accounts: List[Account] = field(default_factory=list)
    transactions: List[Transaction] = field(default_factory=list)
    loans: List[Loan] = field(default_factory=list)
    cards: List[Card] = field(default_factory=list)
    investments: List[Investment] = field(default_factory=list)
    recurring_items: List[RecurringItem] = field(default_factory=list)
    goals: List[Goal] = field(default_factory=list)
    as_of: date = field(default_factory=date.today)

    @property
    def liquid_balance(self) -> int:
        """DEC-10: Liquid balance across savings and current accounts only."""
        return liquid_balance_paise(self.accounts)

    @property
    def debt_service_paise(self) -> int:
        """F5: Monthly debt payments from loans + cards + unmatched EMIs."""
        return monthly_debt_service_paise(self.loans, self.cards, self.transactions)

    @property
    def total_card_balance_paise(self) -> int:
        return sum(c.balance_paise for c in self.cards)

    @property
    def total_card_limit_paise(self) -> int:
        return sum(c.limit_paise for c in self.cards if c.limit_paise)

    @property
    def total_investment_value_paise(self) -> int:
        return sum(i.value_paise for i in self.investments)

    @property
    def total_monthly_sip_paise(self) -> int:
        return sum(i.monthly_sip_paise for i in self.investments)


def build_user_state(
    db: Session,
    user_id: str,
    as_of: Optional[date] = None,
) -> UserState:
    """DEC-06: Builds canonical UserState once per request from database."""
    user = db.get(User, user_id)
    user_name = user.name if user else user_id.title()

    accounts = list(db.scalars(select(Account).where(Account.user_id == user_id)).all())
    transactions = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.date.asc())
        ).all()
    )
    loans = list(db.scalars(select(Loan).where(Loan.user_id == user_id)).all())
    cards = list(db.scalars(select(Card).where(Card.user_id == user_id)).all())
    investments = list(db.scalars(select(Investment).where(Investment.user_id == user_id)).all())
    recurring = list(db.scalars(select(RecurringItem).where(RecurringItem.user_id == user_id)).all())
    goals = list(db.scalars(select(Goal).where(Goal.user_id == user_id)).all())

    # DEC-05: Demo clock: as_of = max(transaction date) + 1 day unless explicitly supplied
    if as_of is None:
        if transactions:
            max_txn_date = max(t.date for t in transactions)
            as_of = max_txn_date + timedelta(days=1)
        else:
            as_of = date.today()

    return UserState(
        user_id=user_id,
        user_name=user_name,
        accounts=accounts,
        transactions=transactions,
        loans=loans,
        cards=cards,
        investments=investments,
        recurring_items=recurring,
        goals=goals,
        as_of=as_of,
    )

