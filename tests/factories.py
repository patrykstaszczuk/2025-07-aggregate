from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.transactions.models import Transaction


def create_transaction(db_session: Session, **kwargs) -> Transaction:
    params = {
        "transaction_id": uuid4(),
        "timestamp": datetime.now(timezone.utc),
        "amount": 199.99,
        "currency": "EUR",
        "customer_id": uuid4(),
        "product_id": uuid4(),
        "quantity": 5,
        **kwargs,
    }
    obj = Transaction(**params)
    db_session.add(obj)
    db_session.commit()
    return obj
