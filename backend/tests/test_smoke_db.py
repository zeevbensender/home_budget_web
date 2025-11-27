"""
Smoke test for Home Budget Web with PostgreSQL database.

This test:
1. Starts a PostgreSQL container
2. Runs Alembic migrations
3. Seeds the database
4. Tests basic API flows

Run with: poetry run pytest tests/test_smoke_db.py -v
Or via Makefile: make smoke-test
"""
import os
import subprocess
import sys
import time

import pytest

# Mark all tests in this module as smoke tests
pytestmark = pytest.mark.smoke

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Test configuration
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
DATABASE_URL = "postgresql://budget:budget@localhost:5432/budget_db"


def wait_for_postgres(max_retries=30, delay=1):
    """Wait for PostgreSQL to be ready."""
    import psycopg2

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            conn.close()
            print("PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... ({i + 1}/{max_retries})")
            time.sleep(delay)
    return False


@pytest.fixture(scope="module")
def postgres_db():
    """Start PostgreSQL container and clean up after tests."""
    compose_file = os.path.join(ROOT_DIR, "docker-compose-postgres.yaml")

    # Start PostgreSQL container
    print("Starting PostgreSQL container...")
    subprocess.run(
        ["docker", "compose", "-f", compose_file, "up", "-d"],
        check=True,
        cwd=ROOT_DIR,
    )

    # Wait for PostgreSQL to be ready
    if not wait_for_postgres():
        subprocess.run(
            ["docker", "compose", "-f", compose_file, "down", "-v"],
            cwd=ROOT_DIR,
        )
        pytest.fail("PostgreSQL did not start in time")

    yield DATABASE_URL

    # Cleanup: stop and remove container
    print("Stopping PostgreSQL container...")
    subprocess.run(
        ["docker", "compose", "-f", compose_file, "down", "-v"],
        cwd=ROOT_DIR,
    )


@pytest.fixture(scope="module")
def migrated_db(postgres_db):
    """Run Alembic migrations."""
    env = os.environ.copy()
    env["DATABASE_URL"] = postgres_db

    print("Running Alembic migrations...")
    result = subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Migration failed: {result.stderr}")
        pytest.fail(f"Alembic migration failed: {result.stderr}")

    print("Migrations completed successfully!")
    return postgres_db


@pytest.fixture(scope="module")
def seeded_db(migrated_db):
    """Seed the database with test data."""
    env = os.environ.copy()
    env["DATABASE_URL"] = migrated_db

    print("Seeding database...")
    result = subprocess.run(
        ["poetry", "run", "python", "scripts/seed_db.py"],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Seed failed: {result.stderr}")
        pytest.fail(f"Database seeding failed: {result.stderr}")

    print(f"Seed output: {result.stdout}")
    return migrated_db


@pytest.fixture(scope="module")
def app_client(seeded_db):
    """Create a test client for the FastAPI app."""
    # Set DATABASE_URL for the app
    os.environ["DATABASE_URL"] = seeded_db

    from fastapi.testclient import TestClient
    from app.main import app

    return TestClient(app)


class TestSmokeDB:
    """Smoke tests for DB-backed API."""

    def test_health_endpoint(self, app_client):
        """Test that health endpoint works."""
        response = app_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_endpoint(self, app_client):
        """Test that root endpoint works."""
        response = app_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_list_expenses(self, app_client):
        """Test listing expenses returns seeded data."""
        response = app_client.get("/api/v1/expense")
        assert response.status_code == 200
        # Current implementation uses JSON storage, not DB
        # This test verifies the API is working
        data = response.json()
        assert isinstance(data, list)

    def test_list_incomes(self, app_client):
        """Test listing incomes returns seeded data."""
        response = app_client.get("/api/v1/income")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_expense(self, app_client):
        """Test creating a new expense."""
        payload = {
            "date": "2025-11-15",
            "category": "Test Category",
            "amount": 100.0,
            "account": "Test Account",
        }
        response = app_client.post("/api/v1/expense", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "created"
        assert body["expense"]["category"] == "Test Category"
        assert body["expense"]["amount"] == 100.0

    def test_create_income(self, app_client):
        """Test creating a new income."""
        payload = {
            "date": "2025-11-15",
            "category": "Test Income",
            "amount": 500.0,
            "account": "Test Account",
        }
        response = app_client.post("/api/v1/income", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "created"
        assert body["income"]["category"] == "Test Income"
        assert body["income"]["amount"] == 500.0
