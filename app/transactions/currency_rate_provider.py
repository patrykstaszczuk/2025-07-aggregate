from abc import ABC, abstractmethod
from enum import StrEnum


class UnsupportedCurrency(Exception):
    pass


class Currency(StrEnum):
    EUR = "EUR"
    USD = "USD"
    PLN = "PLN"

    @classmethod
    def from_str(cls, value: str):
        normalized = value.upper()
        try:
            return cls(normalized)
        except ValueError:
            raise UnsupportedCurrency(f"Invalid currency: {value}")


class CurrencyRateProvider(ABC):
    _RATES: dict

    @abstractmethod
    def get_currency_rate(self, currency: Currency) -> float:
        pass


class SimpleCurrencyRateToPlnProvider(CurrencyRateProvider):
    _RATES = {
        Currency.EUR: 4.0,
        Currency.USD: 3.0,
        Currency.PLN: 1.0,
    }

    def get_currency_rate(self, currency: Currency) -> float:
        if currency not in self._RATES:
            raise ValueError(f"Currency={currency} not supported yet")
        return self._RATES[currency]
