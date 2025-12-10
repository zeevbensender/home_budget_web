# JSON to PostgreSQL Transition Plan

## Overview
This document outlines the phased transition from JSON file storage to PostgreSQL database persistence for the Home Budget Web application. The transition follows a safe, incremental approach with feature flags to enable rollback at any point.

## Architecture Principles
1. **Repository Pattern**: Centralize data access logic in dedicated repository classes
2. **Service Layer**: Business logic sits between routers and repositories
3. **Feature Flags**: Control rollout phases via environment variables and database settings
4. **Dual-Write Mode**: Write to both JSON and PostgreSQL during transition for safety
5. **Minimal Disruption**: Keep API contracts stable, changes are internal only

## Phased Transition Plan

### Phase 1: Repository Layer (Week 1)
**Status**: ✅ Complete

**Objective**: Create data access layer with repository pattern

**Deliverables**:
- `BaseRepository` abstract class with generic CRUD operations
  - `create(data)` - Create new record
  - `get(id)` - Get single record by ID
  - `list(filters, pagination)` - List records with optional filtering
  - `update(id, data)` - Update existing record
  - `delete(id)` - Delete single record
  - `bulk_delete(ids)` - Delete multiple records
  - `count(filters)` - Count records
  - `exists(id)` - Check if record exists
- `ExpenseRepository` implementing BaseRepository for expenses table
- `IncomeRepository` implementing BaseRepository for incomes table
- Repository unit tests using SQLite in-memory database
- Test fixtures in `tests/repositories/conftest.py`

**Acceptance Criteria**:
- All repository tests pass with 100% code coverage
- Repositories can perform CRUD operations on PostgreSQL
- Test suite runs in isolation without affecting production data

**Feature Flags**: None required (repositories not used by application yet)

---

### Phase 2: Service Layer Integration (Week 2)
**Status**: ✅ Complete

**Objective**: Create service layer that uses repositories, but still reads from JSON

**Deliverables**:
- `ExpenseService` class with business logic methods
  - `get_expense_list()` - Get all expenses (from JSON for now)
  - `create_expense(data)` - Create expense (JSON only)
  - `update_expense(id, data)` - Update expense (JSON only)
  - `delete_expense(id)` - Delete expense (JSON only)
  - `bulk_delete_expenses(ids)` - Bulk delete (JSON only)
- `IncomeService` class with business logic methods (similar to ExpenseService)
- Update routers to use services instead of direct storage calls
- Service layer tests

**Acceptance Criteria**:
- All existing API tests continue to pass
- API behavior unchanged (still using JSON storage)
- Services are dependency-injectable with proper abstractions
- Test coverage maintained at 85%+

**Feature Flags**: None required (services use JSON storage at this phase)

---

### Phase 3: Dual-Write Mode (Week 3)
**Status**: ✅ Complete

**Objective**: Write to both JSON and PostgreSQL, still read from JSON

**Deliverables**:
- Feature flag: `USE_DATABASE_STORAGE` (default: False)
- Feature flag: `DUAL_WRITE_ENABLED` (default: False)
- Update services to write to both JSON and PostgreSQL when `DUAL_WRITE_ENABLED=true`
- Keep reading from JSON for consistency
- Add monitoring/logging for write operations
- Dual-write tests validating both stores are updated

**Implementation Details**:
```python
class ExpenseService:
    def create_expense(self, data):
        # Write to JSON (primary)
        json_result = self._create_in_json(data)
        
        # Also write to PostgreSQL if dual-write enabled
        if is_feature_enabled("DUAL_WRITE_ENABLED"):
            try:
                self.repository.create(data)
            except Exception as e:
                logger.warning(f"Dual-write to DB failed: {e}")
        
        return json_result  # Always return JSON result
```

**Acceptance Criteria**:
- When `DUAL_WRITE_ENABLED=false`: behavior unchanged (JSON only)
- When `DUAL_WRITE_ENABLED=true`: writes go to both stores
- Reads still come from JSON (authoritative source)
- Database write failures don't break API responses
- All tests pass with both flag settings

**Feature Flags**:
- `FF_DUAL_WRITE_ENABLED`: Enable dual-write mode (default: False)

