from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.transactions.models import Transaction as TransactionORMModel
from app.transactions.tasks import process_transactions_file_local
from app.transactions.uploads.transactions_file_processor import Transaction, TransactionRowError


@pytest.fixture
def sample_transactions():
    now = datetime.now(timezone.utc)
    return [
        Transaction(
            transaction_id=uuid4(),
            timestamp=now,
            amount=100.0 + i,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=i + 1,
        )
        for i in range(100)
    ]


@patch("app.transactions.tasks.TransactionsFileProcessor")
def test_process_transactions_file_local_inserts_transactions(mock_processor_class, sample_transactions, db_session):
    mock_processor = mock_processor_class.return_value
    mock_processor.process_file.return_value = sample_transactions

    with patch("app.transactions.tasks.get_session") as mocked_session:
        mocked_session.side_effect = lambda: iter([db_session])
        process_transactions_file_local(path="dummy.csv", delimiter=";")

    result = db_session.query(TransactionORMModel).all()
    assert len(result) == 100


@patch("app.transactions.tasks.TransactionsFileProcessor")
def test_processor_should_skip_duplicated_rows(mock_processor_class, db_session):
    mock_processor = mock_processor_class.return_value
    duplicated_transaction_id = uuid4()
    mock_processor.process_file.return_value = [
        Transaction(
            transaction_id=duplicated_transaction_id,
            timestamp=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=1,
        ),
        Transaction(
            transaction_id=duplicated_transaction_id,
            timestamp=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=1,
        ),
        Transaction(
            transaction_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=1,
        ),
    ]

    with patch("app.transactions.tasks.get_session") as mocked_session:
        mocked_session.side_effect = lambda: iter([db_session])
        process_transactions_file_local(path="dummy.csv", delimiter=";")

    result = db_session.query(TransactionORMModel).all()
    assert len(result) == 2


@patch("app.transactions.tasks.TransactionsFileProcessor")
def test_processor_should_skip_errors_rows(mock_processor_class, db_session):
    mock_processor = mock_processor_class.return_value
    duplicated_transaction_id = uuid4()
    mock_processor.process_file.return_value = [
        Transaction(
            transaction_id=duplicated_transaction_id,
            timestamp=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=1,
        ),
        TransactionRowError(
            row_line=1,
            error="Test Error",
        ),
        Transaction(
            transaction_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            amount=100.0,
            currency="USD",
            customer_id=uuid4(),
            product_id=uuid4(),
            quantity=1,
        ),
    ]

    with patch("app.transactions.tasks.get_session") as mocked_session:
        mocked_session.side_effect = lambda: iter([db_session])
        process_transactions_file_local(path="dummy.csv", delimiter=";")

    result = db_session.query(TransactionORMModel).all()
    assert len(result) == 2


@patch("app.transactions.tasks.TransactionsFileProcessor")
@patch("app.transactions.tasks.BATCH_SIZE", new=1)
def test_process_transactions_file_local_inserts_transactions(
    mock_processor_class,
    db_session,
    sample_transactions,
):
    mock_processor = mock_processor_class.return_value
    mock_processor.process_file.return_value = sample_transactions

    with (
        patch("app.transactions.tasks._insert_batch") as mock_batch,
        patch("app.transactions.tasks.get_session") as mock_get_session,
    ):
        mock_get_session.side_effect = lambda: iter([db_session])
        process_transactions_file_local(path="dummy.csv", delimiter=";")
        assert mock_batch.call_count == 100
