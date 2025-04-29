from app.services.rate_service import BaseCurrencyRate, cbr_currency_rate
from app.core.setup_parser import setup_parser


def get_data_source() -> BaseCurrencyRate:
    return cbr_currency_rate


def get_balance() -> dict:
    args = setup_parser()
    return args.balance


def get_debug() -> bool:
    args = setup_parser()
    return args.debug
