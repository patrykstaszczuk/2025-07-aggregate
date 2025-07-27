from datetime import datetime
from typing import Iterable
from uuid import UUID

from pydantic import BaseModel, ValidationError

from app.transactions.config import CSV_FILE_HEADERS_TO_ROW_MAP

from .transactions_file_reader import FileReader


class Transaction(BaseModel):
    transaction_id: UUID
    timestamp: datetime
    amount: float
    currency: str
    customer_id: UUID
    product_id: UUID
    quantity: int


class TransactionRowError(BaseModel):
    row_line: int
    error: str


class TransactionsFileProcessor:
    def __init__(self, file_reader: FileReader) -> None:
        self._file_reader = file_reader

    def process_file(self) -> Iterable[Transaction | TransactionRowError]:
        for row_number, row in enumerate(self._file_reader.read_file(), start=1):
            try:
                # let the pydantic do the work
                yield Transaction(
                    transaction_id=row[CSV_FILE_HEADERS_TO_ROW_MAP["transaction_id"]],  # type: ignore[arg-type]
                    timestamp=row[CSV_FILE_HEADERS_TO_ROW_MAP["timestamp"]],  # type: ignore[arg-type]
                    amount=row[CSV_FILE_HEADERS_TO_ROW_MAP["amount"]],  # type: ignore[arg-type]
                    currency=row[CSV_FILE_HEADERS_TO_ROW_MAP["currency"]],  # type: ignore[arg-type]
                    customer_id=row[CSV_FILE_HEADERS_TO_ROW_MAP["customer_id"]],  # type: ignore[arg-type]
                    product_id=row[CSV_FILE_HEADERS_TO_ROW_MAP["product_id"]],  # type: ignore[arg-type]
                    quantity=row[CSV_FILE_HEADERS_TO_ROW_MAP["quantity"]],  # type: ignore[arg-type]
                )
            except IndexError:
                yield TransactionRowError(row_line=row_number, error="Invalid row structure, cannot parse data")
            except ValidationError as e:
                yield TransactionRowError(row_line=row_number, error=str(e))
