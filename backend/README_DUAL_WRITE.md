# Dual-Write Mode - PostgreSQL Transition Guide

## Overview

This document explains how to use the dual-write feature during the transition from JSON storage to PostgreSQL persistence.

## Current Implementation Status

- ✅ **Phase 1**: Repository Layer - Complete
- ✅ **Phase 2**: Service Layer Integration - Complete
- ✅ **Phase 3**: Dual-Write Mode - Complete
- ✅ **Phase 4**: Read from Database - Complete
- ⏸️ **Phase 5**: Full Database Mode - Not yet implemented

## How It Works

### Phase 3: Dual-Write Mode (JSON Primary)

When dual-write is enabled but database storage is not enabled:

1. **Writes to JSON first** (primary source)
2. **Also writes to PostgreSQL** (secondary, for testing)
3. **Reads from JSON** (authoritative)
4. **Logs all dual-write operations** (for monitoring)
5. **Handles DB failures gracefully** (won't break API responses)

### Phase 4: Database Storage Mode (PostgreSQL Primary)

When both database storage and dual-write are enabled:

1. **Writes to PostgreSQL first** (primary source)
2. **Also writes to JSON** (secondary, for rollback safety)
3. **Reads from PostgreSQL** (authoritative)
4. **Logs all dual-write operations** (for monitoring)
5. **Handles JSON failures gracefully** (won't break API responses)

## Enabling Feature Flags

### Phase 3: Dual-Write Mode (JSON Primary)

```bash
# Enable dual-write mode only
export FF_DUAL_WRITE_ENABLED=true

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Phase 4: Database Storage Mode (PostgreSQL Primary)

```bash
# Enable database storage AND dual-write for rollback safety
export FF_USE_DATABASE_STORAGE=true
export FF_DUAL_WRITE_ENABLED=true
export DATABASE_URL=postgresql://poc_user:poc_password@localhost:5432/poc_db

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Docker Compose

Add to your `docker-compose.yaml`:

```yaml
services:
  backend:
    environment:
      # Phase 3: Dual-write mode
      - FF_DUAL_WRITE_ENABLED=true
      
      # Phase 4: Database storage mode
      - FF_USE_DATABASE_STORAGE=true
      - FF_DUAL_WRITE_ENABLED=true
      
      - DATABASE_URL=postgresql://poc_user:poc_password@db:5432/poc_db
```

### Using Database Configuration

Alternatively, insert feature flags in the database:

```sql
-- Phase 3: Dual-write mode
INSERT INTO feature_flags (name, enabled, description)
VALUES ('DUAL_WRITE_ENABLED', true, 'Enable dual-write to PostgreSQL');

-- Phase 4: Database storage mode
INSERT INTO feature_flags (name, enabled, description)
VALUES ('USE_DATABASE_STORAGE', true, 'Read from PostgreSQL instead of JSON');
```

## Testing Phase 4: Database Storage Mode

### 1. Set up PostgreSQL

```bash
# Start PostgreSQL container
docker-compose -f docker-compose-postgres.yaml up -d

# Run migrations
cd backend
poetry run alembic upgrade head
```

### 2. Enable Database Storage with Dual-Write

```bash
export FF_USE_DATABASE_STORAGE=true
export FF_DUAL_WRITE_ENABLED=true
export DATABASE_URL=postgresql://poc_user:poc_password@localhost:5432/poc_db
```

### 3. Test API Operations

```bash
# Create an expense (writes to PostgreSQL + JSON)
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

# List expenses (reads from PostgreSQL)
curl http://localhost:8000/api/v1/expense
```

### 4. Verify Database Reads

```bash
# Connect to PostgreSQL
psql postgresql://poc_user:poc_password@localhost:5432/poc_db

# Check expenses table
SELECT * FROM expenses;

# The data should match what the API returns
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

## Rollback Procedures

### Rollback from Phase 4 to Phase 3

If you encounter issues with database reads:

```bash
# Disable database storage, keep dual-write enabled
export FF_USE_DATABASE_STORAGE=false
export FF_DUAL_WRITE_ENABLED=true

# Restart the application
# This will revert to reading from JSON while still writing to both stores
```

### Rollback to JSON-Only Mode

To completely disable database features:

```bash
# Disable all database features
export FF_USE_DATABASE_STORAGE=false
export FF_DUAL_WRITE_ENABLED=false

# Or using database
UPDATE feature_flags SET enabled = false WHERE name = 'USE_DATABASE_STORAGE';
UPDATE feature_flags SET enabled = false WHERE name = 'DUAL_WRITE_ENABLED';

# Restart the application
```

## Next Steps

### Phase 4 Complete

Once database storage has been running successfully:

1. **Monitor**: Watch application logs for any dual-write failures
2. **Validate**: Verify database reads match expected data
3. **Compare**: Check data consistency between JSON and PostgreSQL
4. **Prepare**: Plan for Phase 5 when ready to remove JSON storage entirely

### Moving to Phase 5

Once confident in Phase 4:

1. **Disable Dual-Write**: Set `FF_DUAL_WRITE_ENABLED=false`
2. **Remove JSON Code**: Clean up storage.py and related JSON code
3. **Archive JSON**: Backup JSON files for compliance/disaster recovery
4. **Clean Flags**: Remove feature flag checks from codebase

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
