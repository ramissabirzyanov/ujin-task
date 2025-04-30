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
                    "eur": 10,
                    "rub": -20
                }
            }
        }

# result = {}
# from itertools import combinations
# currency_rates = [('usd', 60), ('eur', 100), ('chy', 10), ('rub', 1)]

# for cur_rate1, cur_rate2 in combinations(currency_rates, 2):
#     result[f'{cur_rate1[0]}-{cur_rate2[0]}'] = cur_rate1[1]/cur_rate2[1]
# print(result)

