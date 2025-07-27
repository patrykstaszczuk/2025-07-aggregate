import os
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.pagination import PaginatedInput, PaginatedResponse, Paginator
from app.core.media import get_media_dir
from app.core.session import get_session
from app.transactions.models import Transaction
from app.transactions.uploads import CSVHeaderInvalidException, LocalTransactionsCsvFileSaver

from .models import TransactionRead, TransactionsUploadRequestCreate

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("/{transaction_id}", name="transaction-details", response_model=TransactionRead)
async def get_transaction(transaction_id: UUID, session: Session = Depends(get_session)):
    statement = select(Transaction).where(Transaction.transaction_id == transaction_id)
    obj = session.execute(statement).scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return TransactionRead.model_validate(obj)


@router.get("/", name="transaction-list", response_model=PaginatedResponse[TransactionRead])
async def get_transaction_list(
    session: Session = Depends(get_session),
    pagination_input: PaginatedInput = Depends(),
    customer_id: UUID | None = None,
    product_id: UUID | None = None,
):
    statement = select(Transaction)
    if customer_id:
        statement = statement.where(Transaction.customer_id == customer_id)
    if product_id:
        statement = statement.where(Transaction.product_id == product_id)
    paginator = Paginator(
        statement,
        response_model_cls=TransactionRead,
        page=pagination_input.page,
        page_size=pagination_input.per_page,
    )
    return paginator.paginate(session)


@router.post("/upload", name="transactions-upload", response_model=TransactionsUploadRequestCreate, status_code=201)
def upload_transactions(
    file: UploadFile = File(),
    delimiter: str = Query(),
    session: Session = Depends(get_session),
    media_dir: str = Depends(get_media_dir),
):
    import_id = uuid.uuid4()
    try:
        LocalTransactionsCsvFileSaver(media_dir=media_dir, delimiter=delimiter).save(import_id=import_id, file=file)
    except CSVHeaderInvalidException as e:
        raise HTTPException(status_code=400, detail=str(e))
    return TransactionsUploadRequestCreate(import_id=import_id)
