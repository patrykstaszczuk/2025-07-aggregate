import os
from io import BytesIO

from fastapi.testclient import TestClient

from app.core.media import get_media_dir
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


def test_transactions_upload_should_save_file_to_future_processing_and_return_201(
    db_session,
    monkeypatch,
    tmp_path,
) -> None:
    override_deps(db_session)
    app.dependency_overrides[get_media_dir] = lambda: str(tmp_path / "media")

    fake_file = BytesIO(
        b"transaction_id,timestamp,amount,currency,customer_id,product_id,quantity\n"
        b"550e8400-e29b-41d4-a716-446655440000,2025-07-27T15:30:00Z,99.99,PLN,11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,1\n"
        b"550e8400-e29b-41d4-a716-446655440001,2025-07-27T16:00:00Z,149.50,EUR,33333333-3333-3333-3333-333333333333,44444444-4444-4444-4444-444444444444,2\n",
    )

    fake_file.name = "test.csv"

    response = client.post(
        app.url_path_for("transactions-upload") + "?delimiter=;",
        files={"file": ("test.csv", fake_file, "text/csv")},
    )
    response_json = response.json()

    assert response.status_code == 201
    assert "import_id" in response_json

    saved_file_path = tmp_path / "media" / "transactions" / f"{response_json['import_id']}.csv"
    assert saved_file_path.exists()
