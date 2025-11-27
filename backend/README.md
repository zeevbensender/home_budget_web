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

## Database Setup (PostgreSQL)

### Starting Postgres Locally
Start the Postgres container using docker-compose:
```bash
docker compose -f docker-compose-postgres.yaml up -d
```

### Running Migrations
Run database migrations with Alembic:
```bash
cd backend
DATABASE_URL=postgresql://budget:budget@localhost:5432/budget_db python -m alembic upgrade head
```

### Seeding the Database
Load JSON fixtures into Postgres:
```bash
cd backend
DATABASE_URL=postgresql://budget:budget@localhost:5432/budget_db python -m scripts.seed
```

The seed script will:
1. Create tables if they don't exist
2. Load expenses and incomes from `app/data/*.json`
3. Verify that row counts match the fixture counts

## Notes
- Do not rely on JSON file structure.
- Do not add DB/auth logic during Variant A.
- API responses must remain stable.
