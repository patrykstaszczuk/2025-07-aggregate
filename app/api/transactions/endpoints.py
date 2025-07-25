from datetime import datetime
from uuid import UUID

from fastapi import APIRouter

from .models import TransactionRead

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/{transaction_id}", name="transaction-details", response_model=TransactionRead)
async def get_transaction(transaction_id: UUID):
    return {
        "transaction_id": transaction_id,
        "timestamp": datetime.fromisoformat("2025-07-25T14:30:00+00:00"),
        "amount": 123.45,
        "currency": "PLN",
        "customer_id": UUID("987e6543-e21b-34d3-a456-426614170000"),
        "product_id": UUID("456e7890-e11b-56d3-a456-426614178888"),
        "quantity": 3,
    }
