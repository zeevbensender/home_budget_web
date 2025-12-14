"""Test fixtures for integration tests.

This module provides fixtures for testing with SQLite in-memory database.
It overrides the database dependency to use SQLite instead of PostgreSQL.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session using SQLite in-memory.

    This fixture creates a fresh in-memory SQLite database for each test,
    ensuring test isolation and fast execution.

    Yields:
        Session: SQLAlchemy session for testing
    """
    # Create in-memory SQLite database with special settings for thread safety
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session factory
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create session
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database dependency override.

    This fixture creates a FastAPI TestClient that uses the test database
    instead of trying to connect to PostgreSQL.

    Args:
        db_session: Test database session fixture

    Yields:
        TestClient: FastAPI test client
    """
    # Override the get_db dependency to use the test database
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Session cleanup handled by db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    # Create test client
    with TestClient(app) as test_client:
        yield test_client

    # Clean up dependency override
    app.dependency_overrides.clear()
