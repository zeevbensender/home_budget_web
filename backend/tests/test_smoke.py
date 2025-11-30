"""Smoke integration tests for validating migrations and key API flows.

These tests exercise the main API endpoints against a real Postgres database
to validate that migrations work correctly end-to-end.

Run with: pytest -m smoke -v
"""

import os

import pytest
from fastapi.testclient import TestClient

from app.main import app

# Mark all tests in this module as smoke tests
pytestmark = pytest.mark.smoke

client = TestClient(app)


class TestHealthSmoke:
    """Smoke tests for health endpoint."""

    def test_health_endpoint_responds(self):
        """Health endpoint should return 200 OK."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"


class TestExpenseSmoke:
    """Smoke tests for expense endpoints."""

    def test_list_expenses(self):
        """Should be able to list expenses."""
        response = client.get("/api/v1/expense")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_expense(self):
        """Should be able to create an expense."""
        payload = {
            "date": "2025-01-25",
            "business": "Smoke Test Business",
            "category": "Test Category",
            "amount": 99.99,
            "account": "Test Account",
            "currency": "₪",
            "notes": "Created by smoke test",
        }
        response = client.post("/api/v1/expense", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert "expense" in data
        assert data["expense"]["business"] == "Smoke Test Business"


class TestIncomeSmoke:
    """Smoke tests for income endpoints."""

    def test_list_incomes(self):
        """Should be able to list incomes."""
        response = client.get("/api/v1/income")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_create_income(self):
        """Should be able to create an income."""
        payload = {
            "date": "2025-01-25",
            "category": "Smoke Test Income",
            "amount": 1500.00,
            "account": "Test Bank",
            "currency": "₪",
            "notes": "Created by smoke test",
        }
        response = client.post("/api/v1/income", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "created"
        assert "income" in data
        assert data["income"]["category"] == "Smoke Test Income"


class TestRootSmoke:
    """Smoke tests for root endpoint."""

    def test_root_endpoint(self):
        """Root endpoint should respond with expected message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Home Budget" in data["message"]
