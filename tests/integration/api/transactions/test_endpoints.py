import uuid

from fastapi.testclient import TestClient

from app.core.session import get_session
from app.main import app
from tests.factories import create_transaction

client = TestClient(app)


def override_deps(db_session):
    app.dependency_overrides[get_session] = lambda: db_session


def test_read_transaction_by_id(db_session) -> None:
    transaction = create_transaction(db_session)
    override_deps(db_session)

    response = client.get(app.url_path_for("transaction-details", transaction_id=transaction.transaction_id))
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert isinstance(response_json, dict)
    assert response_json["transaction_id"] == str(transaction.transaction_id)
