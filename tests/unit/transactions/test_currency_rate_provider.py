import pytest

from app.transactions.currency_rate_provider import Currency, SimpleCurrencyRateToPlnProvider, UnsupportedCurrency


def test_currency_from_str_valid():
    assert Currency.from_str("eur") == Currency.EUR
    assert Currency.from_str("USD") == Currency.USD
    assert Currency.from_str("PlN") == Currency.PLN


def test_currency_from_str_invalid():
    with pytest.raises(UnsupportedCurrency) as exc:
        Currency.from_str("ABC")
    assert "Invalid currency" in str(exc.value)


def test_simple_currency_rate_provider_valid():
    provider = SimpleCurrencyRateToPlnProvider()
    assert provider.get_currency_rate(Currency.EUR) == 4.0
    assert provider.get_currency_rate(Currency.USD) == 3.0
    assert provider.get_currency_rate(Currency.PLN) == 1.0


def test_simple_currency_rate_provider_invalid():
    provider = SimpleCurrencyRateToPlnProvider()
    with pytest.raises(ValueError) as exc:
        provider.get_currency_rate("xyz")
    assert "not supported yet" in str(exc.value)
