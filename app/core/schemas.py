from pydantic import BaseModel


class Currency(BaseModel):
    name: str
    value: float


class USD(Currency):
    pass

class RUB(Currency):
    pass

class EUR(Currency):
    pass
