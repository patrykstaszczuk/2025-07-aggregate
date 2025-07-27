from logging import getLogger
from typing import Iterator

from celery import shared_task
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.session import get_session as get_session_global
from app.transactions.models import Transaction as TransactionORMModel
from app.transactions.uploads.transactions_file_processor import (
    Transaction,
    TransactionRowError,
    TransactionsFileProcessor,
)
from app.transactions.uploads.transactions_file_reader import StandardLocalTransactionsCSVFileReader

logger = getLogger(__name__)


def get_session() -> Iterator[Session]:
    yield from get_session_global()


BATCH_SIZE = 10000


@shared_task
def process_transactions_file_local(path: str, delimiter: str) -> None:
    processor = TransactionsFileProcessor(
        file_reader=StandardLocalTransactionsCSVFileReader(path, delimiter=delimiter),
    )
    session = next(get_session())

    batch = []

    for result in processor.process_file():
        if isinstance(result, TransactionRowError):
            logger.error(f"Error while processing row={result.row_line}: {result.error}")
            continue
        batch.append(result)
        if len(batch) >= BATCH_SIZE:
            _insert_batch(session, batch)
            batch.clear()
    if batch:
        _insert_batch(session, batch)
    session.commit()


def _insert_batch(session, transactions: list[Transaction]) -> None:
    stmt = (
        pg_insert(TransactionORMModel)
        .values(
            [t.model_dump() for t in transactions],
        )
        .on_conflict_do_nothing(index_elements=["transaction_id"])
    )

    session.execute(stmt)
