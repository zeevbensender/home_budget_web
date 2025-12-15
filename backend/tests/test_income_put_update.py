"""Tests for PUT /api/v1/income/{id} endpoint (full update)."""


def test_put_income_full_update(client):
    """Test full income update using PUT endpoint."""
    # Step 1: Create an income
    create_payload = {
        "date": "2025-12-01",
        "category": "Old Category",
        "amount": 1000.0,
        "account": "1234",
        "currency": "₪",
        "notes": "Old notes",
    }
    create_resp = client.post("/api/v1/income", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["income"]
    income_id = created["id"]

    # Step 2: Update all fields using PUT
    update_payload = {
        "date": "2025-12-15",
        "category": "Salary",
        "amount": 5000.0,
        "account": "5678",
        "currency": "$",
        "notes": "December salary",
    }
    update_resp = client.put(f"/api/v1/income/{income_id}", json=update_payload)
    assert update_resp.status_code == 200

    updated = update_resp.json()["income"]

    # Assertions - verify all fields were updated
    assert updated["id"] == income_id
    assert updated["date"] == "2025-12-15"
    assert updated["category"] == "Salary"
    assert updated["amount"] == 5000.0
    assert updated["account"] == "5678"
    assert updated["currency"] == "$"
    assert updated["notes"] == "December salary"


def test_put_income_partial_update(client):
    """Test partial income update using PUT endpoint (only some fields)."""
    # Step 1: Create an income
    create_payload = {
        "date": "2025-12-01",
        "category": "Original Category",
        "amount": 1000.0,
        "account": "1234",
        "currency": "₪",
        "notes": "Original notes",
    }
    create_resp = client.post("/api/v1/income", json=create_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()["income"]
    income_id = created["id"]

    # Step 2: Update only some fields using PUT
    update_payload = {
        "amount": 2000.0,
        "category": "Bonus",
    }
    update_resp = client.put(f"/api/v1/income/{income_id}", json=update_payload)
    assert update_resp.status_code == 200

    updated = update_resp.json()["income"]

    # Assertions - verify updated fields changed, others remain
    assert updated["id"] == income_id
    assert updated["amount"] == 2000.0
    assert updated["category"] == "Bonus"
    # These should remain unchanged
    assert updated["date"] == "2025-12-01"
    assert updated["account"] == "1234"
    assert updated["currency"] == "₪"
    assert updated["notes"] == "Original notes"


def test_put_income_not_found(client):
    """Test PUT on non-existent income returns 404."""
    update_payload = {
        "amount": 999.0,
    }
    update_resp = client.put("/api/v1/income/99999", json=update_payload)
    assert update_resp.status_code == 404
