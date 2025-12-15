"""Tests for PUT /api/v1/expense/{id} endpoint (full update)."""


def test_put_expense_full_update(client):
    """Test full expense update using PUT endpoint."""
    # Step 1: Create an expense
    create_payload = {
        "date": "2025-12-01",
        "business": "Old Business",
        "category": "Old Category",
        "amount": 100.0,
        "account": "1234",
        "currency": "₪",
        "notes": "Old notes",
    }
    create_resp = client.post("/api/v1/expense", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["expense"]
    exp_id = created["id"]

    # Step 2: Update all fields using PUT
    update_payload = {
        "date": "2025-12-09",
        "business": "Isradon",
        "category": "Entertainment",
        "amount": 378.0,
        "account": "0802",
        "currency": "₪",
        "notes": "Updated from mobile",
    }
    update_resp = client.put(f"/api/v1/expense/{exp_id}", json=update_payload)
    assert update_resp.status_code == 200

    updated = update_resp.json()["expense"]

    # Assertions - verify all fields were updated
    assert updated["id"] == exp_id
    assert updated["date"] == "2025-12-09"
    assert updated["business"] == "Isradon"
    assert updated["category"] == "Entertainment"
    assert updated["amount"] == 378.0
    assert updated["account"] == "0802"
    assert updated["currency"] == "₪"
    assert updated["notes"] == "Updated from mobile"


def test_put_expense_partial_update(client):
    """Test partial expense update using PUT endpoint (only some fields)."""
    # Step 1: Create an expense
    create_payload = {
        "date": "2025-12-01",
        "business": "Original Business",
        "category": "Original Category",
        "amount": 100.0,
        "account": "1234",
        "currency": "$",
        "notes": "Original notes",
    }
    create_resp = client.post("/api/v1/expense", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["expense"]
    exp_id = created["id"]

    # Step 2: Update only some fields using PUT
    update_payload = {
        "amount": 200.0,
        "notes": "Updated notes only",
    }
    update_resp = client.put(f"/api/v1/expense/{exp_id}", json=update_payload)
    assert update_resp.status_code == 200

    updated = update_resp.json()["expense"]

    # Assertions - verify updated fields changed, others remain
    assert updated["id"] == exp_id
    assert updated["amount"] == 200.0
    assert updated["notes"] == "Updated notes only"
    # These should remain unchanged
    assert updated["date"] == "2025-12-01"
    assert updated["business"] == "Original Business"
    assert updated["category"] == "Original Category"
    assert updated["account"] == "1234"
    assert updated["currency"] == "$"


def test_put_expense_not_found(client):
    """Test PUT on non-existent expense returns 404."""
    update_payload = {
        "amount": 999.0,
    }
    update_resp = client.put("/api/v1/expense/99999", json=update_payload)
    assert update_resp.status_code == 404
