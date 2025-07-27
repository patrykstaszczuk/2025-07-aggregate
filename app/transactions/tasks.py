from celery import shared_task


@shared_task
def process_transactions_file_local(path: str) -> None:
    pass
