from typing import Annotated
from pathlib import Path
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.api.schemas import Currency
from app.api.services import CurrencyService


router = APIRouter()


@router.get('/{currency}/get', response_model=Currency)
async def get_currency(currency: Annotated[str, Path(title="Currency code", pattern="^[a-zA-Z]{3}$")]):
    currency = currency.upper() 
    pass


@router.get('/amount/get', response_model=Currency)
async def get_amount():
    service = CurrencyService()
    return service.get_value()
