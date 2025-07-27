from app.core.session import get_session
from app.main import app


def override_deps(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
