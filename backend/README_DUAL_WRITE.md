# Dual-Write Mode - PostgreSQL Transition Guide

## Overview

This document explains how to use the dual-write feature during the transition from JSON storage to PostgreSQL persistence.

## Current Implementation Status

- ✅ **Phase 1**: Repository Layer - Complete
- ✅ **Phase 2**: Service Layer Integration - Complete
- ✅ **Phase 3**: Dual-Write Mode - Complete
- ⏸️ **Phase 4**: Read from Database - Not yet implemented
- ⏸️ **Phase 5**: Full Database Mode - Not yet implemented

## How Dual-Write Works

When dual-write is enabled, the application:

1. **Writes to JSON first** (remains authoritative source)
2. **Also writes to PostgreSQL** (for testing and validation)
3. **Reads from JSON** (ensures consistency)
4. **Logs all dual-write operations** (for monitoring)
5. **Handles DB failures gracefully** (won't break API responses)

## Enabling Dual-Write

### Using Environment Variables

```bash
# Enable dual-write mode
export FF_DUAL_WRITE_ENABLED=true

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker Compose

Add to your `docker-compose.yaml`:

```yaml
services:
  backend:
    environment:
      - FF_DUAL_WRITE_ENABLED=true
      - DATABASE_URL=postgresql://poc_user:poc_password@db:5432/poc_db
```

### Using Database Configuration

Alternatively, insert a feature flag in the database:

```sql
INSERT INTO feature_flags (name, enabled, description)
VALUES ('DUAL_WRITE_ENABLED', true, 'Enable dual-write to PostgreSQL');
```

## Testing Dual-Write

### 1. Set up PostgreSQL

```bash
# Start PostgreSQL container
docker-compose -f docker-compose-postgres.yaml up -d

# Run migrations
cd backend
poetry run alembic upgrade head
```

### 2. Enable Dual-Write

```bash
export FF_DUAL_WRITE_ENABLED=true
export DATABASE_URL=postgresql://poc_user:poc_password@localhost:5432/poc_db
```

### 3. Test API Operations

```bash
# Create an expense (writes to JSON + PostgreSQL)
curl -X POST http://localhost:8000/api/v1/expense \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-07",
    "category": "Groceries",
    "amount": 150.50,
    "account": "Cash",
    "currency": "₪",
    "notes": "Weekly shopping"
  }'

# List expenses (reads from JSON)
curl http://localhost:8000/api/v1/expense
```

### 4. Verify Database Writes

```bash
# Connect to PostgreSQL
psql postgresql://poc_user:poc_password@localhost:5432/poc_db

# Check expenses table
SELECT * FROM expenses;
```

## Monitoring Dual-Write

### Check Application Logs

Look for log messages like:

```
INFO: Dual-write: Created expense 5 in database
INFO: Dual-write: Updated expense 5 in database
INFO: Dual-write: Deleted expense 5 from database
WARNING: Dual-write failed for expense 5: connection error
```

### Verify Data Consistency

```python
# Compare JSON and database records
import json
from app.core.storage import load_json
from app.core.database import SessionLocal
from app.repositories.expense_repository import ExpenseRepository

# Load from JSON
json_expenses = load_json("expenses.json", [])

# Load from database
db = SessionLocal()
repo = ExpenseRepository(db)
db_expenses = repo.list()

# Compare counts
print(f"JSON expenses: {len(json_expenses)}")
print(f"DB expenses: {len(db_expenses)}")
```

## Troubleshooting

### Dual-Write Not Working

**Symptom**: No logs showing "Dual-write:" messages

**Solutions**:
1. Verify feature flag is enabled:
   ```bash
   echo $FF_DUAL_WRITE_ENABLED
   ```

2. Check database connection:
   ```bash
   psql $DATABASE_URL -c "SELECT 1;"
   ```

3. Check application logs for errors

### Database Connection Errors

**Symptom**: Logs showing "Dual-write failed: connection error"

**Solutions**:
1. Verify DATABASE_URL is correct
2. Check PostgreSQL is running:
   ```bash
   docker-compose -f docker-compose-postgres.yaml ps
   ```

3. Run migrations:
   ```bash
   cd backend && poetry run alembic upgrade head
   ```

### Data Inconsistencies

**Symptom**: JSON and database have different data

**Solutions**:
1. Database writes are asynchronous and may fail silently
2. Check logs for "Dual-write failed" warnings
3. Re-sync data by re-creating records

## Disabling Dual-Write

To disable dual-write and return to JSON-only mode:

```bash
# Using environment variables
export FF_DUAL_WRITE_ENABLED=false

# Or using database
UPDATE feature_flags
SET enabled = false
WHERE name = 'DUAL_WRITE_ENABLED';
```

## Next Steps

Once dual-write has been running successfully:

1. **Phase 4**: Enable `USE_DATABASE_STORAGE` to read from PostgreSQL
2. **Validate**: Verify database reads match JSON data
3. **Phase 5**: Remove JSON storage code entirely

## Architecture Diagram

```
┌─────────────┐
│   Router    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Service   │
└──────┬──────┘
       │
       ├───────────────────┐
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ JSON Storage│     │ Repository  │
│ (Primary)   │     │ (Secondary) │
└─────────────┘     └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    └─────────────┘
```

## Related Documentation

- [PostgreSQL Transition Plan](../docs/milestones/json-to-postgresql-transition-plan.md)
- [Feature Flags Guide](../docs/feature-flags.md)
- [Migration Runbook](../docs/migration-runbook.md)

---

*Last Updated: 2025-12-07*  
*Status: Phase 3 Complete*
