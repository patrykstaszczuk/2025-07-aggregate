from datetime import datetime

from pydantic import BaseModel

from app.api.base_api_model import BaseAPIModel


class CustomerSummaryRead(BaseAPIModel):
    total_cost_pln: float | None
    unique_products_count: int | None
    last_transaction_timestamp: datetime | None


class ProductSummaryRead(BaseAPIModel):
    sold_qty: int | None = None
    total_income_pln: float | None = None
    total_number_of_customers: int | None = None
