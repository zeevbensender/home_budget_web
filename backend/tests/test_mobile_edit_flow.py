"""End-to-end test for mobile edit flow using PUT endpoint."""


def test_mobile_edit_expense_full_flow(client):
    """Test the complete mobile edit flow for an expense."""
    # Step 1: Create an expense (simulating existing data)
    create_payload = {
        "date": "2025-12-14",
        "business": "Keshet Tours",
        "category": "Eating Out",
        "amount": 75.50,
        "account": "8136",
        "currency": "₪",
        "notes": "Original note",
    }
    create_resp = client.post("/api/v1/expense", json=create_payload)
    assert create_resp.status_code == 200, f"Create failed: {create_resp.text}"
    created = create_resp.json()["expense"]
    expense_id = created["id"]
    
    # Step 2: Simulate mobile edit - user changes amount and notes
    # The frontend sends the full object with changes
    edit_payload = {
        "date": "2025-12-14",
        "business": "Keshet Tours",
        "category": "Eating Out",
        "amount": 85.00,  # Changed
        "account": "8136",
        "currency": "₪",
        "notes": "Updated from mobile",  # Changed
        "id": expense_id,  # Frontend includes this
        "type": "expense",  # Frontend includes this
    }
    
    # Step 3: Send PUT request (what the frontend does)
    update_resp = client.put(f"/api/v1/expense/{expense_id}", json=edit_payload)
    
    # Verify the response
    assert update_resp.status_code == 200, f"PUT failed: {update_resp.status_code} - {update_resp.text}"
    updated = update_resp.json()["expense"]
    
    # Verify the changes were saved
    assert updated["id"] == expense_id
    assert updated["amount"] == 85.00, "Amount should be updated"
    assert updated["notes"] == "Updated from mobile", "Notes should be updated"
    # Verify unchanged fields remain the same
    assert updated["date"] == "2025-12-14"
    assert updated["business"] == "Keshet Tours"
    assert updated["category"] == "Eating Out"
    assert updated["account"] == "8136"
    assert updated["currency"] == "₪"


def test_mobile_edit_income_full_flow(client):
    """Test the complete mobile edit flow for an income."""
    # Step 1: Create an income
    create_payload = {
        "date": "2025-12-14",
        "category": "Haifa Apartment",
        "amount": 5500.00,
        "account": "73077",
        "currency": "₪",
        "notes": "Original rent",
    }
    create_resp = client.post("/api/v1/income", json=create_payload)
    assert create_resp.status_code == 200, f"Create failed: {create_resp.text}"
    created = create_resp.json()["income"]
    income_id = created["id"]
    
    # Step 2: Simulate mobile edit
    edit_payload = {
        "date": "2025-12-14",
        "category": "Haifa Apartment",
        "amount": 5600.00,  # Changed
        "account": "73077",
        "currency": "₪",
        "notes": "Rent + utilities",  # Changed
        "id": income_id,
        "type": "income",
    }
    
    # Step 3: Send PUT request
    update_resp = client.put(f"/api/v1/income/{income_id}", json=edit_payload)
    
    # Verify the response
    assert update_resp.status_code == 200, f"PUT failed: {update_resp.status_code} - {update_resp.text}"
    updated = update_resp.json()["income"]
    
    # Verify the changes
    assert updated["id"] == income_id
    assert updated["amount"] == 5600.00
    assert updated["notes"] == "Rent + utilities"
    assert updated["category"] == "Haifa Apartment"
