# DB Schema Guidelines

**Project:** Home Budget Web  
**Backend:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL  
**Purpose:** Define stable, predictable rules for schema evolution and backward-compatible development.

---

## 1. General Principles

1. The database schema must always reflect **implemented features only**.  
2. No speculative or placeholder columns/tables are allowed.  
3. All schema changes must go through **Alembic migrations**.  
4. Schema must remain stable and backward-compatible during rolling deployments.

---

## 2. No Placeholders Policy

- Do not create “future fields”, “reserved columns”, or partially designed tables.  
- Do not add columns “just in case”.  
- Avoid NULL-heavy schemas caused by unused optional fields.

**Rationale:**  
Placeholders become technical debt, confuse developers, and rarely match final feature requirements.

---

## 3. Migration Workflow

1. Modify ORM models.  
2. Run `alembic revision --autogenerate`.  
3. Review the diff manually.  
4. Run migrations using `alembic upgrade head`.  
5. Update service and API layers accordingly.  
6. Add or modify tests.

**Never** rely on FastAPI/SQLAlchemy auto-create patterns in production.

---

## 4. Backward Compatibility Rules

### 4.1 Breaking changes are done in phases
If you need to rename, remove, or change a field:

**Phase 1 (Release N)**  
- Add the new field.  
- Keep the old field.  
- Write both fields if needed.  
- Read from the old field.

**Phase 2 (Release N+1)**  
- Switch read logic to the new field.  
- Mark the old field as deprecated.

**Phase 3 (Release N+2)**  
- Remove the old field via migration.

### 4.2 API versioning
- Existing routes under `/api/v1/` must remain stable.  
- Breaking API changes require `/api/v2/` routes.

---

## 5. Schema Change Types

### 5.1 Safe changes (single-step)
- Adding new nullable columns  
- Adding new tables  
- Adding indexes  
- Adding constraints that do not affect existing data

### 5.2 Risky changes (multi-step)
- Removing or renaming columns  
- Changing field types  
- Changing relations  
- Making a nullable field non-nullable  
- Dropping tables

These require multi-phase migrations.

---

## 6. Service Layer Isolation

Use the pattern:

```
routers → services → repositories → DB
```

The repository layer (SQLAlchemy) is the only place allowed to touch the DB schema directly.

This ensures:
- backward compatibility logic stays in one place  
- API contracts stay stable  
- future features can evolve without changing controller logic  

---

## 7. Data Migrations

When schema changes require updating existing records:

- Write data transformations inside the Alembic migration script.  
- Avoid production-only scripts.  
- Keep data migration logic pure and idempotent.

Examples:
- converting strings to enums  
- restructuring JSON fields  
- moving date fields to datetime fields  

---

## 8. Testing Requirements

Before merging any schema change:

- Run unit tests using SQLite (schema validation).  
- Run integration tests against temporary PostgreSQL (Docker).  
- Migrations must run cleanly against both an empty DB and an existing DB snapshot.

---

## 9. Deployment Policy

During deploys:
- Backend and frontend must remain compatible with both old and new schema versions for at least one release cycle.
- Zero-downtime deploys require fields to remain readable during schema transitions.

---

## 10. Documentation Requirements

Every migration must include:
- a short description (`alembic revision -m "Add category_id to expenses"`)  
- comments explaining decisions for non-trivial transitions  
- manual notes if the migration affects any existing API usage  

---

## 11. When to Create a New API Version

Create `/api/v2/...` instead of modifying v1 when:
- the response schema changes shape  
- required fields change  
- field semantics change  
- authentication/authorization model changes  

---

## 12. Summary

**YES:**  
✔ Schema reflects current features  
✔ Small, incremental migrations  
✔ Multi-phase migration for breaking changes  
✔ Backward compatibility for one release cycle  
✔ Clean isolation via service/repo layers  

**NO:**  
✘ Placeholder columns  
✘ “Reserved for future” fields  
✘ Auto-created schemas  
✘ Big-bang migrations  
✘ Breaking changes inside `/api/v1/`
