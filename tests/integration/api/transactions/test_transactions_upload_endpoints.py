from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.media import get_media_dir
from app.main import app
from app.transactions.models import Transaction
from tests.integration.api.common import override_deps

client = TestClient(app)


@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
@patch("app.transactions.tasks.get_session")
def test_transactions_upload_should_save_file_to_future_processing_return_201_and_invoke_celery_task(
    get_session_mock,
    db_session,
    tmp_path,
) -> None:
    override_deps(db_session)
    app.dependency_overrides[get_media_dir] = lambda: str(tmp_path / "media")
    get_session_mock.side_effect = lambda: iter([db_session])

    fake_file = BytesIO(
        b"transaction_id,timestamp,amount,currency,customer_id,product_id,quantity\n"
        b"550e8400-e29b-41d4-a716-446655440000,2025-07-27T15:30:00Z,99.99,PLN,11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,1\n"
        b"550e8400-e29b-41d4-a716-446655440001,2025-07-27T16:00:00Z,149.50,EUR,33333333-3333-3333-3333-333333333333,44444444-4444-4444-4444-444444444444,2\n",
    )

    fake_file.name = "test.csv"

    response = client.post(
        app.url_path_for("transactions-upload") + "?delimiter=,",
        files={"file": ("test.csv", fake_file, "text/csv")},
    )
    response_json = response.json()
    saved_file_path = tmp_path / "media" / "transactions" / f"{response_json['import_id']}.csv"

    assert response.status_code == 201
    assert "import_id" in response_json
    assert saved_file_path.exists()
    assert len(db_session.execute(select(Transaction)).all()) == 2


def test_should_return_400_if_file_has_invalid_header(db_session, tmp_path) -> None:
    override_deps(db_session)
    app.dependency_overrides[get_media_dir] = lambda: str(tmp_path / "media")

    fake_file = BytesIO(
        b"invalid,timestamp,amount,currency,xyz,product_id,quantity\n"
        b"550e8400-e29b-41d4-a716-446655440000,2025-07-27T15:30:00Z,99.99,PLN,11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,1\n",
    )

    fake_file.name = "test.csv"

    response = client.post(
        app.url_path_for("transactions-upload") + "?delimiter=,",
        files={"file": ("test.csv", fake_file, "text/csv")},
    )

    assert response.status_code == 400
