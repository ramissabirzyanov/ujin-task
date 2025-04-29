from typing import Annotated
from decimal import Decimal
from pathlib import Path
from fastapi import APIRouter
from fastapi import Depends, HTTPException, status

from app.api.schemas import Currency, CurrencySummary, BalanceInput
from app.services.currency_service import CurrencyService


router = APIRouter()


@router.get('/amount/get', response_model=CurrencySummary)
async def get_amount(service: CurrencyService = Depends()):
    total_sum = await service.get_total_amount()
    rates = await service.get_all_rates()
    if not total_sum or not rates:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Can't get data from source, try later please."
        )
    balance = service.balance
    return CurrencySummary(
            balance=balance,
            rates=rates,
            total_sum=total_sum
        )


@router.get('/{currency}/get', response_model=Currency)
async def get_currency(
    currency: Annotated[str, Path(title="Currency code", pattern="^[a-zA-Z]{3}$")],
    service: CurrencyService = Depends()
):
    currency = currency.lower()
    return await service.get_currency_amount(currency)


@router.post('/amount/set', response_model=dict[str, Decimal])
async def set_new_balance(new_balance_data: BalanceInput, service: CurrencyService = Depends()):
    service.balance = new_balance_data.balance
    return service.balance


@router.post('/modify', response_model=dict[str, Decimal])
async def modify_balance(data: BalanceInput, service: CurrencyService = Depends()):
    service.update_balance(data)
    return service.balance
