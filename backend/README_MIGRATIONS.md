# Database Migrations

## Overview

This project uses Alembic for database schema migrations. Migrations are automatically run when the Docker container starts.

## How It Works

1. **Automatic Migration on Startup**: The `entrypoint.sh` script runs `alembic upgrade head` before starting the application
2. **Database Tables**: The initial migration creates `expenses` and `incomes` tables
3. **Feature Flags**: A separate migration adds the `feature_flags` table

## Migration Files Location

- **Configuration**: `backend/alembic.ini`
- **Migration Scripts**: `backend/migrations/versions/`
- **Environment Setup**: `backend/migrations/env.py`

## Existing Migrations

1. **877b61b7b538_initial_poc_schema.py** - Creates expenses and incomes tables
2. **2a3b4c5d6e7f_add_feature_flags_table.py** - Creates feature_flags table
3. **0c27a824a398_add_test_column_to_expenses.py** - Example migration

## Running Migrations Manually

If you need to run migrations manually:

```bash
# Inside the backend container
docker exec -it home_budget_backend bash
cd /app
alembic -c /app/alembic.ini upgrade head

# Or from your local machine (if database is accessible)
cd backend
alembic upgrade head
```

## Creating New Migrations

```bash
# Auto-generate migration from model changes
cd backend
alembic revision --autogenerate -m "description of changes"

# Create empty migration
alembic revision -m "description of changes"
```

## Troubleshooting

### "relation does not exist" Error

If you see errors like `relation "incomes" does not exist`, it means migrations haven't run. This can happen if:

1. The database was created before migrations were automated
2. The container was started without the entrypoint script

**Solution**: Rebuild the container to ensure entrypoint script runs:
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up
```

### Check Migration Status

```bash
# Show current migration version
docker exec -it home_budget_backend alembic -c /app/alembic.ini current

# Show migration history
docker exec -it home_budget_backend alembic -c /app/alembic.ini history
```

## Docker Compose Configuration

The `docker-compose.yaml` ensures:
- Backend waits for database health check before starting
- Entrypoint script runs migrations automatically
- Migrations directory is mounted for development

## Important Notes

- **DO NOT** manually create tables - always use migrations
- **DO NOT** delete migration files - they form a history
- **TEST** migrations on a development database first
- **BACKUP** production database before running migrations
