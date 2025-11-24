from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_add_expense_minimal():
    """Add a simple expense and verify response structure."""
    payload = {
        "date": "2025-11-10",
        "category": "Groceries",
        "amount": 50.0,
        "account": "Cash"
        # currency omitted → should auto-fill default
    }

    response = client.post("/api/expense", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "created"

    exp = body["expense"]

    # Required fields passed-through
    assert exp["date"] == "2025-11-10"
    assert exp["category"] == "Groceries"
    assert exp["amount"] == 50.0
    assert exp["account"] == "Cash"

    # Auto-filled currency (cannot rely on specific value)
    assert exp["currency"] is not None

    # ID must be integer, but exact value is not asserted
    assert isinstance(exp["id"], int)
