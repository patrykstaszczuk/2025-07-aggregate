from datetime import datetime
from uuid import UUID

from app.api.base_api_model import BaseAPIModel


class TransactionRead(BaseAPIModel):
    transaction_id: UUID
    timestamp: datetime
    amount: float
    currency: str
    customer_id: UUID
    product_id: UUID
    quantity: int


class TransactionsUploadRequestCreate(BaseAPIModel):
    import_id: UUID
