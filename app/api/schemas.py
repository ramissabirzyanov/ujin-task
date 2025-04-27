from pydantic import BaseModel


class Currency(BaseModel):
    name: str
    value: float
