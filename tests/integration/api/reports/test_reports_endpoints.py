import uuid

from fastapi.testclient import TestClient

from app.main import app
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
        amount="100",
        currency="PLN",
        customer_id=customer_id,
        quantity=1,
    )

    response = client.get(app.url_path_for("customer-summary", customer_id=customer_id))
    response_json = response.json()
