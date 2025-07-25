from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base

from app.core.settings import get_settings

engine = create_engine(url=get_settings().database_url, pool_pre_ping=True)
Base = declarative_base()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
