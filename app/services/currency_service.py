from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

from app.core.logger import logger
from app.services.rate_service import BaseCurrencyRate


class CurrencyService:
    # _instance = None

    # def __new__(cls, balance: dict, data_source: BaseCurrencyRate):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #         cls._instance._balance = balance
    #         cls._instance.data_source = data_source
    #     return cls._instance

    def __init__(self, balance: dict, data_source: BaseCurrencyRate):
        self.data_source = data_source
        self._balance = balance

    @property
    def balance(self) -> dict[str, Decimal]:
        """
        Получаем баланс через атрибут.
        """
        return self._balance

    @balance.setter
    def balance(self, new_balance: dict[str, Decimal]):
        """
        Установка новых данных баланса. Перезапись.
        """
        if not isinstance(new_balance, dict):
            raise ValueError("balance must be a dict!")
        self._balance = new_balance
        logger.info(f"New balance was set: {self._balance}")

    def modify_balance(self, updates: dict):
        """
        Изменение значения для валюты из баланса.
        """
        for currency, delta in updates.items():
            if currency not in self._balance:
                raise KeyError(
                    f"There is no currency {currency} in current balance to modify it!"
                )
            old_value = self._balance[currency]
            self._balance[currency] += delta
            logger.info(f"Balance {currency}: {old_value} -> {self._balance[currency]}")

    def get_currency_amount(self, currency: str) -> Decimal:
        """
        Получаем значение для конкретной валюты из баланса
        """
        try:
            amount = self.balance[currency]
            return amount
        except KeyError:
            logger.error(f"Not such {currency} in balance")
            return None

    async def get_all_rates(self) -> dict:
        """
        Получаем курсы валют из баланса по отношению к основной валюте,
        а также по отношению друг к другу.
        """
        currencies = list(self.balance.keys())
        currency_rates = await self.data_source.get_currency_rate(currencies)
        rates_to_output = self.data_source.output_formattor(currency_rates)
        return rates_to_output

    async def get_total_amount(self) -> dict[str, Decimal]:
        """
        Получаем общее количество в каждой валюте из баланса.
        """
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
                try:
                    rate = conversions[other_currency][currency]
                except KeyError:
                    logger.error(f"Failed to fetch {other_currency}-{currency} rate")
                    continue
                total += other_amount * rate
            result[currency] = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return result
