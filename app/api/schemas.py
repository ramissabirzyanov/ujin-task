from decimal import Decimal

from pydantic import BaseModel


class Currency(BaseModel):
    name: str
    value: Decimal


class CurrencySummary(BaseModel):
    balance: dict[str, Decimal]
    rates: dict[str, Decimal]
    total_sum: dict[str, Decimal]


class NewBalanceInput(BaseModel):
    new_balance: dict[str, Decimal]

    class Config:
        json_schema_extra = {
            "example": {
                "new_balance": {
                    "usd": 100.50,
                    "eur": 200.75
                }
            }
        }


class ModifyBalanceInput(NewBalanceInput):

    class Config:
        json_schema_extra = {
            "example": {
                "new_balance": {
                    "eur": 10, "rub": -20
                }
            }
        }
