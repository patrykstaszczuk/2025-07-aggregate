import uuid

from fastapi.testclient import TestClient

from app.core.session import get_session
from app.main import app

client = TestClient(app)


def override_deps(db_session):
    app.dependency_overrides[get_session] = lambda: db_session


def test_read_transaction_by_id(db_session) -> None:
    override_deps(db_session)

    response = client.get(app.url_path_for("transaction-details", transaction_id=uuid.uuid4()))
    response_status_code = response.status_code
    response_json = response.json()
    assert response_status_code == 200
    assert isinstance(response_json, dict)
    assert response_json.get("transaction_id")
