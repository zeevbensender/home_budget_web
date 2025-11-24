# Home Budget Web — Backend (Variant A)

## Mode: JSON Storage
The backend currently runs in *JSON mode*.  
All expenses and incomes are read/written to simple `.json` files in `app/data/`.

This is a temporary implementation.  
The storage layer will be replaced with a real database in a future milestone.  
API contracts must stay stable so the switch is transparent to tests.

## Running the Backend
```
uvicorn app.main:app --reload --port 8000
```

## Running Backend Tests
```
pytest -q
```

Tests are API-only and do not depend on storage internals.

## Notes
- Do not rely on JSON file structure.
- Do not add DB/auth logic during Variant A.
- API responses must remain stable.
