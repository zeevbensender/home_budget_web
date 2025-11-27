"""
Database session management for SQLAlchemy.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_database_url() -> str:
    """Get database URL from environment variable."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable is not set")
    return url


def create_session_factory(database_url: str | None = None) -> sessionmaker:
    """Create a session factory for the given database URL."""
    if database_url is None:
        database_url = get_database_url()
    engine = create_engine(database_url)
    return sessionmaker(bind=engine)


def get_session(database_url: str | None = None) -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Usage: with next(get_session()) as session: ...
    """
    SessionLocal = create_session_factory(database_url)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
