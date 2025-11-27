"""Database session management utilities.

This module provides database connection and session management
using SQLAlchemy 2.0 with PostgreSQL.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.models import Base


def get_database_url() -> str:
    """Get database URL from environment variable.

    Returns:
        Database connection string from DATABASE_URL env var,
        or default local postgres URL.
    """
    return os.getenv(
        "DATABASE_URL", "postgresql://budget:budget@localhost:5432/budget_db"
    )


# Create engine lazily to allow testing with different databases
_engine = None
_session_factory = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(get_database_url(), echo=False)
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _session_factory


def get_session() -> Generator[Session, None, None]:
    """Get a database session.

    Yields:
        SQLAlchemy Session instance
    """
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def create_tables():
    """Create all database tables.

    This should be used for testing or initial setup.
    For production, use Alembic migrations.
    """
    Base.metadata.create_all(get_engine())


def drop_tables():
    """Drop all database tables.

    This should only be used for testing.
    """
    Base.metadata.drop_all(get_engine())


def reset_engine():
    """Reset the engine and session factory.

    This is useful for testing with different database configurations.
    """
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
