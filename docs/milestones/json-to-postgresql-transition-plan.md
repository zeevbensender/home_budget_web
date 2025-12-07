# JSON to PostgreSQL Transition Plan

**Project:** Home Budget Web  
**Owner:** @zeevbensender  
**Status:** Phase 1 - In Progress  
**Last Updated:** 2025-12-07

## Overview

This document outlines the phased approach to transitioning the Home Budget Web application from JSON file storage to PostgreSQL database persistence. The transition follows a safe, incremental strategy using feature flags to enable rollback at any stage.

## Goals

1. **Zero Downtime**: Transition without service interruption
2. **Reversible**: Ability to rollback to JSON storage at any phase
3. **Testable**: Comprehensive test coverage at each phase
4. **Incremental**: Small, verifiable changes with clear checkpoints

## Architecture Principles

### Repository Pattern
All data access will be abstracted through repository classes:
- Separate data access from business logic
- Enable easy swapping between storage backends
- Facilitate testing with mock repositories

### Feature Flags
Control the transition using environment-based feature flags:
- `USE_DATABASE_STORAGE`: Enable PostgreSQL storage (default: `false`)
- `DUAL_WRITE_ENABLED`: Write to both JSON and PostgreSQL (default: `false`)

See [docs/feature-flags.md](../feature-flags.md) for usage details.

## Phased Transition Plan

### Phase 1: Infrastructure & Repository Layer (Week 1)

**Goal**: Create the foundation for database-backed storage without affecting current functionality.

#### Deliverables

1. **Base Repository Pattern**
   - Create `BaseRepository` abstract class with common CRUD operations
   - Define standard interfaces: `create()`, `get()`, `list()`, `update()`, `delete()`
   - Include transaction management support

2. **Expense Repository**
   - Implement `ExpenseRepository` extending `BaseRepository`
   - Full CRUD operations for expenses table
   - Bulk delete support
   - Comprehensive unit tests (SQLite in-memory)

3. **Income Repository**
   - Implement `IncomeRepository` extending `BaseRepository`
   - Full CRUD operations for incomes table
   - Bulk delete support
   - Comprehensive unit tests (SQLite in-memory)

4. **Testing Strategy**
   - Unit tests with SQLite in-memory database
   - Integration tests with PostgreSQL (docker-compose)
   - Maintain existing JSON-based API tests
   - Target: 85%+ test coverage

#### Code Structure

```
backend/app/
├── repositories/
│   ├── __init__.py
│   ├── base_repository.py      # Abstract base class
│   ├── expense_repository.py   # Expense CRUD operations
│   └── income_repository.py    # Income CRUD operations
└── tests/
    └── repositories/
        ├── test_expense_repository.py
        └── test_income_repository.py
```

#### Acceptance Criteria

- [ ] All repository classes implemented and tested
- [ ] Unit tests achieve 85%+ coverage
- [ ] Integration tests pass with PostgreSQL
- [ ] Existing JSON-based tests still pass (no regression)
- [ ] Code review completed
- [ ] Documentation updated

#### Exit Criteria

All tests passing, repository layer ready for integration in Phase 2.

---

### Phase 2: Service Layer Integration (Week 2)

**Goal**: Create service classes that can use either JSON or repository storage.

#### Deliverables

1. **Storage Abstraction**
   - Create `StorageBackend` interface
   - Implement `JsonStorageBackend`
   - Implement `DatabaseStorageBackend` using repositories

2. **Service Layer Updates**
   - Update expense service to use storage backend
   - Update income service to use storage backend
   - Feature flag integration: `USE_DATABASE_STORAGE`

3. **Testing**
   - Tests for both storage backends
   - Feature flag toggle tests
   - Data consistency validation

#### Exit Criteria

Services can switch between JSON and database storage via feature flag.

---

### Phase 3: Dual-Write Mode (Week 3)

**Goal**: Write to both JSON and PostgreSQL simultaneously for data validation.