---

### Phase 4: Read from Database (Week 4)
**Status**: ✅ Complete

**Objective**: Switch reads to PostgreSQL while keeping dual-write for safety

**Deliverables**:
- Update services to read from PostgreSQL when `USE_DATABASE_STORAGE=true`
- Keep dual-write enabled for rollback safety
- Migration script to import existing JSON data into PostgreSQL
- Data validation comparing JSON vs DB records

**Implementation Details**:
```python
class ExpenseService:
    def get_expense_list(self):
        if is_feature_enabled("USE_DATABASE_STORAGE"):
            # Read from PostgreSQL (new path)
            return self.repository.list()
        else:
            # Read from JSON (fallback)
            return self._list_from_json()
    
    def create_expense(self, data):
        if is_feature_enabled("USE_DATABASE_STORAGE"):
            # Write to DB (primary)
            db_result = self.repository.create(data)
            
            # Also write to JSON if dual-write enabled
            if is_feature_enabled("DUAL_WRITE_ENABLED"):
                try:
                    self._create_in_json(data)
                except Exception as e:
                    logger.warning(f"Dual-write to JSON failed: {e}")
            
            return db_result
        else:
            # JSON-only path (fallback)
            return self._create_in_json(data)
```

**Acceptance Criteria**:
- When `USE_DATABASE_STORAGE=false`: reads from JSON (rollback path)
- When `USE_DATABASE_STORAGE=true`: reads from PostgreSQL
- Dual-write keeps both stores in sync
- Performance meets or exceeds JSON baseline
- All data migrated successfully from JSON to PostgreSQL

**Feature Flags**:
- `FF_USE_DATABASE_STORAGE`: Read from PostgreSQL instead of JSON (default: False)
- `FF_DUAL_WRITE_ENABLED`: Keep writing to both stores (default: True in this phase)

---

### Phase 5: Full Database Mode (Week 5+)
**Status**: ✅ Complete (with rollback safety)

**Objective**: Production-ready PostgreSQL mode with optional dual-write

**Deliverables**:
- ✅ Set `USE_DATABASE_STORAGE=true` as default
- ✅ Configure `DUAL_WRITE_ENABLED=false` for production (optional, can keep enabled for safety)
- ✅ Update documentation with Phase 5 deployment guide
- ✅ Add Phase 5 test scenarios
- ⏸️ Optional future cleanup: Remove JSON storage code (kept for rollback safety)
- ⏸️ Optional future cleanup: Remove `app/core/storage.py` (kept for rollback safety)
- ⏸️ Optional future cleanup: Clean up feature flags from codebase (kept for operational flexibility)

**Acceptance Criteria**:
- ✅ PostgreSQL is the default primary storage
- ✅ Dual-write can be disabled for production use
- ✅ Rollback capabilities maintained via feature flags
- ✅ Performance validated with dual-write disabled
- ✅ Documentation updated with deployment guide
- ✅ Tests cover Phase 5 scenarios

**Feature Flags**: 
- `FF_USE_DATABASE_STORAGE`: Default true (PostgreSQL primary)
- `FF_DUAL_WRITE_ENABLED`: Default false (can enable for safety), kept for rollback
- Feature flags maintained for operational flexibility and emergency rollback

---

## Feature Flag Configuration

### Environment Variables
```bash
# Phase 3: Enable dual-write (writes to both JSON and PostgreSQL)
FF_DUAL_WRITE_ENABLED=true

# Phase 4: Enable database reads (reads from PostgreSQL)
FF_USE_DATABASE_STORAGE=true
```

### Database Configuration
See `docs/feature-flags.md` for database-based flag management.

---

## Testing Strategy

### Unit Tests
- Repository tests with SQLite in-memory database
- Service tests with mocked repositories
- Router tests with mocked services
- Feature flag tests for all combinations

### Integration Tests
- End-to-end API tests with PostgreSQL testcontainer
- Dual-write validation tests
- Data migration validation tests

### Performance Tests
- Benchmark JSON vs PostgreSQL read/write operations
- Load testing with concurrent requests
- Query performance testing

