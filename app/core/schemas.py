from pydantic import BaseModel


class USDResponse(BaseModel):
    name: str
    value: float