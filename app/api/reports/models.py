from datetime import datetime

from pydantic import BaseModel


class CustomerSummaryRead(BaseModel):
    total_cost_pln: float | None
    unique_products_count: int | None
    last_transaction_timestamp: datetime | None
