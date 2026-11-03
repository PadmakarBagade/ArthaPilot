from datetime import date
from pydantic import BaseModel, Field


class ForecastRead(BaseModel):
    dates: list[date]
    p10_paise: list[int]
    p50_paise: list[int]
    p90_paise: list[int]
    probability_below_zero: list[float] = Field(default_factory=list)
    runs: int
    seed: int
    start_balance_paise: int


class GapRead(BaseModel):
    date: date
    expected_balance_paise: int
    probability_below_zero: float
    evidence: str


class StressRequest(BaseModel):
    scenario: str
    new_emi_paise: int = 0


class StressRead(BaseModel):
    scenario: str
    forecast: ForecastRead
    survival_days: int
    first_breach_date: date | None
