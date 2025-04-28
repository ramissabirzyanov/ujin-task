from decimal import Decimal

from pydantic import BaseModel


class Currency(BaseModel):
    name: str
    value: Decimal
