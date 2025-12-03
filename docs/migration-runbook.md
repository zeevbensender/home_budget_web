# Migration Runbook: Backup, Rollback & Escalation

**Project:** Home Budget Web  
**Backend:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL  
**Owner:** @zeevbensender  
**Labels:** ops, docs, runbook

This runbook provides step-by-step procedures for database migrations including pre-migration backup, monitoring migration progress, rollback steps, and escalation contacts.

---

## Table of Contents

1. [Pre-Migration Checklist](#1-pre-migration-checklist)
2. [Pre-Migration Backup](#2-pre-migration-backup)
3. [Running the Migration](#3-running-the-migration)
4. [Monitoring Migration Progress](#4-monitoring-migration-progress)
5. [Post-Migration Validation](#5-post-migration-validation)
6. [Rollback Procedures](#6-rollback-procedures)
7. [Escalation & Contacts](#7-escalation--contacts)
8. [Quick Reference Commands](#8-quick-reference-commands)

---

## 1. Pre-Migration Checklist

Before running any migration, complete the following pre-checks:

### 1.1 Database Health Checks

```bash
# Check database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Check current database size
psql $DATABASE_URL -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# Check active connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Check for long-running queries (> 5 minutes)
psql $DATABASE_URL -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes' 
AND state != 'idle';"

# Check for locks
psql $DATABASE_URL -c "SELECT relation::regclass, mode, granted 
FROM pg_locks 
WHERE NOT granted;"
```

### 1.2 Alembic Status Check

```bash
# Navigate to backend directory
cd backend

# Check current migration revision
poetry run alembic current

# Show pending migrations
poetry run alembic history --verbose

# Preview migration SQL (dry run)
poetry run alembic upgrade head --sql
```

### 1.3 Pre-Migration Verification

- [ ] All pending migrations reviewed and approved
- [ ] Migration tested in staging/local environment
- [ ] Backup completed successfully (see Section 2)
- [ ] No long-running queries or locks on target tables
- [ ] Sufficient disk space available
- [ ] Maintenance window scheduled (if applicable)
- [ ] Team notified of upcoming migration

---

## 2. Pre-Migration Backup

### 2.1 Full Database Backup with pg_dump

```bash
# Set timestamp for backup file naming
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Full database backup (recommended for production)
pg_dump $DATABASE_URL \
  --format=custom \
  --verbose \
  --file="backup_${TIMESTAMP}.dump"

# Verify backup file was created
ls -lh backup_${TIMESTAMP}.dump

# Test backup integrity
pg_restore --list backup_${TIMESTAMP}.dump > /dev/null && echo "Backup verified successfully"
```

### 2.2 Schema-Only Backup

```bash
# Backup schema only (useful for quick rollback reference)
pg_dump $DATABASE_URL \
  --schema-only \
  --file="schema_backup_${TIMESTAMP}.sql"
```

### 2.3 Table-Specific Backup

For migrations affecting specific tables:

```bash
# Backup specific table(s) before migration
pg_dump $DATABASE_URL \
  --format=custom \
  --table=expenses \
  --table=incomes \
  --file="tables_backup_${TIMESTAMP}.dump"
```

### 2.4 Backup with Docker Compose (Local/CI)

```bash
# Using docker-compose for local/CI environments
docker-compose -f docker-compose-postgres.yaml exec -T db \
  pg_dump -U poc_user -d poc_db \
  --format=custom \
  > backup_${TIMESTAMP}.dump
```

### 2.5 Backup Storage Recommendations

- Store backups in a secure location outside the database server
- For production: Use cloud storage (S3, GCS) with appropriate retention policies
- Keep at least the last 3 successful migration backups
- Document the backup location in the migration PR

---

## 3. Running the Migration

### 3.1 Standard Migration

```bash
# Navigate to backend directory
cd backend

# Run all pending migrations
poetry run alembic upgrade head
```

### 3.2 Step-by-Step Migration

For critical migrations, run one revision at a time:

```bash
# Upgrade to specific revision
poetry run alembic upgrade +1

# Or upgrade to a specific revision ID
poetry run alembic upgrade <revision_id>
```

### 3.3 Migration with Logging

```bash
# Run migration with detailed logging
poetry run alembic upgrade head 2>&1 | tee migration_$(date +%Y%m%d_%H%M%S).log
```

---

## 4. Monitoring Migration Progress

### 4.1 Real-Time Query Monitoring

In a separate terminal, monitor active queries during migration:

```bash
# Watch for long-running queries
watch -n 5 'psql $DATABASE_URL -c "SELECT pid, now() - query_start AS duration, state, query FROM pg_stat_activity WHERE state != '\''idle'\'' ORDER BY query_start;"'
```

### 4.2 Lock Monitoring

```bash
# Monitor locks during migration
psql $DATABASE_URL -c "
SELECT 
  blocked_locks.pid AS blocked_pid,
  blocked_activity.usename AS blocked_user,
  blocking_locks.pid AS blocking_pid,
  blocking_activity.usename AS blocking_user,
  blocked_activity.query AS blocked_statement,
  blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
  ON blocking_locks.locktype = blocked_locks.locktype
  AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
  AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
  AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
  AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
  AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
  AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
  AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
  AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
  AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
  AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;"
```

### 4.3 Grafana Dashboard Monitoring

During migrations, monitor the following dashboards:
- **Database Metrics**: `<GRAFANA_URL>/d/home-budget-db`
- **API Performance**: `<GRAFANA_URL>/d/home-budget-api`

See [grafana-prometheus-integration.md](grafana-prometheus-integration.md) for setup.

---

## 5. Post-Migration Validation

### 5.1 Schema Validation Queries

```sql
-- Verify migration was applied
SELECT * FROM alembic_version;

-- Check table structure (replace 'expenses' with your table)
\d expenses

-- Count records in affected tables
SELECT 
  'expenses' AS table_name, COUNT(*) AS row_count FROM expenses
UNION ALL
SELECT 
  'incomes' AS table_name, COUNT(*) AS row_count FROM incomes;
```

### 5.2 Data Integrity Checks

```sql
-- Check for NULL values in required columns (example for expenses)
SELECT COUNT(*) AS null_count 
FROM expenses 
WHERE date IS NULL OR amount IS NULL;

-- Verify foreign key relationships (if applicable)
SELECT e.id, e.category 
FROM expenses e 
LEFT JOIN categories c ON e.category_id = c.id 
WHERE e.category_id IS NOT NULL AND c.id IS NULL;

-- Check for duplicate records (if unique constraint was added)
SELECT column_name, COUNT(*) 
FROM table_name 
GROUP BY column_name 
HAVING COUNT(*) > 1;
```

### 5.3 Index Validation

```sql
-- Verify new indexes exist
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'expenses';

-- Check index usage stats
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'expenses';
```

### 5.4 Application Smoke Tests

```bash
# Navigate to backend directory
cd backend

# Run smoke tests against the migrated database
poetry run pytest -m smoke -v

# Run full test suite
poetry run pytest
```

### 5.5 API Health Check

```bash
# Check API health endpoint
curl -s http://localhost:8000/api/v1/health | jq .

# Test a sample endpoint (adjust as needed)
curl -s http://localhost:8000/api/v1/expenses | jq . | head -20
```

---

## 6. Rollback Procedures

### 6.1 Alembic Downgrade (Preferred)

If the migration includes a reversible downgrade:

```bash
# Navigate to backend directory
cd backend

# Downgrade one revision
poetry run alembic downgrade -1

# Or downgrade to specific revision
poetry run alembic downgrade <revision_id>

# Verify current revision after downgrade
poetry run alembic current
```

### 6.2 Full Database Restore

If Alembic downgrade is not possible or migration is irreversible:

```bash
# CAUTION: This replaces the entire database!

# Step 1: Stop the application to prevent new writes
# (On Render: pause the service via dashboard)

# Step 2: Restore from backup
pg_restore \
  --clean \
  --if-exists \
  --dbname=$DATABASE_URL \
  --verbose \
  backup_<TIMESTAMP>.dump

# Step 3: Verify restoration
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"

# Step 4: Restart the application
```

### 6.3 Table-Specific Restore

To restore specific tables only:

```bash
# Restore specific table from backup
pg_restore \
  --dbname=$DATABASE_URL \
  --table=expenses \
  --data-only \
  --clean \
  backup_<TIMESTAMP>.dump
```

### 6.4 Rollback with Docker Compose (Local/CI)

```bash
# Stop containers
docker-compose -f docker-compose-postgres.yaml down

# Remove volume (destroys current data)
docker volume rm home_budget_web_postgres_data

# Restart containers
docker-compose -f docker-compose-postgres.yaml up -d

# Wait for Postgres to be ready
docker-compose -f docker-compose-postgres.yaml exec db pg_isready -U poc_user -d poc_db

# Restore from backup
cat backup_<TIMESTAMP>.dump | docker-compose -f docker-compose-postgres.yaml exec -T db \
  pg_restore -U poc_user -d poc_db

# Re-run migrations to desired state
cd backend && poetry run alembic upgrade <target_revision>
```

### 6.5 Rollback Decision Tree

```
Migration failed or causing issues?
│
├─► Data corruption detected?
│   └─► YES → Full database restore (Section 6.2)
│   └─► NO  → Continue to next question
│
├─► Migration is reversible?
│   └─► YES → Alembic downgrade (Section 6.1)
│   └─► NO  → Continue to next question
│
├─► Only specific tables affected?
│   └─► YES → Table-specific restore (Section 6.3)
│   └─► NO  → Full database restore (Section 6.2)
│
└─► Contact escalation (Section 7)
```

---

## 7. Escalation & Contacts

### 7.1 Primary Contact

| Role | Contact | GitHub Handle |
|------|---------|---------------|
| **Owner / DB Admin** | Zeev Bensender | @zeevbensender |
| **Project Assistant** | (AI Assistant) | — |

### 7.2 Escalation Path

1. **Level 1 - Self-Service**
   - Follow this runbook for standard operations
   - Check [db_migration_guidelines.md](../backend/db_migration_guidelines.md) for migration best practices
   - Review migration logs and error messages

2. **Level 2 - Owner Escalation**
   - If rollback fails or data integrity issues persist
   - If migration blocks production deployment
   - Contact: **@zeevbensender** via GitHub issue or PR comment

3. **Level 3 - Emergency**
   - Service outage affecting users
   - Data loss or corruption confirmed
   - Immediate action: Pause application, preserve logs, contact @zeevbensender

### 7.3 Incident Documentation

When escalating, include:
- Migration revision ID
- Timestamp of migration attempt
- Error messages and logs
- Steps already attempted
- Backup file location and timestamp

---

## 8. Quick Reference Commands

### Backup Commands

```bash
# Full backup
pg_dump $DATABASE_URL --format=custom --verbose --file="backup_$(date +%Y%m%d_%H%M%S).dump"

# Schema-only backup
pg_dump $DATABASE_URL --schema-only --file="schema_$(date +%Y%m%d_%H%M%S).sql"
```

### Migration Commands

```bash
# Check current revision
poetry run alembic current

# Preview migration SQL
poetry run alembic upgrade head --sql

# Run migration
poetry run alembic upgrade head

# Downgrade one revision
poetry run alembic downgrade -1
```

### Validation Commands

```bash
# Run smoke tests
poetry run pytest -m smoke -v

# Check Alembic version
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"
```

### Restore Commands

```bash
# Full restore
pg_restore --clean --if-exists --dbname=$DATABASE_URL backup_<TIMESTAMP>.dump

# Table-specific restore
pg_restore --dbname=$DATABASE_URL --table=<table_name> backup_<TIMESTAMP>.dump
```

---

## Related Documentation

- [DB Migration Guidelines](../backend/db_migration_guidelines.md) - Engineering principles and PR template
- [DB Schema Guidelines](../backend/db_schema_guidelines.md) - Schema evolution rules
- [Smoke Tests](smoke-tests.md) - Integration testing procedures
- [Migration PR Template](../.github/PULL_REQUEST_TEMPLATE/migration_pr_template.md) - PR checklist for migrations
- [Grafana Integration](grafana-prometheus-integration.md) - Monitoring setup

---

*Last updated: 2025-12-03*  
*Document owner: @zeevbensender*
