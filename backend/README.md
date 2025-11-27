# Home Budget Web — Backend

## Overview

FastAPI backend for the Home Budget Web application.

## Current Mode: JSON Storage

The backend currently runs in *JSON mode*.  
All expenses and incomes are read/written to simple `.json` files in `app/data/`.

This is a temporary implementation.  
The storage layer will be replaced with PostgreSQL in a future milestone.  
API contracts must stay stable so the switch is transparent to tests.

---

## Prerequisites

- **Python 3.11+**
- **Poetry** (Python dependency manager)
- **PostgreSQL** (optional for development, required for production)

---

## Setup

### 1. Install Dependencies

```bash
poetry install
```

### 2. Create Environment File

```bash
cp .env.example .env
```

The default `.env` settings work with the local PostgreSQL container.

### 3. Start PostgreSQL (Optional)

If you need PostgreSQL running locally:

```bash
# From the project root
docker compose -f docker-compose-postgres.yaml up -d
```

Connection string:
```
postgresql://budget:budget@localhost:5432/budget_db
```

---

## Running the Backend

### Using Poetry

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### Using the Convenience Script

```bash
./run_local.sh
```

The API will be available at http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Running Tests

```bash
# Run all tests (verbose)
poetry run pytest -v

# Run tests quietly
poetry run pytest -q

# Run with PYTHONPATH (if needed)
PYTHONPATH=$PYTHONPATH:$(pwd) poetry run pytest -v
```

Tests are API-only and do not depend on storage internals.

---

## Using Docker

### Run with Docker Compose (Full Stack)

From the project root:

```bash
docker compose up
```

### Run with Docker Compose (Backend + DB Only)

```bash
docker compose up db backend
```

### Using the Makefile

```bash
make build      # Build the container
make up         # Start the stack
make up-detached  # Start in background
make down       # Stop containers
make clean      # Stop and remove volumes
make test       # Run tests in container
make rebuild    # Rebuild from scratch
```

---

## Migrations

The project uses Alembic for database migrations.

> **Note**: The migration system is being set up. See the root [README.md](../README.md) for more details.

Migration files are stored in `migrations/`.

### Migration Commands (Future)

```bash
# Run all pending migrations
poetry run alembic upgrade head

# Create a new migration
poetry run alembic revision --autogenerate -m "Description"

# Downgrade one migration
poetry run alembic downgrade -1
```

See [migrations/migration_pr_template.md](migrations/migration_pr_template.md) for migration PR guidelines.

---

## Seeding Data

> **Note**: The seed script is being developed. See the root [README.md](../README.md) for more details.

---

## Project Structure

```
backend/
├── app/
│   ├── core/           # Settings, storage utilities
│   ├── data/           # JSON storage files (temporary)
│   ├── routers/        # API route handlers
│   └── main.py         # Application entry point
├── migrations/         # Alembic migration files
├── tests/              # API tests
├── .env.example        # Environment template
├── Makefile            # Development commands
├── pyproject.toml      # Python dependencies
└── run_local.sh        # Local development script
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment mode | dev |
| `DATABASE_URL` | PostgreSQL connection string | postgresql://budget:budget@localhost:5432/budget_db |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

---

## Development Notes

- Do not rely on JSON file structure (it will be replaced).
- API responses must remain stable.
- Tests should not reference storage internals.
- Storage implementation stays fully swappable.

---

## Related Documentation

- [Root README](../README.md) - Full project documentation
- [Frontend README](../frontend/README.md) - Frontend documentation
- [DB Schema Guidelines](db_schema_guidelines.md) - Database design guidelines
- [Migration PR Template](migrations/migration_pr_template.md) - PR template for migrations
