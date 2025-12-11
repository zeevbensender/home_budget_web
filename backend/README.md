# Home Budget Web — Backend

## Mode: PostgreSQL Database Storage
The backend uses **PostgreSQL** as its primary storage.
All expenses and incomes are stored in a PostgreSQL database.

This is the production-ready implementation following the completion of Phase 5
of the PostgreSQL migration. JSON storage has been removed.

## Running the Backend
```
uvicorn app.main:app --reload --port 8000
```

## Running Backend Tests
```
pytest -q
```

Tests are API-focused and use PostgreSQL (or SQLite for unit tests).

## Notes
- PostgreSQL is required for full API functionality.
- API contracts remain stable across storage implementations.
