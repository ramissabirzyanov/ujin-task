from httpx import AsyncClient, RequestError, Response
from abc import ABC, abstractmethod
from typing import Optional
from itertools import combinations
from collections import defaultdict

from app.core.settings import settings
from app.core.setup_parser import setup_parser
from app.core.logger import logger


class BaseCurrencyRate(ABC):
    def __init__(self, source: str):
        self.source = source
        
    @abstractmethod
    async def get_currency_rate(self, currency: str) -> Optional[float]:
        """Абстрактный метод для получения курса валюты"""
        pass

    async def _make_request_to_source(self) -> Response:
        try:
            async with AsyncClient() as client:
                logger.debug(f"Requesting {self.source}")
                response = await client.get(self.source)
                response.raise_for_status()
                return response
        except RequestError as e:
            logger.error(f"Request to {self.source} failed with error: {e}")
            return None

class CBRCurrencyRate(BaseCurrencyRate):

    def __init__(self):
        super().__init__(settings.DATA_FROM_CBR)

    async def get_currency_rate(self, currency: str) -> Optional[float]:
        currency = currency.upper()
        response = await self._make_request_to_source()
        data = await response.json()
        try:
            current_rate = data["Valute"][currency]["Value"]
        except KeyError:
            logger.error(f"Failed to fetch {currency} rate")
            return None
        logger.debug(f"Successfully updated {currency} rate: {current_rate}")
        return current_rate


class CurrencyService:
    def __init__(self, data_source: BaseCurrencyRate = CBRCurrencyRate()):
        self.data_source = data_source
        self.currency = None
        self.currency_rates = {}
        args = setup_parser()
        self._balance = args.balance

    @property
    def balance(self) -> dict:
        return self._balance

    async def get_all_rates(self) -> dict: 
        for currency in self.balance:
            if currency == 'rub':
                continue
            rate = await self.data_source.get_currency_rate(currency)
            if not rate:
                logger.info(f"Something is wrong: {currency} rate is None.")
                continue
            self.currency_rates[f'{currency}-rub'] = rate

        for currency1, currency2 in combinations(self.currency_rates.keys(), 2):
            rate1 = self.currency_rates[currency1]
            rate2 = self.currency_rates[currency2] 
            self.currency_rates[f"{currency1}-{currency2}"] = rate1 / rate2

        return self.currency_rates


    async def get_total_amount(self):
        conversions = defaultdict(dict)
        all_rates = await self.get_all_rates() 
        for pair, rate in all_rates.items():
            currency_from, currency_to = pair.split('-')

            conversions[currency_from][currency_to] = rate
            conversions[currency_to][currency_from] = 1/rate

        result = {}
        for currency, amount in self.balance.items():
            total = amount
            for other_currency, other_amount in self.balance.items():
                if other_currency == currency:
                    continue
                rate = conversions[other_currency][currency]
                total += other_amount * rate
            result[currency] = round(total, 2)
        return result
