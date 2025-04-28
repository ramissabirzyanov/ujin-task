from app.api.services import BaseCurrencyRate, CBRCurrencyRate
from app.core.setup_parser import setup_parser


def get_data_source() -> BaseCurrencyRate:
    return CBRCurrencyRate()


def get_balance() -> dict:
    args = setup_parser()
    return args.banance
