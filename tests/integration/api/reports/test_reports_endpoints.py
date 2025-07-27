import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.transactions.currency_rate_provider import Currency, SimpleCurrencyRateToPlnProvider
from tests.factories import create_transaction
from tests.integration.api.common import override_deps

client = TestClient(app)


def test_get_customer_summary(db_session) -> None:
    override_deps(db_session)
    product_1_id = uuid.uuid4()
    customer_id = uuid.uuid4()
    transaction_1_in_eur = create_transaction(
        db_session,
        amount=100,
        currency="EUR",
        product_id=product_1_id,
        customer_id=customer_id,
        quantity=1,
    )
    transaction_2_in_usd = create_transaction(
        db_session,
        amount=100,
        currency="USD",
        product_id=product_1_id,
        customer_id=customer_id,
        quantity=2,
    )
    transaction_3_in_pln = create_transaction(
        db_session,
        amount=100,
        currency="PLN",
        customer_id=customer_id,
        quantity=1,
    )
    transaction_4_for_different_customer = create_transaction(
        db_session,
        amount=500,
        currency="PLN",
    )
    rate_for_eur = SimpleCurrencyRateToPlnProvider._RATES[Currency.EUR]
    rate_for_usd = SimpleCurrencyRateToPlnProvider._RATES[Currency.USD]

    response = client.get(app.url_path_for("customer-summary", customer_id=customer_id))
    response_json = response.json()
    assert response.status_code == 200
    assert (
        response_json["total_cost_pln"]
        == (
            (transaction_1_in_eur.amount * transaction_1_in_eur.quantity) * rate_for_eur
            + (transaction_2_in_usd.amount * transaction_2_in_usd.quantity) * rate_for_usd
            + (transaction_3_in_pln.amount * transaction_3_in_pln.quantity)
        )
        == 1100
    )
    assert response_json["unique_products_count"] == 2
    assert response_json["last_transaction_timestamp"] in [
        transaction_3_in_pln.timestamp.isoformat(),
        transaction_3_in_pln.timestamp.isoformat().replace("+00:00", "Z"),
    ]


def test_customer_summary_should_return_404_if_no_transaction_for_given_customer(db_session) -> None:
    override_deps(db_session)
    response = client.get(app.url_path_for("customer-summary", customer_id=uuid.uuid4()))
    assert response.status_code == 404


def test_customer_summary_should_raise_exception_if_transactions_are_in_unsupported_currency(db_session) -> None:
    override_deps(db_session)
    unsupported_currency = "xxx"
    customer_id = uuid.uuid4()
    create_transaction(db_session, currency=unsupported_currency, customer_id=customer_id)
    response = client.get(app.url_path_for("customer-summary", customer_id=customer_id))
    assert response.status_code == 400


def test_get_product_summary(db_session) -> None:
    override_deps(db_session)
    product_id = uuid.uuid4()
    transaction_1_eur = create_transaction(db_session, product_id=product_id, quantity=10, currency="EUR", amount=100)
    transaction_2_pln = create_transaction(db_session, product_id=product_id, quantity=20, currency="PLN", amount=400)
    transaction_3_different_product = create_transaction(db_session)

    response = client.get(app.url_path_for("product-summary", product_id=product_id))
    response_json = response.json()

    rate_for_eur = SimpleCurrencyRateToPlnProvider._RATES[Currency.EUR]
    assert response.status_code == 200

    assert response_json["sold_qty"] == 30
    assert response_json["total_income_pln"] == (
        transaction_2_pln.amount * transaction_2_pln.quantity
        + (transaction_1_eur.amount * transaction_1_eur.quantity) * rate_for_eur
    )
    assert response_json["total_number_of_customers"] == 2


def test_product_summary_should_return_404_if_no_transaction_for_given_product(db_session) -> None:
    override_deps(db_session)
    response = client.get(app.url_path_for("product-summary", product_id=uuid.uuid4()))
    assert response.status_code == 404
