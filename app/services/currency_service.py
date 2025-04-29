from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations
from collections import defaultdict

from app.core.logger import logger
from app.services.rate_service import BaseCurrencyRate


class CurrencyService:
    def __init__(
        self,
        balance: dict,
        data_source: BaseCurrencyRate
    ):
        self.data_source = data_source
        self._balance = balance

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
                raise KeyError(
                    f"There is no currency {currency} in current balance to modify it!"
                )
            old_value = self._balance[currency]
            self._balance[currency] += delta
            logger.info(f"Balance {currency}: {old_value} -> {self._balance[currency]}")

    def get_currency_amount(self, currency: str) -> Decimal:
        try:
            amount = self.balance[currency]
            return amount
        except KeyError:
            logger.error(f"Not such {currency} in balance")
            return None

    async def get_all_rates(self) -> dict:
        currency_rates = {}
        currencies = [currency for currency in self.balance if currency != "rub"] #default ['usd', 'eur'] if balance = {}
        for currency in currencies:
            rate = await self.data_source.get_currency_rate(currency)
            if not rate:
                logger.error(f"Something is wrong: {currency} rate is None.")
                continue
            currency_rates[f'{currency}-rub'] = rate

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
                total += other_amount * Decimal(str(rate))
            result[currency] = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return result
