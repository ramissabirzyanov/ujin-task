from fastapi import Depends, Request

from app.services.rate_service import BaseCurrencyRate, cbr_currency_rate
from app.services.currency_service import CurrencyService


def get_data_source() -> BaseCurrencyRate:
    """Источник данных"""
    return cbr_currency_rate


def get_balance(request: Request) -> dict:
    """Абстрагируем получение баланса"""
    return request.app.state.parsed_args.balance


def get_currency_service(
    balance: dict = Depends(get_balance),
    data_source: BaseCurrencyRate = Depends(get_data_source)
) -> CurrencyService:
    return CurrencyService(balance, data_source)
