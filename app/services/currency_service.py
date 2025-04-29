from decimal import Decimal
from itertools import combinations
from collections import defaultdict
from fastapi import Depends

from app.core.logger import logger
from app.api.dependencies import get_data_source, get_balance, get_debug
from app.services.rate_service import BaseCurrencyRate


class CurrencyService:
    def __init__(
        self,
        data_source: BaseCurrencyRate = Depends(get_data_source),
        balance=Depends(get_balance),
        debug=Depends(get_debug)
    ):
        self.data_source = data_source
        self._balance = balance
        self.debug = debug

    @property
    def balance(self) -> dict[str, Decimal]:
        return self._balance

    @balance.setter
    def balance(self, new_balance: dict[str, Decimal]):
        if not isinstance(new_balance, dict):
            raise ValueError("balance must be a dict!")
        self._balance = new_balance
        logger.info(f"New balance was set: {self._balance}")

    def update_balance(self, updates: dict):
        for currency, delta in updates.items():
            if currency not in self._balance:
                raise KeyError(f"There is no {currency} in current balance")
            old_value = self._balance[currency]
            self._balance[currency] += delta
            logger.info(f"Balance {currency}: {old_value} -> {self._balance[currency]}")

    def get_currency_amount(self, currency) -> Decimal:
        return self.balance[currency]

    async def get_all_rates(self) -> dict:
        currency_rates = {}
        currencies = [currency for currency in self.balance if currency != "rub"]
        for currency in currencies:
            rate = await self.data_source.get_currency_rate(currency)
            if not rate:
                logger.info(f"Something is wrong: {currency} rate is None.")
                continue
            currency_rates[currency] = rate

        for currency1, currency2 in combinations(currencies, 2):
            rate1 = currency_rates[currency1]
            rate2 = currency_rates[currency2]
            currency_rates[f"{currency1}-{currency2}"] = rate1 / rate2

        return currency_rates

    async def get_total_amount(self) -> dict[str, Decimal]:
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
                    return None
                total += other_amount * rate
            result[currency] = round(total, 2)
        return result

