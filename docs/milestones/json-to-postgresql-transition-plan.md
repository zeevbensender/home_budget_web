# Milestone: Transition from JSON Storage to PostgreSQL Persistence

**Project:** Home Budget Web  
**Backend:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL  
**Owner:** @zeevbensender  
**Status:** Planning  
**Created:** 2024-12-07  
**Target Completion:** TBD

---

## 🎯 Executive Summary

This document outlines the complete transition plan from the current JSON file-based storage (PoC mode) to a production-ready PostgreSQL database persistence layer. The transition will be executed in phases to ensure zero-downtime deployment, maintain API stability, and support multi-user environments with proper data integrity.

### Key Objectives

1. **Replace JSON-based CRUD logic** with SQLAlchemy ORM operations
2. **Deploy clean database schema** aligned with current features (expenses, incomes, feature flags)
3. **Safe traffic switch** from JSON files to PostgreSQL database
4. **No data migration required** (PoC stage - acceptable to start fresh)
5. **Production-ready infrastructure** for both development and production environments

---

## 📋 Table of Contents

1. [Current State Analysis](#current-state-analysis)
2. [Target Architecture](#target-architecture)
3. [Phased Transition Plan](#phased-transition-plan)
4. [Development Environment Setup](#development-environment-setup)
5. [Production Environment Setup](#production-environment-setup)
6. [Code Changes Required](#code-changes-required)
7. [Testing Strategy](#testing-strategy)
8. [Rollout Plan](#rollout-plan)
9. [Rollback Strategy](#rollback-strategy)
10. [Open Questions & Recommendations](#open-questions--recommendations)
11. [Success Criteria](#success-criteria)
12. [Timeline & Dependencies](#timeline--dependencies)

---

## 1. Current State Analysis

### 1.1 Existing Implementation

**Storage Layer:**
- JSON files in `backend/app/data/` directory
- `storage.py` provides `load_json()` and `save_json()` utilities
- In-memory Python lists for CRUD operations
- No transaction support, no concurrent access handling

**API Layer:**
- `expense_router.py`: Direct manipulation of in-memory lists
- `income_router.py`: Direct manipulation of in-memory lists
- Global state management with JSON file persistence

**Database Infrastructure (Already Present):**
- ✅ SQLAlchemy 2.0 models defined (`expense.py`, `income.py`, `feature_flag.py`)
- ✅ Database configuration in `core/database.py`
- ✅ Alembic migrations setup with initial schema
- ✅ PostgreSQL support in dependencies

### 1.2 Current Pain Points

1. **No transaction support** - Data can be corrupted during concurrent writes
2. **No data integrity** - No foreign keys, constraints, or validation at DB level
3. **Limited scalability** - File I/O on every request, no caching, no connection pooling
4. **No query optimization** - Full file reads for simple queries
5. **No audit trail** - No tracking of who changed what and when
6. **Multi-user risks** - Race conditions with concurrent access
7. **No backup/restore** - File-based backups are primitive

### 1.3 What's Already Built

**Advantages:**
- ✅ Database models already designed and tested
- ✅ Migration infrastructure in place (Alembic)
- ✅ Feature flag system for gradual rollouts
- ✅ Comprehensive migration guidelines documented
- ✅ Test infrastructure compatible with both approaches
- ✅ Docker Compose setup for PostgreSQL development

---

## 2. Target Architecture

### 2.1 Persistence Layer

```
┌─────────────────────────────────────────────────────┐
│                   API Endpoints                      │
│            (expense_router, income_router)           │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                  Service Layer                       │
│          (expense_service, income_service)           │
│              Business Logic & Validation             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│               Repository Layer (NEW)                 │
│         (expense_repository, income_repository)      │
│           SQLAlchemy ORM Operations                  │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│                  PostgreSQL Database                 │
│              expenses | incomes | feature_flags      │
└─────────────────────────────────────────────────────┘
```

### 2.2 Database Schema

**Tables (already defined in migrations):**

```sql
-- expenses table
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    business VARCHAR(255),
    category VARCHAR(100) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    account VARCHAR(100) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT '₪',
    notes TEXT,
    test_column VARCHAR(50)  -- for testing migrations
);

-- incomes table
CREATE TABLE incomes (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    category VARCHAR(100) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    account VARCHAR(100) NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT '₪',
    notes TEXT
);

-- feature_flags table
CREATE TABLE feature_flags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT FALSE,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, user_id)
);

-- Alembic version tracking
CREATE TABLE alembic_version (
    version_num VARCHAR(32) PRIMARY KEY
);
```

### 2.3 Recommended Future Enhancements (Not in Scope)

These are intentionally excluded from this milestone but documented for future reference:

1. **User Authentication & Multi-tenancy** (Future Milestone)
   - Add `user_id` foreign key to expenses/incomes
   - User table with authentication
   - Row-level security

2. **Categories & Tags** (Future Milestone)
   - Normalize categories into separate table
   - Many-to-many tags relationship
   - Category budgets and limits

3. **Audit Trail** (Future Milestone)
   - Change tracking table
   - Created/updated timestamps on all tables
   - User action logging

4. **Soft Deletes** (Future Milestone)
   - `deleted_at` timestamp column
   - Support for data recovery

---

## 3. Phased Transition Plan

### Phase 1: Infrastructure & Repository Layer (Week 1)

**Objective:** Build database access layer without changing API behavior

**Tasks:**
1. ✅ PostgreSQL already configured in `docker-compose-postgres.yaml`
2. Create repository layer: `app/repositories/expense_repository.py`
3. Create repository layer: `app/repositories/income_repository.py`
4. Create database session dependency injection pattern
5. Unit tests for repository layer (isolated from API tests)

**Feature Flag:** `USE_DATABASE_STORAGE` (default: `false`)

**Outcome:** Repository layer ready, JSON still active

---

### Phase 2: Parallel Write Mode (Week 2)

**Objective:** Write to both JSON and DB, read from JSON (safety net)

**Tasks:**
1. Update routers to inject database session
2. Implement dual-write logic in service layer
3. Log any discrepancies between JSON and DB writes
4. Smoke tests with both storage systems active

**Feature Flag:** `USE_DATABASE_STORAGE=false`, `DUAL_WRITE_ENABLED=true`

**Outcome:** Data written to both systems, confidence in DB writes

---

### Phase 3: Switch to Read from DB (Week 3)

**Objective:** Read from DB, write to both (validate DB reads)

**Tasks:**
1. Update service layer to read from repository
2. Keep JSON writes for rollback safety
3. Full integration test suite against database
4. Performance testing (query times, connection pooling)
5. Monitor error rates and query performance

**Feature Flag:** `USE_DATABASE_STORAGE=true`, `DUAL_WRITE_ENABLED=true`

**Outcome:** Application uses database for reads and writes, JSON as backup

---

### Phase 4: DB-Only Mode (Week 4)

**Objective:** Remove JSON dependency entirely

**Tasks:**
1. Remove JSON file writes
2. Remove `app/core/storage.py` (deprecated)
3. Remove in-memory list management from routers
4. Remove JSON fallback data from routers
5. Update documentation and README
6. Final migration validation

**Feature Flag:** `USE_DATABASE_STORAGE=true`, `DUAL_WRITE_ENABLED=false`

**Outcome:** Production-ready PostgreSQL persistence, JSON code removed

---

### Phase 5: Production Deployment & Monitoring (Week 5)

**Objective:** Deploy to production and monitor

**Tasks:**
1. Deploy to staging environment (Render or similar)
2. Run smoke tests against staging database
3. Deploy to production with monitoring
4. Set up database backups (automated)
5. Set up database monitoring (connection pool, slow queries)
6. Document operational runbooks

**Feature Flag:** All flags removed (stable state)

**Outcome:** Production database operational, monitoring in place

---

## 4. Development Environment Setup

### 4.1 Local Development with Docker Compose

**Prerequisites:**
- Docker and Docker Compose installed
- Python 3.11+
- Poetry (optional, pip works too)

**Setup Steps:**

```bash
# 1. Start PostgreSQL container
cd /path/to/home_budget_web
docker-compose -f docker-compose-postgres.yaml up -d

# 2. Verify database is running
docker-compose -f docker-compose-postgres.yaml ps

# 3. Install backend dependencies
cd backend
pip install -r requirements.txt

# 4. Set environment variables
export DATABASE_URL="postgresql://poc_user:poc_password@localhost:5432/poc_db"

# 5. Run migrations
alembic upgrade head

# 6. Verify migration status
alembic current

# 7. (Optional) Seed test data
python scripts/seed_smoke.py

# 8. Start backend server
uvicorn app.main:app --reload --port 8000

# 9. Run tests
pytest -v
```

### 4.2 Environment Variables

**Required:**
```bash
DATABASE_URL=postgresql://poc_user:poc_password@localhost:5432/poc_db
ENV=dev
PORT=8000
```

**Feature Flags (during transition):**
```bash
# Phase 1: JSON only (default)
FF_USE_DATABASE_STORAGE=false

# Phase 2: Dual write
FF_USE_DATABASE_STORAGE=false
FF_DUAL_WRITE_ENABLED=true

# Phase 3: DB reads, dual write
FF_USE_DATABASE_STORAGE=true
FF_DUAL_WRITE_ENABLED=true

# Phase 4+: DB only
FF_USE_DATABASE_STORAGE=true
FF_DUAL_WRITE_ENABLED=false
```

### 4.3 Database Management Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history

# Show current revision
alembic current

# Generate SQL without executing (preview)
alembic upgrade head --sql
```

### 4.4 Testing Against Database

```bash
# Run all tests (uses JSON by default in test mode)
pytest

# Run tests with database (set env var)
export FF_USE_DATABASE_STORAGE=true
pytest

# Run smoke tests only
pytest -m smoke

# Run with coverage
pytest --cov=app --cov-report=html
```

---

## 5. Production Environment Setup

### 5.1 Render.com Deployment

**Current Configuration (`render.yaml`):**
- Backend service: Docker-based FastAPI app
- Database: PostgreSQL (free tier initially)
- Auto-deploy from main branch

**Database Connection:**
```yaml
envVars:
  - key: DATABASE_URL
    fromDatabase:
      name: hbw-db
      property: connectionString
```

### 5.2 Production Checklist

**Before First Production Deployment:**

- [ ] Database created on Render (or hosting platform)
- [ ] Database connection string configured
- [ ] Migrations run successfully: `alembic upgrade head`
- [ ] Smoke tests pass against production DB
- [ ] Monitoring enabled (see Section 5.3)
- [ ] Backup strategy confirmed (see Section 5.4)
- [ ] Rollback plan documented
- [ ] Feature flags configured correctly

### 5.3 Monitoring & Observability

**Database Metrics to Monitor:**

1. **Connection Pool:**
   - Active connections
   - Idle connections
   - Connection wait time
   - Pool exhaustion errors

2. **Query Performance:**
   - Slow query log (queries > 1s)
   - Most frequent queries
   - Query execution time (p50, p95, p99)
   - Index usage statistics

3. **Database Health:**
   - Database size growth
   - Table sizes
   - Disk I/O
   - Replication lag (if applicable)

4. **Application Metrics:**
   - HTTP response times
   - Error rates by endpoint
   - Request volume
   - Feature flag usage

**Recommended Tools (Low Cost/Free):**

1. **Sentry** (Error Tracking)
   - Free tier available (verify current limits at sentry.io/pricing)
   - Python/FastAPI integration
   - Real-time alerts

2. **UptimeRobot** (Health Monitoring)
   - Free tier: 50 monitors
   - 5-minute checks
   - Email/SMS alerts

3. **Grafana Cloud** (Metrics & Dashboards)
   - Free tier available
   - PostgreSQL exporter integration
   - Pre-built dashboards

4. **Render Metrics** (Platform-Native)
   - CPU, Memory, Network included
   - Database connection stats
   - No additional cost

### 5.4 Backup Strategy

**Automated Backups:**

**Option 1: Platform-Native (Recommended for Render)**
- Render PostgreSQL includes daily backups (free tier: 7 days retention)
- Automatic backup before migrations
- Point-in-time recovery (paid plans)

**Option 2: Manual/Scheduled Backups**
```bash
# Daily backup script
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
pg_dump $DATABASE_URL --format=custom --file="backup_${TIMESTAMP}.dump"

# Upload to cloud storage (S3, GCS, etc.)
# aws s3 cp backup_${TIMESTAMP}.dump s3://bucket/backups/
```

**Backup Schedule:**
- **Development:** Weekly (manual)
- **Staging:** Daily (automated)
- **Production:** Daily (automated) + pre-migration (manual)

**Retention Policy:**
- Development: Last 2 backups
- Staging: 7 days
- Production: 30 days

**Backup Testing:**
- Monthly restore test to verify backup integrity
- Document restore time (RTO: Recovery Time Objective)

---

## 6. Code Changes Required

### 6.1 New Files to Create

**Repositories (Data Access Layer):**

```
backend/app/repositories/
├── __init__.py
├── base_repository.py           # Base class with common CRUD operations
├── expense_repository.py         # Expense-specific queries
└── income_repository.py          # Income-specific queries
```

**Services (Business Logic Layer):**

```
backend/app/services/
├── expense_service.py            # Already exists, needs update for DB
├── income_service.py             # New file for income business logic
└── storage_adapter.py            # Adapter pattern for JSON/DB switching
```

### 6.2 Files to Modify

**Routers:**
- `app/routers/expense_router.py` - Inject DB session, call repositories
- `app/routers/income_router.py` - Inject DB session, call repositories

**Dependencies:**
- `app/core/database.py` - Already exists, may need connection pool tuning

**Tests:**
- `tests/conftest.py` - Add DB fixtures for testing
- All test files - Support both JSON and DB modes

### 6.3 Code Example: Repository Pattern

**base_repository.py:**
```python
"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from app.core.database import Base

T = TypeVar('T', bound=Base)

class BaseRepository(Generic[T]):
    """Generic repository for CRUD operations."""
    
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db
    
    def get_all(self) -> List[T]:
        """Get all records."""
        return self.db.query(self.model).all()
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def create(self, **kwargs) -> T:
        """Create new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance
    
    def update(self, id: int, **kwargs) -> Optional[T]:
        """Update existing record."""
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.db.commit()
            self.db.refresh(instance)
        return instance
    
    def delete(self, id: int) -> bool:
        """Delete record by ID."""
        instance = self.get_by_id(id)
        if instance:
            self.db.delete(instance)
            self.db.commit()
            return True
        return False
    
    def bulk_delete(self, ids: List[int]) -> int:
        """Delete multiple records by IDs."""
        count = self.db.query(self.model).filter(self.model.id.in_(ids)).delete(synchronize_session=False)
        self.db.commit()
        return count
```

**expense_repository.py:**
```python
"""Repository for expense data access."""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from app.models.expense import Expense
from app.repositories.base_repository import BaseRepository

class ExpenseRepository(BaseRepository[Expense]):
    """Repository for expense CRUD operations."""
    
    def __init__(self, db: Session):
        super().__init__(Expense, db)
    
    def get_by_date_range(self, start_date: date, end_date: date) -> List[Expense]:
        """Get expenses within date range."""
        return (
            self.db.query(Expense)
            .filter(Expense.date >= start_date, Expense.date <= end_date)
            .order_by(Expense.date.desc())
            .all()
        )
    
    def get_by_category(self, category: str) -> List[Expense]:
        """Get expenses by category."""
        return (
            self.db.query(Expense)
            .filter(Expense.category == category)
            .order_by(Expense.date.desc())
            .all()
        )
    
    def get_total_by_category(self) -> dict:
        """Get total expenses grouped by category."""
        from sqlalchemy import func
        results = (
            self.db.query(
                Expense.category,
                func.sum(Expense.amount).label('total')
            )
            .group_by(Expense.category)
            .all()
        )
        return {category: float(total) for category, total in results}
```

**Updated expense_router.py (excerpt):**
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.expense_repository import ExpenseRepository
from app.core.feature_flags import is_feature_enabled

router = APIRouter()

@router.get("/expense")
def list_expenses(db: Session = Depends(get_db)):
    """List all expenses."""
    if is_feature_enabled("USE_DATABASE_STORAGE", db=db):
        # Use database
        repo = ExpenseRepository(db)
        expenses = repo.get_all()
        return [expense_to_dict(e) for e in expenses]
    else:
        # Use JSON (legacy)
        from app.core.storage import load_json
        return load_json("expenses.json", [])

@router.post("/expense")
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    """Create new expense."""
    if is_feature_enabled("USE_DATABASE_STORAGE", db=db):
        repo = ExpenseRepository(db)
        new_expense = repo.create(**expense.dict())
        return {"status": "created", "expense": expense_to_dict(new_expense)}
    else:
        # JSON logic (legacy)
        # ... existing code ...
```

### 6.4 Files to Remove (Phase 4)

- `app/core/storage.py` - JSON file operations (deprecated)
- `app/data/*.json` - JSON data files (archived)

### 6.5 Database Session Management

**Dependency Injection Pattern:**
```python
from app.core.database import get_db

# In router
@router.get("/expense")
def list_expenses(db: Session = Depends(get_db)):
    # db session automatically managed (opened/closed)
    repo = ExpenseRepository(db)
    return repo.get_all()
```

**Transaction Handling:**
```python
# Automatic commit/rollback in repository
def create_expense(data: dict, db: Session):
    try:
        expense = Expense(**data)
        db.add(expense)
        db.commit()
        db.refresh(expense)
        return expense
    except Exception as e:
        db.rollback()
        raise
```

---

## 7. Testing Strategy

### 7.1 Test Categories

**Unit Tests:**
- Repository layer (isolated, uses transaction rollback)
- Service layer business logic
- Model validation

**Integration Tests:**
- API endpoints against real database
- End-to-end flows (create → read → update → delete)
- Concurrent request handling

**Smoke Tests:**
- Health check endpoints
- Basic CRUD operations
- Database connectivity

**Performance Tests:**
- Query execution times
- Connection pool stress test
- Bulk operations (100+ records)

### 7.2 Test Database Setup

**Option 1: SQLite for Unit Tests (Fast)**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from app.core.database import Base

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

**Option 2: PostgreSQL for Integration Tests (Accurate)**
```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from app.core.database import Base

@pytest.fixture(scope="session")
def postgres_test_db():
    # Use test database
    engine = create_engine("postgresql://test_user:test_pass@localhost:5432/test_db")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
```

### 7.3 Test Scenarios

**Critical Paths to Test:**

1. **Expense CRUD:**
   - ✓ Create expense with all fields
   - ✓ Create expense with minimal fields (auto-fill defaults)
   - ✓ Read all expenses
   - ✓ Read expense by ID
   - ✓ Update expense field by field
   - ✓ Delete expense
   - ✓ Bulk delete expenses

2. **Income CRUD:**
   - ✓ Same as expenses

3. **Data Integrity:**
   - ✓ Required fields validation (date, category, amount, account)
   - ✓ Amount precision (2 decimal places)
   - ✓ Default currency applied
   - ✓ Date format validation

4. **Concurrent Access:**
   - ✓ Simultaneous writes to different records
   - ✓ Simultaneous updates to same record
   - ✓ Transaction isolation

5. **Edge Cases:**
   - ✓ Empty database queries
   - ✓ Non-existent ID lookups
   - ✓ Invalid field updates
   - ✓ Duplicate IDs (should not be possible)

6. **Feature Flag Switching:**
   - ✓ JSON mode works
   - ✓ DB mode works
   - ✓ Dual write works (both updated)
   - ✓ Switching mid-operation handled gracefully

### 7.4 Test Coverage Goals

- **Target:** 85%+ code coverage
- **Critical paths:** 100% coverage (CRUD operations)
- **New code:** All new repository/service code covered

---

## 8. Rollout Plan

### 8.1 Development Environment Rollout

**Week 1-2: Internal Development**
1. Developers set up local PostgreSQL via Docker Compose
2. Run migrations: `alembic upgrade head`
3. Enable feature flag: `FF_USE_DATABASE_STORAGE=true`
4. Run full test suite
5. Validate all endpoints work with database

**Success Criteria:**
- ✓ All tests pass with database enabled
- ✓ No regressions in API behavior
- ✓ Developer documentation updated

### 8.2 Staging Environment Rollout

**Week 3: Staging Deployment**
1. Deploy to staging environment
2. Run migrations on staging database
3. Enable dual-write mode: `FF_DUAL_WRITE_ENABLED=true`
4. Run smoke tests
5. Monitor for 48 hours (logs, errors, performance)

**Success Criteria:**
- ✓ Zero errors in logs
- ✓ API response times < 200ms (95th percentile)
- ✓ Database writes confirmed in both JSON and DB

### 8.3 Production Environment Rollout

**Week 4: Production Deployment (Gradual)**

**Step 1: DB-Read Mode (Day 1-3)**
- Deploy with `FF_USE_DATABASE_STORAGE=true`
- Keep dual writes active for rollback safety
- Monitor error rates, response times
- Have rollback plan ready

**Step 2: Validate (Day 4-7)**
- Confirm all queries working correctly
- Check database performance metrics
- Verify no data consistency issues
- Review slow query logs

**Step 3: DB-Only Mode (Day 8+)**
- Disable dual writes: `FF_DUAL_WRITE_ENABLED=false`
- Archive JSON files (keep for 30 days)
- Remove JSON code (merge cleanup PR)
- Update production documentation

**Success Criteria:**
- ✓ Zero production incidents
- ✓ API response time maintained (< 200ms p95)
- ✓ Database queries optimized (no full table scans)
- ✓ Monitoring shows healthy database metrics

### 8.4 Communication Plan

**Stakeholders to Notify:**
- Development team
- QA/testers
- DevOps/platform team
- End users (if applicable)

**Communication Timeline:**
- **2 weeks before:** Migration announcement, timeline shared
- **1 week before:** Detailed technical plan shared
- **3 days before:** Final rollout schedule confirmed
- **Day of:** Status updates every 4 hours
- **Day after:** Retrospective and success metrics

---

## 9. Rollback Strategy

### 9.1 Rollback Scenarios

**Scenario 1: Database Connection Issues**
- **Trigger:** Cannot connect to database
- **Action:** Revert to JSON mode (`FF_USE_DATABASE_STORAGE=false`)
- **Recovery Time:** < 5 minutes

**Scenario 2: Data Integrity Issues**
- **Trigger:** Data corruption, lost records
- **Action:** Restore from backup, revert to JSON
- **Recovery Time:** < 30 minutes

**Scenario 3: Performance Degradation**
- **Trigger:** Response times > 500ms, timeouts
- **Action:** Optimize queries or revert to JSON temporarily
- **Recovery Time:** < 15 minutes (rollback) or hours (optimization)

### 9.2 Rollback Procedure

**Immediate Rollback (JSON Fallback):**
```bash
# 1. Set feature flag to disable database
export FF_USE_DATABASE_STORAGE=false

# 2. Restart application
# (Render: redeploy with updated env var)

# 3. Verify JSON mode active
curl https://your-api.com/api/v1/health

# 4. Restore JSON files if needed (from backup)
cp backup_data/*.json app/data/
```

**Database Restore (If Data Corrupted):**
```bash
# 1. Stop application (prevent new writes)

# 2. Restore from most recent backup
pg_restore --clean --dbname=$DATABASE_URL backup_TIMESTAMP.dump

# 3. Verify restoration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM expenses;"

# 4. Restart application
```

### 9.3 Rollback Decision Tree

```
Production issue detected?
│
├─► Database connection failed?
│   └─► YES → Enable JSON fallback immediately
│
├─► Data corruption/loss detected?
│   └─► YES → Restore from backup + enable JSON fallback
│
├─► Performance degradation?
│   ├─► Queries slow (> 500ms)?
│   │   └─► Optimize queries OR enable JSON fallback temporarily
│   └─► Connection pool exhausted?
│       └─► Increase pool size OR enable JSON fallback
│
└─► Minor issues (errors, edge cases)?
    └─► Fix forward (hot fix) OR rollback to previous deployment
```

### 9.4 Preserving JSON Files (Safety Net)

**During Transition:**
- Keep JSON files updated during dual-write phase
- Archive JSON files after successful migration (30-day retention)
- Store backup copy in cloud storage (S3, GCS)

**JSON File Backup:**
```bash
# Before deploying DB-only mode, backup JSON files
tar -czf json_backup_$(date +%Y%m%d).tar.gz app/data/*.json

# Upload to cloud storage
# aws s3 cp json_backup_20250107.tar.gz s3://bucket/backups/
```

---

## 10. Open Questions & Recommendations

### 10.1 Questions Requiring Input

**Q1: Data Migration from JSON to Database**

**Question:** The issue states "no need for data migration plan" since the project is in PoC stage. Should we:
- A) Start with empty database (users re-enter data)
- B) Provide optional migration script (one-time import of JSON to DB)
- C) Keep dual-read mode (fallback to JSON for historical data)

**Recommendation:** **Option B** - Provide optional migration script. Even for PoC, preserving existing test data is valuable for:
- Continuity during development
- Testing with realistic data
- Demo purposes

**Implementation:**
```bash
# Optional script: scripts/migrate_json_to_db.py
python scripts/migrate_json_to_db.py --source app/data/expenses.json --table expenses
```

---

**Q2: Connection Pool Size & Concurrency**

**Question:** What are the expected concurrent users and request volumes?

**Current Configuration:**
```python
# app/core/database.py
POOL_SIZE = 5  # Default in .env.example
```

**Recommendation:**
- **Development:** 5 connections (current)
- **Staging:** 10 connections
- **Production:** Start with 20, monitor and adjust

**Rationale:** PostgreSQL hosting platforms typically have connection limits on free/starter tiers (verify current limits in platform documentation). Start conservative, scale based on metrics.

---

**Q3: Backup & Disaster Recovery**

**Question:** What is acceptable data loss window (RPO) and recovery time (RTO)?

**Recommendation:**
- **RPO (Recovery Point Objective):** 24 hours (daily backups)
- **RTO (Recovery Time Objective):** 1 hour (time to restore from backup)

**Implementation:**
- Use platform-native backups (Render: included in free tier)
- Supplement with weekly manual backups to cloud storage
- Test restore procedure monthly

---

**Q4: Multi-User Support & Authentication**

**Question:** Is user authentication required in this milestone?

**Recommendation:** **No** - Keep single-tenant for this milestone. Add user authentication in a future milestone.

**Rationale:**
- Reduces scope and complexity
- Focus on storage layer transition
- Authentication is independent concern

**Future Implementation:**
```sql
-- Future: Add user_id to expenses/incomes
ALTER TABLE expenses ADD COLUMN user_id INTEGER REFERENCES users(id);
```

---

**Q5: Index Strategy**

**Question:** Which queries should be optimized with indexes?

**Recommendation:** Start with these indexes:

```sql
-- Expenses
CREATE INDEX idx_expenses_date ON expenses(date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_expenses_account ON expenses(account);

-- Incomes
CREATE INDEX idx_incomes_date ON incomes(date);
CREATE INDEX idx_incomes_category ON incomes(category);
CREATE INDEX idx_incomes_account ON incomes(account);

-- Composite index for common queries
CREATE INDEX idx_expenses_date_category ON expenses(date, category);
```

**Add in Alembic Migration:**
```python
# migrations/versions/add_performance_indexes.py
def upgrade():
    op.create_index('idx_expenses_date', 'expenses', ['date'])
    op.create_index('idx_expenses_category', 'expenses', ['category'])
    # ... etc
```

---

**Q6: Error Handling & Logging**

**Question:** What level of error logging and monitoring is needed?

**Recommendation:**

1. **Structured Logging:**
```python
import logging
logger = logging.getLogger(__name__)

# In repository operations
logger.info("Creating expense", extra={"amount": expense.amount, "category": expense.category})
logger.error("Failed to create expense", extra={"error": str(e)}, exc_info=True)
```

2. **Database Query Logging (Development Only):**
```python
# In development, log slow queries
engine = create_engine(DATABASE_URL, echo=True)  # SQLAlchemy query logging
```

3. **Production Monitoring (Sentry):**
```python
# Add Sentry integration in app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% performance monitoring
)
```

---

**Q7: Testing Data Seeding**

**Question:** How should test data be seeded in different environments?

**Recommendation:**

**Development:**
```bash
# Use existing seed script
python scripts/seed_smoke.py
```

**Staging:**
```bash
# Use fixtures with realistic volumes
python scripts/seed_test_data.py --count=1000
```

**Production:**
- No automatic seeding
- Users create their own data
- Optional: import from previous JSON files (migration script)

---

**Q8: Database Naming Conventions**

**Question:** Should table/column names follow snake_case or camelCase?

**Recommendation:** **snake_case** (already implemented)

**Rationale:**
- Standard PostgreSQL convention
- Already used in existing migrations
- Better compatibility with SQL tools

---

**Q9: API Response Format Changes**

**Question:** Should API response format change when switching from JSON to DB?

**Recommendation:** **No** - Keep API contract identical

**Implementation:**
```python
def expense_to_dict(expense: Expense) -> dict:
    """Convert SQLAlchemy model to dict matching JSON format."""
    return {
        "id": expense.id,
        "date": expense.date.isoformat(),  # Convert date to string
        "business": expense.business,
        "category": expense.category,
        "amount": float(expense.amount),    # Convert Decimal to float
        "account": expense.account,
        "currency": expense.currency,
        "notes": expense.notes,
    }
```

**Rationale:**
- Frontend doesn't need to change
- Tests don't need to change
- Backward compatibility maintained

---

**Q10: Feature Flag Management**

**Question:** Should feature flags be stored in environment variables or database?

**Recommendation:** **Hybrid approach** (already implemented)

**Strategy:**
1. **Global flags:** Environment variables (deployment-level control)
   - `FF_USE_DATABASE_STORAGE`
   - `FF_DUAL_WRITE_ENABLED`

2. **Per-user flags:** Database (gradual rollout)
   - Future: Beta features for specific users

**Current Implementation:**
- Feature flag resolution order: Env vars → Database → Default
- Already implemented in `app/core/feature_flags.py`

---

### 10.2 Best Practices Recommendations

**1. Migration Testing**
- Always test migrations on a copy of production data
- Use `alembic upgrade --sql` to preview changes
- Have rollback plan before running migration

**2. Connection Pool Management**
```python
# Recommended settings
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # Max connections
    max_overflow=10,           # Extra connections if pool full
    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle connections every hour
)
```

**3. Query Optimization**
- Use `select_related` for joins (SQLAlchemy 2.0 style)
- Add indexes for filtered columns (date, category)
- Monitor slow query log (queries > 1 second)

**4. Security**
- Use parameterized queries (SQLAlchemy does this by default)
- Never construct SQL from user input
- Validate and sanitize all inputs

**5. Transaction Management**
```python
# Use context manager for transactions
with db.begin():
    # Multiple operations in one transaction
    expense1 = repo.create(...)
    expense2 = repo.create(...)
    # Auto-commit if successful, auto-rollback if error
```

**6. Health Checks**
```python
# Add database health check endpoint
@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple query to verify DB connection
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

---

## 11. Success Criteria

### 11.1 Technical Success Metrics

**Database Migration:**
- ✓ All tables created successfully via Alembic
- ✓ All migrations run without errors
- ✓ Database schema matches ORM models exactly
- ✓ No manual schema changes required

**Application Functionality:**
- ✓ All API endpoints work with database storage
- ✓ API response format unchanged (backward compatible)
- ✓ All existing tests pass with database enabled
- ✓ No regressions in feature behavior

**Performance:**
- ✓ API response time < 200ms (95th percentile)
- ✓ Database queries < 100ms (95th percentile)
- ✓ Connection pool utilization < 80%
- ✓ No database connection timeouts

**Reliability:**
- ✓ Zero data loss during transition
- ✓ Zero production incidents during rollout
- ✓ Transaction rollback works correctly on errors
- ✓ Concurrent requests handled without race conditions

**Code Quality:**
- ✓ Test coverage > 85%
- ✓ No linting errors (black, isort)
- ✓ Type hints on all new code
- ✓ Documentation updated

### 11.2 Operational Success Metrics

**Monitoring:**
- ✓ Database monitoring dashboard operational
- ✓ Error tracking configured (Sentry)
- ✓ Uptime monitoring configured (UptimeRobot)
- ✓ Alerts configured for critical issues

**Backup & Recovery:**
- ✓ Automated daily backups configured
- ✓ Backup restoration tested successfully
- ✓ Recovery procedure documented
- ✓ Rollback procedure tested

**Documentation:**
- ✓ Migration runbook complete and tested
- ✓ Developer setup guide updated
- ✓ Deployment guide updated
- ✓ API documentation reflects new behavior

### 11.3 Business Success Metrics

**User Impact:**
- ✓ No user-facing downtime during migration
- ✓ No data loss reported by users
- ✓ Application performance maintained or improved
- ✓ No increase in error rates

**Development Velocity:**
- ✓ Developers can work with database locally
- ✓ CI/CD pipeline includes database tests
- ✓ Feature development continues uninterrupted
- ✓ Faster iteration on new features (proper persistence)

---

## 12. Timeline & Dependencies

### 12.1 Estimated Timeline

| Phase | Duration | Tasks | Dependencies |
|-------|----------|-------|--------------|
| **Phase 1:** Repository Layer | 1 week | Build repository classes, unit tests | SQLAlchemy models (✓ exists) |
| **Phase 2:** Dual Write | 1 week | Update routers, service layer, integration tests | Phase 1 complete |
| **Phase 3:** DB Read | 1 week | Switch reads to DB, performance testing, monitoring | Phase 2 stable |
| **Phase 4:** DB Only | 3 days | Remove JSON code, cleanup, final validation | Phase 3 validated |
| **Phase 5:** Production | 1 week | Staging deploy, production deploy, monitoring | All phases complete |

**Total Estimated Time:** 4-5 weeks (calendar time, with buffer for testing and validation)

### 12.2 Dependencies

**Infrastructure:**
- ✅ PostgreSQL database (development: Docker Compose)
- ✅ PostgreSQL database (production: Render or hosting platform)
- ⏳ Monitoring tools (Sentry, UptimeRobot, Grafana - setup required)

**Code:**
- ✅ SQLAlchemy models defined
- ✅ Alembic migrations setup
- ✅ Feature flag system
- ⏳ Repository layer (to be built)
- ⏳ Updated routers (to be modified)

**Testing:**
- ✅ Test infrastructure (pytest)
- ✅ Smoke tests
- ⏳ Database fixtures (to be added)
- ⏳ Integration tests with DB (to be added)

**Documentation:**
- ✅ Migration guidelines
- ✅ Schema guidelines
- ✅ Migration runbook
- ⏳ This milestone document (current)
- ⏳ Updated README (to be updated)

### 12.3 Critical Path

The critical path (longest sequence of dependent tasks):

1. **Repository Layer** (1 week) → 
2. **Dual Write Mode** (1 week) → 
3. **DB Read Mode** (1 week) → 
4. **DB Only Mode** (3 days) → 
5. **Production Deployment** (1 week)

**Parallelizable Tasks:**
- Monitoring setup (can happen anytime before Phase 5)
- Documentation updates (can happen alongside development)
- CI/CD updates (can happen alongside development)

### 12.4 Risk Mitigation

**Risk:** Development takes longer than estimated
- **Mitigation:** Build in 20% buffer time, prioritize core functionality

**Risk:** Production issues during rollout
- **Mitigation:** Phased rollout with feature flags, rollback plan tested

**Risk:** Performance issues with database
- **Mitigation:** Performance testing in Phase 3, query optimization

**Risk:** Data loss during transition
- **Mitigation:** Dual-write phase, backups before deployment

---

## 13. Related Documentation

This milestone document references and complements:

- [DB Migration Guidelines](../../backend/db_migration_guidelines.md) - Engineering principles and PR template
- [DB Schema Guidelines](../../backend/db_schema_guidelines.md) - Schema evolution rules
- [Alembic Conventions](../../backend/alembic_conventions.md) - Migration naming and standards
- [Migration Runbook](../migration-runbook.md) - Operational procedures for migrations
- [Migration PR Template](../../.github/PULL_REQUEST_TEMPLATE/migration_pr_template.md) - PR checklist
- [Feature Flags Documentation](../feature-flags.md) - Feature flag usage guide
- [Smoke Tests Documentation](../smoke-tests.md) - Testing procedures

---

## 14. Appendix

### 14.1 Glossary

- **PoC (Proof of Concept):** Early-stage project to validate feasibility
- **CRUD:** Create, Read, Update, Delete operations
- **ORM (Object-Relational Mapping):** SQLAlchemy's pattern for database access
- **Feature Flag:** Toggle to enable/disable features without code deployment
- **Dual Write:** Writing data to both old and new storage systems
- **Repository Pattern:** Abstraction layer between business logic and data access
- **Migration:** Database schema change script managed by Alembic
- **Rollback:** Reverting to previous state (code deployment or database schema)

### 14.2 Quick Reference Commands

**Database Management:**
```bash
# Start local PostgreSQL
docker-compose -f docker-compose-postgres.yaml up -d

# Run migrations
cd backend && alembic upgrade head

# Create migration
alembic revision --autogenerate -m "description"

# Check migration status
alembic current

# Rollback one migration
alembic downgrade -1
```

**Testing:**
```bash
# Run all tests
cd backend && pytest

# Run with database
export FF_USE_DATABASE_STORAGE=true && pytest

# Run smoke tests
pytest -m smoke
```

**Feature Flags:**
```bash
# JSON only (Phase 1)
export FF_USE_DATABASE_STORAGE=false

# Dual write (Phase 2)
export FF_DUAL_WRITE_ENABLED=true

# DB read (Phase 3)
export FF_USE_DATABASE_STORAGE=true

# DB only (Phase 4+)
export FF_USE_DATABASE_STORAGE=true
export FF_DUAL_WRITE_ENABLED=false
```

---

**Document Version:** 1.0  
**Last Updated:** 2024-12-07  
**Owner:** @zeevbensender  
**Status:** Ready for Review

---

## Approval & Sign-off

- [ ] Technical Review: @zeevbensender
- [ ] Architecture Review: @zeevbensender
- [ ] Security Review: @zeevbensender (CodeQL checks)
- [ ] Operations Review: @zeevbensender

**Approved for Implementation:** _______________ (Date)
