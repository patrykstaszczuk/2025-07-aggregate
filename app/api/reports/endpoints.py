from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.session import get_session

from .models import CustomerSummaryRead

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/customer-summary/{customer_id}),", name="customer-summary", response_model=CustomerSummaryRead)
def get_customer_summary(
    session: Session = Depends(get_session),
    customer_id: UUID | None = None,
):
    return CustomerSummaryRead()
