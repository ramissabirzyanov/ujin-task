from typing import Annotated
from decimal import Decimal
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.logger import logger

from app.api.schemas import Currency, CurrencySummary, NewBalanceInput, ModifyBalanceInput
from app.api.dependencies import get_currency_service
from app.services.currency_service import CurrencyService


router = APIRouter()


@router.get('/amount/get', response_model=CurrencySummary)
async def get_amount(service: CurrencyService = Depends(get_currency_service)):
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
    service: CurrencyService = Depends(get_currency_service)
):
    currency = currency.lower()
    amount = service.get_currency_amount(currency)
    if amount is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Currency {currency} not found"
        )
    return Currency(name=currency, value=amount)


@router.post('/amount/set', response_model=dict[str, Decimal])
async def set_new_balance(
    new_balance_data: NewBalanceInput,
    service: CurrencyService = Depends(get_currency_service)
):
    service.balance = new_balance_data.new_balance
    return service.balance


@router.post('/modify', response_model=dict[str, Decimal])
async def modify_balance(
    data: ModifyBalanceInput,
    service: CurrencyService = Depends(get_currency_service)
):
    service.modify_balance(data.new_balance)
    return service.balance
