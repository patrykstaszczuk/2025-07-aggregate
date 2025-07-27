from datetime import datetime
from uuid import UUID

from app.transactions.uploads.transactions_file_processor import (
    FileReader,
    Transaction,
    TransactionRowError,
    TransactionsFileProcessor,
)


class DummyFileReader(FileReader):
    def __init__(self, rows):
        self.rows = rows

    def read_file(self):
        for row in self.rows:
            yield row


def test_file_processor_parses_correctly():
    rows = [
        [
            "550e8400-e29b-41d4-a716-446655440000",
            "2025-07-27T15:30:00Z",
            "99.99",
            "PLN",
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
            "1",
        ],
        [
            "550e8400-e29b-41d4-a716-446655440001",
            "2025-07-27T16:00:00Z",
            "149.50",
            "EUR",
            "33333333-3333-3333-3333-333333333333",
            "44444444-4444-4444-4444-444444444444",
            "2",
        ],
    ]

    file_reader = DummyFileReader(rows)
    processor = TransactionsFileProcessor(file_reader)
    transactions = list(processor.process_file())

    assert len(transactions) == 2

    t1 = transactions[0]
    assert isinstance(t1, Transaction)
    assert t1.transaction_id == UUID("550e8400-e29b-41d4-a716-446655440000")
    assert t1.timestamp == datetime.fromisoformat("2025-07-27T15:30:00+00:00")
    assert t1.amount == 99.99
    assert t1.currency == "PLN"
    assert t1.customer_id == UUID("11111111-1111-1111-1111-111111111111")
    assert t1.product_id == UUID("22222222-2222-2222-2222-222222222222")
    assert t1.quantity == 1

    t2 = transactions[1]
    assert t2.currency == "EUR"
    assert t2.amount == 149.50


def test_file_processor_yields_errors_per_row():
    rows = [
        ["bad", "data"],
        [
            "550e8400-e29b-41d4-a716-446655440000",
            "2025-07-27T15:30:00Z",
            "99.99",
            "PLN",
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
            "1",
        ],
        [
            "111",  # invalid UUID
            "2025-07-27T15:30:00Z",
            "99.99",
            "PLN",
            "11111111-1111-1111-1111-111111111111",
            "22222222-2222-2222-2222-222222222222",
            "sadsa",  # invalid quantity
        ],
    ]
    file_reader = DummyFileReader(rows)
    processor = TransactionsFileProcessor(file_reader)
    transactions = list(processor.process_file())

    assert len(transactions) == 3
    assert isinstance(transactions[0], TransactionRowError)
    assert isinstance(transactions[1], Transaction)
    assert isinstance(transactions[2], TransactionRowError)