### Test Coverage Requirements
- Maintain 85%+ code coverage
- All critical paths tested with both feature flag states
- Edge cases: DB failures, connection errors, data inconsistencies

---

## Rollback Procedures

### Phase 3 Rollback (Dual-Write Issues)
```bash
# Disable dual-write, revert to JSON-only
FF_DUAL_WRITE_ENABLED=false
```
No data loss - JSON remains authoritative source.

### Phase 4 Rollback (Database Read Issues)
```bash
# Revert to reading from JSON
FF_USE_DATABASE_STORAGE=false
```
Data still synced via dual-write, can switch back seamlessly.

### Emergency Rollback (Any Phase)
```bash
# Disable all database features
FF_USE_DATABASE_STORAGE=false
FF_DUAL_WRITE_ENABLED=false
```
System reverts to pure JSON mode immediately.

---

## Success Metrics

### Phase 1 (Repository Layer)
- ✅ 100% repository test coverage
- ✅ All CRUD operations functional
- ✅ Test suite execution time < 2 seconds

### Phase 2 (Service Integration)
- ✅ All existing tests still pass
- ✅ Zero API behavior changes
- ✅ Test coverage ≥ 85%

### Phase 3 (Dual-Write)
- ✅ Both stores updated on writes
- ✅ No increase in API response times
- ✅ Database write errors don't break API

### Phase 4 (Read from Database)
- ✅ Query performance better than JSON
- ✅ All data migrated successfully
- ✅ Zero data inconsistencies

### Phase 5 (Full Database Mode)
- ✅ JSON code removed
- ✅ Feature flags cleaned up
- ✅ Production stability for 2+ weeks

---

## Repository Structure

```
backend/
├── app/
│   ├── repositories/          # Phase 1
│   │   ├── __init__.py
│   │   ├── base_repository.py      # Abstract base class
│   │   ├── expense_repository.py   # Expense data access
│   │   └── income_repository.py    # Income data access
│   ├── services/              # Phase 2
│   │   ├── __init__.py
│   │   ├── expense_service.py      # Expense business logic
│   │   └── income_service.py       # Income business logic
│   ├── routers/               # Updated in Phase 2
│   │   ├── expense_router.py       # Uses ExpenseService
│   │   └── income_router.py        # Uses IncomeService
│   └── core/
│       ├── storage.py              # Removed in Phase 5
│       └── feature_flags.py        # Used in Phases 3-4
└── tests/
    ├── repositories/          # Phase 1 tests
    │   ├── conftest.py             # SQLite fixtures
    │   ├── test_expense_repository.py
    │   └── test_income_repository.py
    ├── services/              # Phase 2 tests
    │   ├── test_expense_service.py
    │   └── test_income_service.py
    └── integration/           # Phase 3-4 tests
        ├── test_dual_write.py
        └── test_data_migration.py
```

---

## Dependencies

### Required Packages (Already Installed)
- `sqlalchemy>=2.0` - ORM and query builder
- `psycopg2-binary>=2.9` - PostgreSQL adapter
- `alembic>=1.13` - Database migrations
- `pytest>=8.3` - Testing framework

### Database Requirements
- PostgreSQL 14+ (production)
- SQLite (tests only)

---

## Timeline Summary

| Phase | Duration | Feature Flags | Risk Level |
|-------|----------|---------------|------------|
| Phase 1: Repository Layer | Week 1 | None | Low |
| Phase 2: Service Integration | Week 2 | None | Low |
| Phase 3: Dual-Write | Week 3 | DUAL_WRITE_ENABLED | Medium |
| Phase 4: Read from DB | Week 4 | USE_DATABASE_STORAGE | Medium |
| Phase 5: Full DB Mode | Week 5+ | All removed | Low |

**Total estimated duration**: 5-6 weeks

---

## Related Documentation
- [Feature Flags Guide](../feature-flags.md)
- [Migration Runbook](../migration-runbook.md)
- [Database Migration Guidelines](../../backend/db_migration_guidelines.md)
- [Smoke Tests](../smoke-tests.md)

---

*Document Version: 1.0*  
*Last Updated: 2025-12-07*  
*Owner: @zeevbensender*
