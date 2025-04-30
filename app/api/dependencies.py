from fastapi import Request

from app.services.rate_service import BaseCurrencyRate, cbr_currency_rate
from app.services.currency_service import CurrencyService


def get_data_source() -> BaseCurrencyRate:
    """Источник данных"""
    return cbr_currency_rate


def get_balance(request: Request) -> dict:
    """Получение баланса и созранение  в состояние"""
    return request.app.state.cli_args.balance


def get_currency_service(request: Request) -> CurrencyService:
    "Получение экземпляра класс и сохранение в состояние"
    return request.app.state.currency_service
