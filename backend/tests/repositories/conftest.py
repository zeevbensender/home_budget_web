"""Test configuration and fixtures for repository tests."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base


@pytest.fixture(scope="function")
def db_session():
    """
    Create an in-memory SQLite database session for testing.

    This fixture creates a fresh database for each test function,
    ensuring test isolation.

    Yields:
        SQLAlchemy Session instance connected to in-memory SQLite database
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:", echo=False)

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
        # Clean up
        Base.metadata.drop_all(bind=engine)
