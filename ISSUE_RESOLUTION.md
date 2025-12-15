# Issue Resolution: Save Updated Entity Fails (405 Method Not Allowed)

## Problem Description

When users tried to edit transactions in mobile mode, they encountered a **405 Method Not Allowed** error. The deployed backend was rejecting PUT requests with the message that only PATCH is allowed.

### Error Details
- **Error**: HTTP 405 Method Not Allowed
- **Endpoint**: PUT `/api/v1/expense/{id}` and PUT `/api/v1/income/{id}`
- **Response Header**: `Allow: PATCH` (indicating PUT method not available)
- **Impact**: Mobile users unable to save edits to expenses or incomes

## Root Cause

The deployed backend (hbw-backend.onrender.com) was running outdated code that only had PATCH endpoints for updates. The frontend code had been updated to use PUT for full object updates (required for mobile modal edits), but the backend hadn't been redeployed yet.

## Solution

PUT endpoints were added to the backend in commit `ed6469b8` (December 15, 2025 at 11:23 UTC) and are present in the main branch:

### Backend Changes (Already Implemented)
- **File**: `backend/app/routers/expense_router.py` (lines 65-91)
  - Added `@router.put("/expense/{expense_id}")` endpoint
  - Handles full object updates using `ExpenseFullUpdate` schema
  
- **File**: `backend/app/routers/income_router.py` (lines 63-89)
  - Added `@router.put("/income/{income_id}")` endpoint
  - Handles full object updates using `IncomeFullUpdate` schema

### Frontend (Already Using PUT)
- **File**: `frontend/src/api.js`
  - `updateExpense(id, data)` uses PUT method
  - `updateIncome(id, data)` uses PUT method

## Verification

### Tests Added
1. **test_mobile_edit_flow.py**: End-to-end tests for mobile edit flow
2. **test_put_endpoint_extra_fields.py**: Tests that PUT handles extra fields from frontend

### All Tests Passing
```
✅ test_put_expense_full_update
✅ test_put_expense_partial_update
✅ test_put_expense_not_found
✅ test_put_income_full_update
✅ test_put_income_partial_update
✅ test_put_income_not_found
✅ test_mobile_edit_expense_full_flow
✅ test_mobile_edit_income_full_flow
✅ test_put_expense_with_extra_fields_from_frontend
✅ test_put_income_with_extra_fields_from_frontend
✅ test_put_endpoint_methods_are_registered
```

### Routes Verified
The FastAPI application correctly registers both PATCH and PUT methods:
```
/api/v1/expense/{expense_id}    PATCH, PUT, DELETE
/api/v1/income/{income_id}      PATCH, PUT, DELETE
```

## Deployment Status

**Code Status**: ✅ Fixed in repository (main branch)
**Deployed Status**: ⚠️ Needs redeployment

The fix is complete in the codebase. The next deployment to production will resolve the issue for all users.

## Technical Details

### PUT Endpoint Implementation
The PUT endpoints accept partial updates (only changed fields need to be sent):

**Request**: PUT `/api/v1/expense/12`
```json
{
  "amount": 85.00,
  "notes": "Updated from mobile",
  "id": 12,
  "type": "expense"
}
```

**Response**: 200 OK
```json
{
  "status": "updated",
  "expense": {
    "id": 12,
    "date": "2025-12-14",
    "business": "Keshet Tours",
    "category": "Eating Out",
    "amount": 85.00,
    "account": "8136",
    "currency": "₪",
    "notes": "Updated from mobile"
  }
}
```

### Extra Fields Handling
The PUT endpoints gracefully handle extra fields (`id`, `type`) that the frontend includes. Pydantic's `model_dump(exclude_unset=True)` filters to only the defined schema fields.

## Next Steps

1. **Automatic Deployment**: The backend has `autoDeploy: true` configured in `render.yaml` and should automatically deploy when changes are pushed to the main branch.

2. **Manual Deployment** (if needed): If automatic deployment hasn't occurred, manually trigger a deployment through Render's dashboard or via the GitHub Actions workflow.

3. **Verification After Deployment**: Test the mobile edit functionality on production after redeployment to confirm the fix is live.

## Prevention

- The comprehensive test suite (117 tests total) now includes end-to-end mobile edit flow tests
- Tests verify both PATCH and PUT methods work correctly
- Tests cover the exact payload format sent by the frontend (including extra fields)

## References

- Commit adding PUT endpoints: `ed6469b8`
- Related PR: #90 "Fix mobile transaction modal double API call bug and add PUT endpoints"
- Tests: `backend/tests/test_put_endpoint_extra_fields.py`, `backend/tests/test_mobile_edit_flow.py`
