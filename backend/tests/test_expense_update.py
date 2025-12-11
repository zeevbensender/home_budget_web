def test_update_expense_minimal(client):
    # --- Step 1: Create an expense to update ---
    create_payload = {
        "date": "2025-11-10",
        "category": "Groceries",
        "amount": 50.0,
        "account": "Cash",
    }
    create_resp = client.post("/api/v1/expense", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["expense"]
    exp_id = created["id"]

    # --- Step 2: Update the category ---
    update_payload = {
        "field": "category",
        "value": "Updated Category"
    }
    update_resp = client.patch(f"/api/v1/expense/{exp_id}", json=update_payload)
    assert update_resp.status_code == 200

    updated = update_resp.json()["expense"]

    # Assertions
    assert updated["id"] == exp_id
    assert updated["category"] == "Updated Category"
