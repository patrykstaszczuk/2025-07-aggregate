from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session

from app.core.session import get_session
from app.transactions.models import Transaction

from .models import CustomerSummaryRead

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/customer-summary/{customer_id})", name="customer-summary", response_model=CustomerSummaryRead)
def get_customer_summary(
    session: Session = Depends(get_session),
    customer_id: UUID | None = None,
):

    currency_conversion = case(
        (Transaction.currency == "EUR", 4),
        (Transaction.currency == "USD", 3),
        (Transaction.currency == "PLN", 1.0),
        else_=1.0,
    )

    total_cost_pln = session.execute(
        select(
            func.sum(Transaction.amount * Transaction.quantity * currency_conversion),
        ).where(Transaction.customer_id == customer_id),
    ).scalar()

    unique_products_count = session.execute(
        select(func.count(distinct(Transaction.product_id))).where(Transaction.customer_id == customer_id),
    ).scalar()

    last_transaction_timestamp = session.execute(
        select(Transaction.timestamp)
        .where(Transaction.customer_id == customer_id)
        .order_by(Transaction.timestamp.desc())
        .limit(1),
    ).scalar()

    return CustomerSummaryRead(
        total_cost_pln=total_cost_pln,
        unique_products_count=unique_products_count,
        last_transaction_timestamp=last_transaction_timestamp,
    )
