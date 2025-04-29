from decimal import Decimal

from pydantic import BaseModel


class Currency(BaseModel):
    name: str
    value: Decimal


class CurrencySummary(BaseModel):
    balance: dict[str, Decimal]
    rates: dict[str, Decimal]
    total_sum: dict[str, Decimal]


class BalanceInput(BaseModel):
    balance: dict[str, Decimal]
