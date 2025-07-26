from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.orm import aliased

from app.api.pagination import PaginatedInput, PaginatedResponse, Paginator
from app.api.transactions.models import TransactionRead
from app.transactions.models import Transaction
from tests.factories import create_transaction


@pytest.mark.parametrize(
    "page, per_page, expected_count",
    [
        (1, 5, 5),
        (2, 5, 5),
        (1, 10, 10),
        (3, 4, 2),
    ],
)
def test_pagination_for_different_parameters(db_session, page, per_page, expected_count) -> None:
    for _ in range(10):
        create_transaction(db_session)

    pagination_input = PaginatedInput(page=page, per_page=per_page)
    paginator = Paginator(
        select(Transaction),
        response_model_cls=TransactionRead,
        page=pagination_input.page,
        page_size=pagination_input.per_page,
    )
    res = paginator.paginate(db_session)
    assert isinstance(res, PaginatedResponse)
    assert len(res.items) == expected_count


def test_pagination_for_statement_with_join(db_session) -> None:
    create_transaction(db_session)
    create_transaction(db_session)
    create_transaction(db_session)

    pagination_input = PaginatedInput(page=1, per_page=10)
    transaction_alias = aliased(Transaction)
    statement = select(
        Transaction,
        transaction_alias.transaction_id.label("equal_with_amount"),
    ).join(transaction_alias, Transaction.amount == transaction_alias.amount)

    class TransactionReadOverwrite(TransactionRead):
        equal_with_amount: UUID

    paginator = Paginator(
        statement,
        scalar_fields=["equal_with_amount"],
        response_model_cls=TransactionReadOverwrite,
        page=pagination_input.page,
        page_size=pagination_input.per_page,
    )
    res = paginator.paginate(db_session)
    assert res.items[0].equal_with_amount is not None
    assert len(res.items) == 9  # number of pairs after join


def test_filtering_paginated_query(db_session) -> None:
    create_transaction(db_session, amount=10)
    create_transaction(db_session, amount=30)

    statement = select(Transaction).where(Transaction.amount == 10)
    pagination_input = PaginatedInput(page=1, per_page=10)
    paginator = Paginator(
        statement,
        response_model_cls=TransactionRead,
        page=pagination_input.page,
        page_size=pagination_input.per_page,
    )
    res = paginator.paginate(db_session)
    assert len(res.items) == 1
    assert res.items[0].amount == 10


def test_sorting_paginated_query(db_session) -> None:
    create_transaction(db_session, amount=10)
    create_transaction(db_session, amount=30)

    statement = select(Transaction).order_by(Transaction.amount.desc())
    pagination_input = PaginatedInput(page=1, per_page=1)
    paginator = Paginator(
        statement,
        response_model_cls=TransactionRead,
        page=pagination_input.page,
        page_size=pagination_input.per_page,
    )
    res = paginator.paginate(db_session)
    assert len(res.items) == 1
    assert res.items[0].amount == 30
