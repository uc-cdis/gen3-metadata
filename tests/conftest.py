from alembic.config import main as alembic_main
from cryptography.fernet import Fernet
import pytest
import os
from sqlalchemy.exc import SQLAlchemyError

from wts.api import app as service_app
from wts.api import _setup


def test_settings():
    settings = {
        "FENCE_BASE_URL": "localhost",
        "OIDC_CLIENT_ID": "test",
        "OIDC_CLIENT_SECRET": "test",
        "SECRET_KEY": "test",
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:postgres@localhost:5432/wts_test",
        "WTS_BASE_URL": "/",
        "ENCRYPTION_KEY": Fernet.generate_key().decode("utf-8"),
    }
    print(settings)
    for k, v in settings.items():
        os.environ[k] = v


@pytest.fixture(scope="session")
def app():
    test_settings()
    setup_test_database()
    with service_app.app_context():
        _setup(service_app)
    return service_app


def setup_test_database():
    """
    When running tests locally, we need to update the existing DB to
    the latest version.
    But in automated tests, a new DB is created from the latest models
    so there is no need to migrate (and alembic fails when trying).
    """
    try:
        alembic_main(["--raiseerr", "upgrade", "head"])
    except SQLAlchemyError as e:
        print("Skipping test DB migration: {}".format(e))
