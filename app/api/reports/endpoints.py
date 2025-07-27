from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.transactions.currency_rate_provider import UnsupportedCurrency

from ...transactions.models import Transaction
from .models import CustomerSummaryRead, ProductSummaryRead
from .queries import (
    get_last_transaction_timestamp_for_customer,
    get_total_cost_pln_for_customer,
    get_unique_products_count_for_customer,
)

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/customer-summary/{customer_id})", name="customer-summary", response_model=CustomerSummaryRead)
def get_customer_summary(
    customer_id: UUID = Path(),
    session: Session = Depends(get_session),
):
    transaction_count = session.execute(
        select(func.count(Transaction.transaction_id)).where(Transaction.customer_id == customer_id),
    ).scalar()
    if not transaction_count:
        raise HTTPException(status_code=404, detail=f"No transactions for customer={customer_id}")
    try:
        total_cost_pln = get_total_cost_pln_for_customer(session, customer_id=customer_id)
    except UnsupportedCurrency as e:
        raise HTTPException(status_code=400, detail=f"Cannot prepare summary due to: {str(e)}")

    return CustomerSummaryRead(
        total_cost_pln=total_cost_pln,
        unique_products_count=get_unique_products_count_for_customer(session, customer_id=customer_id),
        last_transaction_timestamp=get_last_transaction_timestamp_for_customer(session, customer_id=customer_id),
    )


@router.get("/products-summary/{product_id}", name="product-summary", response_model=ProductSummaryRead)
def get_product_summary(
    product_id: UUID = Path(),
    session: Session = Depends(get_session),
):
    return ProductSummaryRead()
