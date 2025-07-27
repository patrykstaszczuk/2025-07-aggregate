from fastapi.testclient import TestClient

from app.main import app
from tests.factories import create_transaction
from tests.integration.api.common import override_deps

client = TestClient(app)


def test_read_transaction_by_id(db_session) -> None:
    transaction = create_transaction(db_session)
    override_deps(db_session)

    response = client.get(app.url_path_for("transaction-details", transaction_id=transaction.transaction_id))
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert isinstance(response_json, dict)
    assert response_json["transaction_id"] == str(transaction.transaction_id)


def test_read_paginated_transactions(db_session) -> None:
    override_deps(db_session)
    create_transaction(db_session)
    create_transaction(db_session)
    create_transaction(db_session)
    url = app.url_path_for("transaction-list") + "?page=1&per_page=1"
    response = client.get(url)
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert isinstance(response_json, dict)
    assert "items" in response_json
    assert "meta" in response_json
    assert response_json["meta"]["total_pages"] == 3


def test_read_filtered_transactions_by_customer_id(db_session) -> None:
    override_deps(db_session)
    transaction = create_transaction(db_session)
    create_transaction(db_session)
    create_transaction(db_session)

    response = client.get(app.url_path_for("transaction-list") + f"?customer_id={transaction.customer_id}")
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["customer_id"] == str(transaction.customer_id)


def test_read_filtered_transactions_by_product_id(db_session) -> None:
    override_deps(db_session)
    transaction = create_transaction(db_session)
    create_transaction(db_session)
    create_transaction(db_session)

    response = client.get(app.url_path_for("transaction-list") + f"?product_id={transaction.product_id}")
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert len(response_json["items"]) == 1
    assert response_json["items"][0]["product_id"] == str(transaction.product_id)
