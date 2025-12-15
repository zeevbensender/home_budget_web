"""Test that PUT endpoints handle extra fields from frontend gracefully.

Note: The 'client' fixture is automatically available from conftest.py
and does not need to be imported explicitly per project conventions.
"""

def test_put_expense_with_extra_fields_from_frontend(client):
    """
    Test that PUT endpoint handles extra fields (id, type) that frontend sends.
    
    The frontend's TransactionModal sends id and type fields along with the
    update data. The PUT endpoint should handle these gracefully.
    """
    # Create an expense
    create_payload = {
        "date": "2025-12-14",
        "business": "Test Business",
        "category": "Test Category",
        "amount": 100.0,
        "account": "1234",
        "currency": "₪",
    }
    resp = client.post("/api/v1/expense", json=create_payload)
    assert resp.status_code == 200
    expense_id = resp.json()["expense"]["id"]
    
    # Update with extra fields (exactly like frontend does)
    update_payload = {
        "date": "2025-12-14",
        "business": "Test Business",
        "category": "Updated Category",
        "amount": 150.0,
        "account": "1234",
        "currency": "₪",
        "notes": "Updated",
        "id": expense_id,  # Extra field from frontend
        "type": "expense",  # Extra field from frontend
    }
    
    resp = client.put(f"/api/v1/expense/{expense_id}", json=update_payload)
    assert resp.status_code == 200, f"PUT failed with extra fields: {resp.text}"
    
    updated = resp.json()["expense"]
    assert updated["category"] == "Updated Category"
    assert updated["amount"] == 150.0
    assert updated["notes"] == "Updated"


def test_put_income_with_extra_fields_from_frontend(client):
    """Test that PUT income endpoint handles extra fields from frontend."""
    # Create an income
    create_payload = {
        "date": "2025-12-14",
        "category": "Salary",
        "amount": 5000.0,
        "account": "9999",
        "currency": "₪",
    }
    resp = client.post("/api/v1/income", json=create_payload)
    assert resp.status_code == 200
    income_id = resp.json()["income"]["id"]
    
    # Update with extra fields
    update_payload = {
        "date": "2025-12-14",
        "category": "Bonus",
        "amount": 6000.0,
        "account": "9999",
        "currency": "₪",
        "notes": "Year-end bonus",
        "id": income_id,  # Extra field from frontend
        "type": "income",  # Extra field from frontend
    }
    
    resp = client.put(f"/api/v1/income/{income_id}", json=update_payload)
    assert resp.status_code == 200, f"PUT failed with extra fields: {resp.text}"
    
    updated = resp.json()["income"]
    assert updated["category"] == "Bonus"
    assert updated["amount"] == 6000.0


def test_put_endpoint_methods_are_registered(client):
    """Verify that PUT methods are actually registered in the router."""
    # Make an OPTIONS request to check allowed methods
    resp = client.options("/api/v1/expense/1")
    
    # FastAPI should include PUT in allowed methods
    # Note: The Allow header might not be set for OPTIONS requests in FastAPI
    # So we'll just verify PUT works instead
    
    # Create a test expense
    create_resp = client.post("/api/v1/expense", json={
        "date": "2025-12-14",
        "business": "Test",
        "category": "Test",
        "amount": 50.0,
        "account": "1234",
    })
    assert create_resp.status_code == 200
    exp_id = create_resp.json()["expense"]["id"]
    
    # Verify PUT works (method is registered)
    put_resp = client.put(f"/api/v1/expense/{exp_id}", json={"amount": 75.0})
    assert put_resp.status_code == 200, "PUT method should be registered"
    
    # Verify PATCH also still works
    patch_resp = client.patch(f"/api/v1/expense/{exp_id}", json={"field": "amount", "value": 100.0})
    assert patch_resp.status_code == 200, "PATCH method should still work"