#### Deliverables

1. **Dual-Write Implementation**
   - Enable `DUAL_WRITE_ENABLED` feature flag
   - Write to both backends on create/update/delete
   - Log any discrepancies

2. **Data Migration Tool**
   - Script to migrate existing JSON data to PostgreSQL
   - Validation of migrated data
   - Rollback capability

3. **Monitoring**
   - Log dual-write operations
   - Track success/failure rates
   - Alert on discrepancies

#### Exit Criteria

Data consistency verified between JSON and PostgreSQL for 48+ hours.

---

### Phase 4: Read from Database (Week 4)

**Goal**: Switch reads to PostgreSQL while maintaining dual-writes.

#### Deliverables

1. **Read Switchover**
   - Enable database reads via feature flag
   - Keep JSON writes active (safety net)
   - Performance monitoring

2. **Performance Validation**
   - Response time comparisons
   - Database query optimization
   - Index verification

3. **Rollback Testing**
   - Verify ability to switch back to JSON reads
   - Document rollback procedure

#### Exit Criteria

All reads from PostgreSQL, performance acceptable, rollback tested.

---

### Phase 5: Full Database Mode (Week 5)

**Goal**: Complete transition, remove JSON storage.

#### Deliverables

1. **Disable JSON Writes**
   - Stop writing to JSON files
   - Archive existing JSON data
   - Remove JSON storage code paths

2. **Cleanup**
   - Remove JSON-related code
   - Update documentation
   - Remove feature flags

3. **Final Validation**
   - Full regression test suite
   - Performance benchmarks
   - Load testing

#### Exit Criteria

Application runs entirely on PostgreSQL, JSON code removed.

---

## Testing Strategy

### Unit Tests
- **SQLite in-memory database** for fast unit tests
- Test each repository method independently
- Mock external dependencies
- Target: 85%+ coverage

### Integration Tests
- **PostgreSQL via docker-compose** for real database tests
- Test full service-to-database flow
- Verify transactions and rollbacks
- Test concurrent operations

### Smoke Tests
- End-to-end API tests
- Test all critical user flows
- Run against both JSON and database backends
- See [docs/smoke-tests.md](../smoke-tests.md)

### Performance Tests
- Benchmark CRUD operations
- Compare JSON vs PostgreSQL performance
- Monitor query performance
- Load testing with realistic data volumes

## Rollback Procedures

### Phase 1 Rollback
No rollback needed - repository layer not yet integrated.

### Phase 2-4 Rollback
1. Set `USE_DATABASE_STORAGE=false` in environment
2. Restart application
3. Verify JSON storage is active

### Phase 5 Rollback
Requires code deployment to previous version.

See [docs/migration-runbook.md](../migration-runbook.md) for detailed procedures.

## Risk Mitigation

### Data Loss Prevention
- Always maintain dual writes during transition
- Regular database backups before each phase
- Archive JSON data before cleanup

### Performance Risk
- Benchmark before each phase
- Monitor query performance
- Index optimization based on actual queries

### Rollback Risk
- Test rollback procedure at each phase
- Document rollback steps
- Keep previous phase code available

## Success Metrics

- **Zero Data Loss**: All data migrated successfully
- **Performance**: Database operations ≤ JSON operation latency
- **Test Coverage**: Maintain 85%+ throughout transition
- **Uptime**: No service interruptions during transition

## Documentation Updates

- [ ] Update README with database setup instructions
- [ ] Update development environment docs
- [ ] Create database backup procedures
- [ ] Update deployment documentation

## References

- [Database Migration Guidelines](../../backend/db_migration_guidelines.md)
- [Feature Flags Guide](../feature-flags.md)
- [Migration Runbook](../migration-runbook.md)
- [Smoke Tests](../smoke-tests.md)

---

*Last updated: 2025-12-07*  
*Phase 1 implementation by: GitHub Copilot Agent*
