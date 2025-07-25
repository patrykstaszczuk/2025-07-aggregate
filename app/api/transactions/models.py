from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TransactionRead(BaseModel):
    transaction_id: UUID
    timestamp: datetime
    amount: float
    currency: str
    customer_id: UUID
    product_id: UUID
    quantity: int
