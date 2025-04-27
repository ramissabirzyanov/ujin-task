from httpx import AsyncClient, RequestError

from app.core.settings import settings
from app.core.logger import logger


balances = {
    "usd": 60,
    "rub": 100,
    "eur": 300,
}


class CurrencyRate:
    url_data = settings.FROM_URL

    def __init__(self, currency: str):
        self.currency = currency.upper()

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
        except RequestError as e:
            logger.error(f"Request failed for {self.currency}: {e}")
            return None


class USDService(CurrencyRate):

    def __init__(self, value):
        super().__init__('USD')
        self.value = value

    async def get_value():
        return balances['usd']
    

class RUBService(CurrencyRate):
    def __init__(self, value):

        super().__init__('RUB')
        self.value = value

class EURService(CurrencyRate):
    def __init__(self, value):

        super().__init__('EUR')
        self.value = value

