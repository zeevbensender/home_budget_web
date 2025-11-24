from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_delete_expense_minimal():
    # --- Step 1: Create an expense to delete ---
    create_payload = {
        "date": "2025-11-10",
        "category": "Groceries",
        "amount": 50.0,
        "account": "Cash",
    }
    create_resp = client.post("/api/v1/expense", json=create_payload)
    assert create_resp.status_code == 200

    exp_id = create_resp.json()["expense"]["id"]

    # --- Step 2: Delete the expense ---
    delete_resp = client.delete(f"/api/v1/expense/{exp_id}")
    assert delete_resp.status_code == 200

    body = delete_resp.json()
    assert body["status"] == "deleted"
    assert body["id"] == exp_id
