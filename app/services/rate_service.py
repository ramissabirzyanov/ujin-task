from abc import ABC, abstractmethod
from typing import Optional
from httpx import AsyncClient, RequestError, Response

from app.core.settings import settings
from app.core.logger import logger


class BaseCurrencyRate(ABC):
    def __init__(self, source: str):
        self.source = source

    @abstractmethod
    async def get_currency_rate(self, currency: str) -> Optional[float]:
        """Абстрактный метод для получения курса валюты"""
        pass

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


class CBRCurrencyRate(BaseCurrencyRate):

    def __init__(self):
        super().__init__(settings.DATA_FROM_CBR)

    async def get_currency_rate(self, currency: str) -> Optional[float]:
        currency = currency.upper()
        response = await self._make_request_to_source()
        if not response:
            return None
        data = await response.json()
        try:
            current_rate = data["Valute"][currency]["Value"]
        except KeyError:
            logger.error(f"Failed to fetch {currency} rate")
            return None
        logger.debug(f"Successfully updated {currency} rate: {current_rate}")
        return current_rate
