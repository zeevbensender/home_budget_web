# Smoke Integration Tests

This document describes how to run the Postgres-based smoke integration tests that validate database migrations and key API flows.

## Overview

The smoke integration tests:
1. Spin up a Postgres database
2. Run Alembic migrations (`alembic upgrade head`)
3. Seed minimal test data
4. Run smoke tests that exercise key API endpoints

## Running Locally

### Prerequisites

- Docker installed and running
- Poetry installed (`pip install poetry`)
- Python 3.11+

### Option 1: Using docker-compose (Recommended)

1. Start the Postgres container:
   ```bash
   docker-compose -f docker-compose-postgres.yaml up -d
   ```

2. Wait for Postgres to be ready:
   ```bash
   docker-compose -f docker-compose-postgres.yaml exec db pg_isready -U poc_user -d poc_db
   ```

3. Set the DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL="postgresql://poc_user:poc_password@localhost:5432/poc_db"
   ```

4. Navigate to backend directory:
   ```bash
   cd backend
   ```

5. Install dependencies:
   ```bash
   poetry install
   ```

6. Run Alembic migrations:
   ```bash
   poetry run alembic upgrade head
   ```

7. Seed test data (optional):
   ```bash
   poetry run python scripts/seed_test_data.py
   ```

8. Run smoke tests:
   ```bash
   poetry run pytest -m smoke -v
   ```

9. Cleanup (when done):
   ```bash
   docker-compose -f docker-compose-postgres.yaml down -v
   ```

### Option 2: Using your own Postgres instance

1. Create a test database and user
2. Set the DATABASE_URL environment variable:
   ```bash
   export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
   ```
3. Follow steps 4-8 from Option 1

## CI Workflow

The smoke tests run automatically in GitHub Actions:
- On push to `main` branch (when backend files change)
- On pull requests (when backend files change)

The workflow file is located at `.github/workflows/smoke-integration.yml`.

## Adding New Smoke Tests

Smoke tests should:
1. Be marked with `@pytest.mark.smoke` or include `pytestmark = pytest.mark.smoke`
2. Test critical API flows that depend on database state
3. Be idempotent (can run multiple times without failure)
4. Be fast (smoke tests should complete quickly)

Example:
```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

pytestmark = pytest.mark.smoke
client = TestClient(app)

def test_critical_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
```

## Troubleshooting

### Connection refused error
Ensure Postgres is running and the DATABASE_URL is correct.

### Migration errors
Make sure you're running migrations from the `backend` directory.

### Seed data errors
The seed script skips seeding if data already exists. To reset, drop and recreate the database:
```bash
docker-compose -f docker-compose-postgres.yaml down -v
docker-compose -f docker-compose-postgres.yaml up -d
```
