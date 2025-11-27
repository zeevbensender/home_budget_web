"""
CI Smoke test for Home Budget Web with PostgreSQL database.

This test is designed to run in CI environments where:
1. PostgreSQL is already running as a service container
2. Migrations have been applied via `alembic upgrade head`
3. Database has been seeded via `python scripts/seed_db.py`

Run with: PYTHONPATH=$PYTHONPATH:$(pwd) poetry run pytest tests/test_smoke_ci.py -v

Note: For local development with docker-compose, use test_smoke_db.py instead.
"""
import pytest

# Mark all tests in this module as smoke tests
pytestmark = pytest.mark.smoke


class TestSmokeCI:
    """CI smoke tests for DB-backed API."""

    def test_health_endpoint(self, ci_app_client):
        """Test that health endpoint works."""
        response = ci_app_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_endpoint(self, ci_app_client):
        """Test that root endpoint works."""
        response = ci_app_client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_list_expenses(self, ci_app_client):
        """Test listing expenses returns data."""
        response = ci_app_client.get("/api/v1/expense")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_incomes(self, ci_app_client):
        """Test listing incomes returns data."""
        response = ci_app_client.get("/api/v1/income")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_expense(self, ci_app_client):
        """Test creating a new expense."""
        payload = {
            "date": "2025-11-15",
            "category": "CI Test Category",
            "amount": 100.0,
            "account": "CI Test Account",
        }
        response = ci_app_client.post("/api/v1/expense", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "created"
        assert body["expense"]["category"] == "CI Test Category"
        assert body["expense"]["amount"] == 100.0

    def test_create_income(self, ci_app_client):
        """Test creating a new income."""
        payload = {
            "date": "2025-11-15",
            "category": "CI Test Income",
            "amount": 500.0,
            "account": "CI Test Account",
        }
        response = ci_app_client.post("/api/v1/income", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "created"
        assert body["income"]["category"] == "CI Test Income"
        assert body["income"]["amount"] == 500.0
