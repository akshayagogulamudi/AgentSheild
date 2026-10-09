"""Pytest configuration and fixtures."""
import sys
import os
import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database.models import Base
from main import app
from database import get_db


# Use in-memory database for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Enable foreign keys for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="session")
def db_session_factory(db_engine):
    """Create test database session factory."""
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture(scope="module", autouse=True)
def clear_app_overrides_after_module():
    """Clear app dependency overrides after each test module."""
    yield
    # After this module's tests, clear overrides so next module gets clean state
    if get_db in app.dependency_overrides:
        del app.dependency_overrides[get_db]
