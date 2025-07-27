from datetime import datetime

from pydantic import BaseModel


class CustomerSummaryRead(BaseModel):
    total_cost_pln: float | None
    unique_products_count: int | None
    last_transaction_timestamp: datetime | None


class ProductSummaryRead(BaseModel):
    sold_qty: int | None = None
    total_income_pln: float | None = None
    total_number_of_customers: int | None = None
