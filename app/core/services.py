from httpx import AsyncClient

from app.core.settings import settings
from app.core.logger import logger
from app.core.schemas import USD



class Currency:
    def __init__(self, currency: str):
        self.currency = currency.upper()
        self.url_data = settings.FROM_URL
        

    async def get_currency_rate(self):
        try:
            async with AsyncClient() as client:
                response = await client.get(self.url_data)
                response.raise_for_status()
                data = response.json()
                current_rate = data["Valute"][self.currency]["Value"]
                logger.debug(f"Successfully updated {self.currency} rate: {current_rate}")
                return current_rate
        except KeyError:
            logger.error(f"Failed to fetch {self.currency} rate")
            return None


class USDService:
    
    def __init__(self, value):
        self.value = value
        self.url_data = settings.FROM_URL
    