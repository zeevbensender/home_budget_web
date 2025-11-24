from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_add_income_minimal():
    """Add a simple income and verify response structure."""
    payload = {
        "date": "2025-11-10",
        "category": "Salary",     # REQUIRED and correct field name
        "amount": 5000.0,
        "account": "Bank"
        # currency omitted → should auto-fill
    }

    response = client.post("/api/v1/income", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "created"

    inc = body["income"]

    # Check returned structure
    assert inc["date"] == "2025-11-10"
    assert inc["category"] == "Salary"
    assert inc["amount"] == 5000.0
    assert inc["account"] == "Bank"

    # Currency auto-fill must happen
    assert inc["currency"] is not None

    # ID must be integer
    assert isinstance(inc["id"], int)
