from app.api.services import BaseCurrencyRate, CBRCurrencyRate

def get_data_source() -> BaseCurrencyRate:
    return CBRCurrencyRate()
