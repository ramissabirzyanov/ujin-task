from httpx import AsyncClient, RequestError

from app.core.settings import settings
from app.core.logger import logger
from abc import ABC, abstractmethod
from typing import Optional


class BaseCurrencyRate(ABC):
    @abstractmethod
    async def get_currency_rate(self, currency: str) -> Optional[float]:
        """Абстрактный метод для получения курса валюты"""
        pass

class CBRCurrencyRate(BaseCurrencyRate):
    def __init__(self):
        self.url_data = settings.DATA_FROM_CBR

    async def get_currency_rate(self, currency: str):
        try:
            currency = currency.upper()
            async with AsyncClient() as client:
                response = await client.get(self.url_data)
                response.raise_for_status()
                data =  await response.json()
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
    def __init__(self):
        pass