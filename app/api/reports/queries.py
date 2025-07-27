from datetime import datetime
from uuid import UUID

from sqlalchemy import case, distinct, func, select
from sqlalchemy.orm import Session

from app.transactions.currency_rate_provider import Currency, SimpleCurrencyRateToPlnProvider
from app.transactions.models import Transaction


def get_unique_products_count_for_customer(session: Session, customer_id: UUID) -> int | None:
    return session.execute(
        select(func.count(distinct(Transaction.product_id))).where(Transaction.customer_id == customer_id),
    ).scalar()


def get_last_transaction_timestamp_for_customer(session: Session, customer_id: UUID) -> datetime | None:
    return session.execute(
        select(Transaction.timestamp)
        .where(Transaction.customer_id == customer_id)
        .order_by(Transaction.timestamp.desc())
        .limit(1),
    ).scalar()


def get_total_cost_pln_for_customer(session: Session, customer_id: UUID) -> float | None:
    transaction_count = session.execute(
        select(func.count(Transaction.transaction_id)).where(Transaction.customer_id == customer_id),
    ).scalar()
    if not transaction_count:
        return None
    curr_converter = SimpleCurrencyRateToPlnProvider()
    currencies_in_transactions = session.execute(
        select(distinct(Transaction.currency)).where(Transaction.customer_id == customer_id),
    ).all()
    currency_conversion = []
    for row in currencies_in_transactions:
        currency = Currency.from_str(row[0])
        rate = curr_converter.get_currency_rate(currency)
        currency_conversion.append(
            (Transaction.currency == currency.value, rate),
        )
    currency_conversion = case(*currency_conversion)  # type: ignore
    return session.execute(
        select(
            func.sum(Transaction.amount * Transaction.quantity * currency_conversion),
        ).where(Transaction.customer_id == customer_id),
    ).scalar()


def get_sold_qty_of_product(session: Session, product_id: UUID) -> int | None:
    return session.execute(
        select(func.sum(Transaction.quantity)).where(Transaction.product_id == product_id),
    ).scalar()


def get_total_income_for_product_in_pln(session: Session, product_id: UUID) -> float | None:
    transaction_count = session.execute(
        select(func.count(Transaction.transaction_id)).where(Transaction.product_id == product_id),
    ).scalar()
    if not transaction_count:
        return None
    curr_converter = SimpleCurrencyRateToPlnProvider()
    currencies_in_transactions_for_product = session.execute(
        select(distinct(Transaction.currency)).where(Transaction.product_id == product_id),
    ).all()
    currency_conversion = []
    for row in currencies_in_transactions_for_product:
        currency = Currency.from_str(row[0])
        rate = curr_converter.get_currency_rate(currency)
        currency_conversion.append(
            (Transaction.currency == currency.value, rate),
        )
    currency_conversion = case(*currency_conversion)  # type: ignore

    return session.execute(
        select(
            func.sum(Transaction.amount * Transaction.quantity * currency_conversion),
        ).where(Transaction.product_id == product_id),
    ).scalar()


def get_total_number_of_unique_customers_for_product(session: Session, product_id: UUID) -> int | None:
    return session.execute(
        select(func.count(distinct(Transaction.customer_id))).where(Transaction.product_id == product_id),
    ).scalar()
