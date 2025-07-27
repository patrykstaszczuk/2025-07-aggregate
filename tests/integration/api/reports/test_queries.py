from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.api.reports.queries import (
    get_last_transaction_timestamp_for_customer,
    get_sold_qty_of_product,
    get_total_cost_pln_for_customer,
    get_total_income_for_product_in_pln,
    get_total_number_of_unique_customers_for_product,
    get_unique_products_count_for_customer,
)
from app.transactions.currency_rate_provider import (
    Currency,
    SimpleCurrencyRateToPlnProvider,
    UnsupportedCurrency,
)
from app.transactions.models import Transaction


@pytest.fixture
def customer_id():
    return uuid4()


@pytest.fixture
def another_customer_id():
    return uuid4()


def test_total_cost_single_pln_transaction(db_session: Session, customer_id):
    tx = Transaction(
        customer_id=customer_id,
        amount=100,
        quantity=2,
        currency="PLN",
        product_id=uuid4(),
        timestamp=datetime.utcnow(),
    )
    db_session.add(tx)
    db_session.commit()

    result = get_total_cost_pln_for_customer(db_session, customer_id)
    assert result == 200.0


def test_total_cost_eur_transaction(db_session: Session, customer_id):
    tx = Transaction(
        customer_id=customer_id,
        amount=50,
        quantity=2,
        currency="EUR",
        product_id=uuid4(),
        timestamp=datetime.utcnow(),
    )
    db_session.add(tx)
    db_session.commit()

    result = get_total_cost_pln_for_customer(db_session, customer_id)
    assert result == 50 * 2 * 4.0  # EUR => 4.0


