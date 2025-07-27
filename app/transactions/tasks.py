from celery import shared_task

from app.transactions.uploads.transactions_file_processor import TransactionsFileProcessor
from app.transactions.uploads.transactions_file_reader import StandardLocalTransactionsCSVFileReader


@shared_task
def process_transactions_file_local(path: str, delimiter: str) -> None:
    processor = TransactionsFileProcessor(
        file_reader=StandardLocalTransactionsCSVFileReader(path, delimiter=delimiter),
    )
    processor.process_file()
