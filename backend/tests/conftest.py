"""
Pytest configuration for Home Budget Web backend tests.

Provides fixtures for both CI (with pre-configured PostgreSQL service)
and local development (using docker-compose).
"""
import os
import pytest


@pytest.fixture(scope="module")
def ci_app_client():
    """
    Create a test client for CI environments where PostgreSQL is
    already running as a service container and migrations/seeding
    have been completed.

    This fixture is used by the CI smoke test job.
    """
    # DATABASE_URL should be set by CI environment
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set - skipping CI smoke test")

    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)
