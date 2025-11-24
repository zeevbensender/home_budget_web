# Milestone 2 — Variant A Progress Checklist

## Goal
Stabilize existing UI + backend with automated tests and cleanup before database migration.

---

## 1. Testing

### 1.1 Backend API Tests
- [x] Healthcheck endpoint
- [x] Add expense
- [x] Edit expense
- [x] Delete expense
- [x] Bulk delete expenses
- [x] Add income
- [ ] Edit income
- [ ] Delete income
- [ ] Bulk delete incomes

### 1.2 Frontend Unit Tests
- [ ] Critical helper functions
- [ ] Add/edit/delete transaction logic (minimal)

### 1.3 Light E2E Tests
- [ ] Start backend and run smoke tests
- [ ] Validate add → edit → delete flow through UI/API

---

## 2. Dependency Cleanup
- [ ] Remove SQLAlchemy
- [ ] Remove psycopg2
- [ ] Remove Alembic
- [ ] Remove auth-related libs (jose, passlib, bcrypt)
- [ ] Update pyproject and requirements

---

## 3. Documentation
- [ ] Document backend JSON-mode storage architecture
- [ ] Document how to run backend tests
- [ ] Document how to run frontend tests
- [ ] Add test directory structure explanation

---

## 4. DB-Safe Architecture Constraints
- [ ] Tests do not reference JSON file paths
- [ ] Storage implementation stays fully swappable
- [ ] API contract defined and stable
- [ ] No reliance on internal storage logic in tests

---

## 5. Deliverables
- [ ] Complete test suite
- [ ] Clean dependency list
- [ ] Updated README
- [ ] No UI regressions
- [ ] API behavior unchanged
