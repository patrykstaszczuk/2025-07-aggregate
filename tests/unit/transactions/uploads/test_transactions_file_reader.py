from io import BytesIO
from pathlib import Path

import pytest

from app.transactions.uploads.transactions_file_reader import LocalTransactionsFileReader


@pytest.fixture
def fake_csv_file(tmp_path: Path) -> Path:
    fake_file_content = BytesIO(
        b"transaction_id,timestamp,amount,currency,customer_id,product_id,quantity\n"
        b"550e8400-e29b-41d4-a716-446655440000,2025-07-27T15:30:00Z,99.99,PLN,11111111-1111-1111-1111-111111111111,22222222-2222-2222-2222-222222222222,1\n"
        b"550e8400-e29b-41d4-a716-446655440001,2025-07-27T16:00:00Z,149.50,EUR,33333333-3333-3333-3333-333333333333,44444444-4444-4444-4444-444444444444,2\n",
    )
    file_path = tmp_path / "test_transactions.csv"
    file_path.write_bytes(fake_file_content.getvalue())
    return file_path


def test_read_file_yields_all_lines(fake_csv_file):
    reader = LocalTransactionsFileReader(str(fake_csv_file))
    lines = list(reader.read_file())

    assert len(lines) == 3
    assert lines[0].startswith("transaction_id")
    assert "99.99" in lines[1]
    assert "149.50" in lines[2]
