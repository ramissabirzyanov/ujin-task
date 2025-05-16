from decimal import Decimal

from pydantic import BaseModel, RootModel


class Currency(BaseModel):
    name: str
    value: Decimal


class CurrencySummary(BaseModel):
    balance: dict[str, Decimal]
    rates: dict[str, Decimal]
    total_sum: dict[str, Decimal]


class NewBalanceInput(RootModel):
    root: dict[str, Decimal]

    class Config:
        json_schema_extra = {
            "example": {
                "usd": 100.50,
                "eur": 200.75
                }
            }


class ModifyBalanceInput(NewBalanceInput):

    class Config:
        json_schema_extra = {
            "example": {
                "eur": 10,
                "rub": -20
                }
            }
