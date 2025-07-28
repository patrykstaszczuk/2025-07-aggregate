from app.api.authentication import ensure_authenticated
from app.core.session import get_session
from app.main import app


def override_deps(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    app.dependency_overrides[ensure_authenticated] = lambda: None
