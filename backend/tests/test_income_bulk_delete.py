from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bulk_delete_income_minimal():
    # --- Step 1: Create incomes to delete ---
    created_ids = []
    for i in range(3):
        payload = {
            "date": "2025-11-10",
            "category": f"Test {i}",
            "amount": 1000.0 + i,
            "account": "Bank",
        }
        resp = client.post("/api/income", json=payload)
        assert resp.status_code == 200
        created_ids.append(resp.json()["income"]["id"])

    # --- Step 2: Bulk delete them ---
    delete_payload = {"ids": created_ids}
    delete_resp = client.post("/api/income/bulk-delete", json=delete_payload)
    assert delete_resp.status_code == 200

    body = delete_resp.json()
    assert body["status"] == "deleted"
    assert body["count"] == len(created_ids)