def test_total_cost_mixed_currencies(db_session: Session, customer_id):
    db_session.add_all(
        [
            Transaction(
                customer_id=customer_id,
                amount=10,
                quantity=1,
                currency="USD",
                product_id=uuid4(),
                timestamp=datetime.utcnow(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=20,
                quantity=1,
                currency="EUR",
                product_id=uuid4(),
                timestamp=datetime.utcnow(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=30,
                quantity=1,
                currency="PLN",
                product_id=uuid4(),
                timestamp=datetime.utcnow(),
            ),
        ],
    )
    db_session.commit()

    result = get_total_cost_pln_for_customer(db_session, customer_id)
    assert result == (10 * 1 * 3.0) + (20 * 1 * 4.0) + (30 * 1 * 1.0)


def test_total_cost_no_transactions(db_session: Session, another_customer_id):
    result = get_total_cost_pln_for_customer(db_session, another_customer_id)
    assert result is None


def test_total_cost_unsupported_currency(db_session: Session, customer_id):
    tx = Transaction(
        customer_id=customer_id,
        amount=100,
        quantity=1,
        currency="GBP",
        product_id=uuid4(),
        timestamp=datetime.utcnow(),
    )
    db_session.add(tx)
    db_session.commit()

    with pytest.raises(UnsupportedCurrency):
        get_total_cost_pln_for_customer(db_session, customer_id)


def test_unique_products_count(db_session: Session, customer_id):
    pid = uuid4()
    db_session.add_all(
        [
            Transaction(
                customer_id=customer_id,
                amount=1,
                quantity=1,
                currency="PLN",
                product_id=pid,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=1,
                quantity=1,
                currency="PLN",
                product_id=pid,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=1,
                quantity=1,
                currency="PLN",
                product_id=uuid4(),
                timestamp=datetime.now(),
            ),
        ],
    )
    db_session.commit()

    result = get_unique_products_count_for_customer(db_session, customer_id)
    assert result == 2


def test_total_cost_no_transactions(db_session, customer_id):
    total = get_total_cost_pln_for_customer(db_session, customer_id)
    assert total is None or total == 0.0


def test_last_transaction_timestamp(db_session, customer_id):
    now = datetime.now(timezone.utc)

    transaction = Transaction(
        customer_id=customer_id,
        product_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        amount=100,
        quantity=1,
        currency="PLN",
        timestamp=now,
    )
    db_session.add(transaction)
    db_session.commit()

    response = get_last_transaction_timestamp_for_customer(db_session, customer_id)
    assert response == now


def test_last_transaction_timestamp_none(db_session: Session, another_customer_id):
    result = get_last_transaction_timestamp_for_customer(db_session, another_customer_id)
    assert result is None


@pytest.mark.parametrize(
    "input_str,expected",
    [
        ("eur", Currency.EUR),
        ("EUR", Currency.EUR),
        ("Usd", Currency.USD),
        ("pln", Currency.PLN),
    ],
)
def test_currency_from_str_valid(input_str, expected):
    assert Currency.from_str(input_str) == expected


def test_currency_from_str_invalid():
    with pytest.raises(UnsupportedCurrency):
        Currency.from_str("GBP")


def test_currency_rate_provider_valid():
    provider = SimpleCurrencyRateToPlnProvider()
    assert provider.get_currency_rate(Currency.EUR) == 4.0
    assert provider.get_currency_rate(Currency.USD) == 3.0
    assert provider.get_currency_rate(Currency.PLN) == 1.0


def test_currency_rate_provider_invalid():
    provider = SimpleCurrencyRateToPlnProvider()
    with pytest.raises(ValueError):
        provider.get_currency_rate("GBP")  # type: ignore


def test_get_sold_qty_of_product(db_session: Session, customer_id):
    product_id = uuid4()
    db_session.add_all(
        [
            Transaction(
                customer_id=customer_id,
                amount=10,
                quantity=2,
                currency="PLN",
                product_id=product_id,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=15,
                quantity=3,
                currency="PLN",
                product_id=product_id,
                timestamp=datetime.now(),
            ),
        ],
    )
    db_session.commit()

    result = get_sold_qty_of_product(db_session, product_id)
    assert result == 5


def test_get_sold_qty_of_product_none(db_session: Session):
    result = get_sold_qty_of_product(db_session, uuid4())
    assert result is None or result == 0


def test_get_total_income_for_product_in_pln(db_session: Session, customer_id):
    product_id = uuid4()
    db_session.add_all(
        [
            Transaction(
                customer_id=customer_id,
                amount=10,
                quantity=1,
                currency="USD",  # * 3.0
                product_id=product_id,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=20,
                quantity=1,
                currency="EUR",  # * 4.0
                product_id=product_id,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=30,
                quantity=1,
                currency="PLN",  # * 1.0
                product_id=product_id,
                timestamp=datetime.now(),
            ),
        ],
    )
    db_session.commit()

    result = get_total_income_for_product_in_pln(db_session, product_id)
    expected = (10 * 1 * 3.0) + (20 * 1 * 4.0) + (30 * 1 * 1.0)
    assert result == expected


def test_get_total_income_for_product_none(db_session: Session):
    result = get_total_income_for_product_in_pln(db_session, uuid4())
    assert result is None


def test_get_total_number_of_unique_customers_for_product(db_session: Session, customer_id, another_customer_id):
    product_id = uuid4()
    db_session.add_all(
        [
            Transaction(
                customer_id=customer_id,
                amount=10,
                quantity=1,
                currency="PLN",
                product_id=product_id,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=customer_id,
                amount=15,
                quantity=2,
                currency="PLN",
                product_id=product_id,
                timestamp=datetime.now(),
            ),
            Transaction(
                customer_id=another_customer_id,
                amount=25,
                quantity=1,
                currency="PLN",
                product_id=product_id,
                timestamp=datetime.now(),
            ),
        ],
    )
    db_session.commit()

    result = get_total_number_of_unique_customers_for_product(db_session, product_id)
    assert result == 2


def test_get_total_number_of_unique_customers_for_product_none(db_session: Session):
    result = get_total_number_of_unique_customers_for_product(db_session, uuid4())
    assert result is None or result == 0
