import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from app.core.session import Base


@pytest.fixture(scope="session")
def db_engine():
    with PostgresContainer("postgres:15") as container:
        container.start()
        engine = create_engine(container.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": "memory://",
        "result_backend": None,
        "task_always_eager": True,
        "task_eager_propagates": True,
    }
