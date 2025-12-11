def test_delete_income_minimal(client):
    # --- Step 1: Create an income to delete ---
    create_payload = {
        "date": "2025-11-10",
        "category": "Salary",
        "amount": 5000.0,
        "account": "Bank",
    }

    create_resp = client.post("/api/v1/income", json=create_payload)
    assert create_resp.status_code == 200

    inc_id = create_resp.json()["income"]["id"]

    # --- Step 2: Delete the income ---
    delete_resp = client.delete(f"/api/v1/income/{inc_id}")
    assert delete_resp.status_code == 200

    body = delete_resp.json()
    assert body["status"] == "deleted"
    assert body["id"] == inc_id
