from app.services.rate_service import BaseCurrencyRate, cbr_currency_rate


_parsed_args = None

def set_parsed_args(args):
    global _parsed_args
    _parsed_args = args

def get_balance():
    return _parsed_args.balance

def is_debug():
    return _parsed_args.debug

def get_data_source() -> BaseCurrencyRate:
    return cbr_currency_rate
