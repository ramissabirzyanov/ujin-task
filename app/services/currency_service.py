from decimal import Decimal, ROUND_HALF_UP
from itertools import combinations
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
        return self._balance

    @balance.setter
    def balance(self, new_balance: dict[str, Decimal]):
        if not isinstance(new_balance, dict):
            raise ValueError("balance must be a dict!")
        self._balance = new_balance
        logger.info(f"New balance was set: {self._balance}")

    def modify_balance(self, updates: dict):
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
        all_rates = {}
        currency_rates = []
        base_currency_rate = self.data_source.get_base_currency_rate_of_source()
        
        if self.data_source.base_currency in self.balance and len(self.balance) == 1:
            return {
                f"{self.data_source.base_currency}-{self.data_source.base_currency}": base_currency_rate[1]
            }

        if self.data_source.base_currency in self.balance:
            currency_rates.append(self.data_source.get_base_currency_rate_of_source())

        currencies = [currency for currency in self.balance if currency != self.data_source.base_currency]  # default ['usd', 'eur', 'rub'] if balance = {}
        for currency in currencies:
            currency, rate = await self.data_source.get_currency_rate(currency)
            if not rate:
                logger.info(f"There no rate for currency {currency} on the source: {self.data_source}.")
                continue
            currency_rates.append((currency,rate))

        for cur_rate1, cur_rate2 in combinations(currency_rates, 2):
            cross_rate = cur_rate1[1]/cur_rate2[1]
            all_rates[f'{cur_rate1[0]}-{cur_rate2[0]}'] = cross_rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return all_rates

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
