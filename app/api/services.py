from httpx import AsyncClient, RequestError, Response

from app.core.settings import settings
from app.core.setup_parser import setup_parser
from app.core.logger import logger
from abc import ABC, abstractmethod
from typing import Optional


class BaseCurrencyRate(ABC):
    def __init__(self, source: str):
        self.source = source
        
    @abstractmethod
    async def get_currency_rate(self, currency: str) -> Optional[float]:
        """Абстрактный метод для получения курса валюты"""
        pass

    async def _make_request_to_source(self) -> Response:
        async with AsyncClient() as client:
            logger.debug(f"Requesting {self.source}")
            response = await client.get(self.source)
            response.raise_for_status()
            return response

class CBRCurrencyRate(BaseCurrencyRate):

    def __init__(self):
        super().__init__(settings.DATA_FROM_CBR)

    async def get_currency_rate(self, currency: str) -> Optional[float]:
        try:
            currency = currency.upper()
            response = await self._make_request_to_source()
            data = await response.json()
        except RequestError as e:
            logger.error(f"Request failed for {currency}: {e}")
            return None

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

    async def get_value(self):
        args = setup_parser()
        balance = args.balance #dict
        if args.debug:
            response = await self.data_source._make_request_to_source()
            logger.debug(f"Request URL: {response.request.url}")
            logger.debug(f"Request headers: {response.request.headers}")
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response body: {response.text}")
        logger.info("Here we go...!")
        return balance
# /{currency}/ self.currency = None ? 
