"""Test fixtures for repository tests.

This module provides fixtures for testing repositories with SQLite in-memory database.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session using SQLite in-memory.
    
    This fixture creates a fresh in-memory SQLite database for each test,
    ensuring test isolation and fast execution.
    
    Yields:
        Session: SQLAlchemy session for testing
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
        Base.metadata.drop_all(bind=engine)
