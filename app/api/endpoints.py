from typing import Annotated
from pathlib import Path
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.api.schemas import Currency, CurrencySummary
from app.services.currency_service import CurrencyService


router = APIRouter()


@router.get('/{currency}/get', response_model=Currency)
async def get_currency(
    currency: Annotated[str, Path(title="Currency code", pattern="^[a-zA-Z]{3}$")],
    service: CurrencyService = Depends()
):
    currency = currency.lower()
    return await service.get_currency_amount(currency)


@router.get('/amount/get', response_model=CurrencySummary)
async def get_amount(service: CurrencyService = Depends()):
    total_sum = await service.get_total_amount()
    rates = await service.get_all_rates()
    balance = service.balance
    return CurrencySummary(
            balance=balance,
            rates=rates,
            total_sum=total_sum
        )
