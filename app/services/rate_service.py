from abc import ABC, abstractmethod
from typing import Optional
from httpx import AsyncClient, RequestError, Response
from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations

from app.core.settings import settings
from app.core.logger import logger


class BaseCurrencyRate(ABC):
    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    def get_base_currency_rate_of_source(self) -> Decimal:
        """
        Абстрактный метод для получения курса основой валюты,
        относительно которой будут курсы других валют.
        """
        pass

    @abstractmethod
    async def get_currency_rate(self, currency: str) -> Optional[dict[str, Decimal]]:
        """Абстрактный метод для получения курса валюты по отношению к основной."""
        pass

    @abstractmethod
    def output_formattor(self, currency_rates: dict) -> dict:
        """Абстрактный метод для формата вывода"""
        pass



class CBRCurrencyRate(BaseCurrencyRate):

    def __init__(self):
        super().__init__(source=settings.DATA_FROM_CBR)
        self.base_currency = 'rub'

    def get_base_currency_rate_of_source(self):
        """
        Получение словаря вида {rub: 1.0}
        Чтобы в дальнейшем удобно получать курс вида {usd-rub: 60}
        """
        return {self.base_currency: Decimal('1')}
    
    async def _make_request_to_source(self) -> Optional[Response]:
        try:
            async with AsyncClient() as client:
                logger.debug(f"Requesting {self.source}")
                response = await client.get(self.source)
                response.raise_for_status()
                return response
        except RequestError as e:
            logger.error(f"Request to {self.source} failed with error: {e}")
            return None

    async def get_currency_rate(self, currencies: list) -> Optional[dict[str, Decimal]]:
        """
        Данные о курсе валюты к рублю от ЦБР. По умолчанию USD и EUR.
        """

        if self.base_currency in currencies and len(currencies) == 1:
            currencies = ['eur', 'usd', self.base_currency]
        currency_rate = {}
        response = await self._make_request_to_source()
        if not response:
            return None
        data = response.json()  # по хорошему надо в кэш. Например self._cache = {}

        for currency in currencies:
            if currency == self.base_currency:
                continue
            try:
                rate = data["Valute"][currency.upper()]["Value"]
                logger.debug(f"Successfully updated {currency} rate: {rate}")
                currency_rate[currency] = Decimal(rate)
            except KeyError:
                logger.error(f"Failed to fetch {currency} rate")
                continue
        return currency_rate | self.get_base_currency_rate_of_source()

    def output_formattor(self, currency_rates: dict) -> dict:
        readble_output = {}
        for cur1, cur2 in combinations(currency_rates, 2):
            rate1 = currency_rates[cur1]
            rate2 = currency_rates[cur2]
            cross_rate = rate1/rate2
            rounded_rate = cross_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            readble_output[f"{cur1}-{cur2}"] = rounded_rate
            # readble_output[f"{cur1}-{cur2}"] =cross_rate
        return readble_output


cbr_currency_rate = CBRCurrencyRate()
