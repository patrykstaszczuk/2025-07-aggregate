from celery import Celery

from app.core.settings import get_settings

settings = get_settings()

celery_app = Celery("transactions_aggregator")
celery_app.config_from_object(
    {
        "broker_url": settings.celery_broker_url,
        "task_default_queue": settings.celery_default_queue_name,
        "task_ignore_result": True,
        "task_serializer": "json",
        "accept_content": ["json"],
        "timezone": "Europe/Warsaw",
    },
)

celery_app.conf.broker_transport_options = {
    "visibility_timeout": 2 * 3600,
    "polling_interval": 5,
    "region": "eu-central-1",
}

tasks_to_autodiscover = [
    "app.transactions.tasks",
]

celery_app.autodiscover_tasks(tasks_to_autodiscover)

celery_app.conf.beat_schedule_filename = None
