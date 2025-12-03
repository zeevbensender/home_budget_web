# DB Schema & Migration Guidelines (consolidated)

Project: Home Budget Web  
Backend: FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL  
Purpose: Single, practical guideline combining schema/principles and an actionable migration PR template.

---

## 1. Audience & Goals
This document is for developers, reviewers, and release managers working on schema changes. It codifies:
- Engineering principles for safe, backward-compatible schema evolution.
- A migration PR checklist to ensure migrations are reviewed, tested, and operationally safe.

Owners / Reviewers:
- DB reviewer: @zeevbensender and project assistant
- Service reviewer: @zeevbensender and project assistant
- Release manager: @zeevbensender and project assistant

---

## 2. High-level Principles
- Schema must reflect implemented features only — no speculative or placeholder columns/tables.
- All schema changes must go through Alembic migrations (no ad-hoc auto-creates in production).
- Prefer small, incremental migrations. Large “big-bang” migrations are high risk.
- Keep the system backward-compatible for at least one release cycle where possible.

Rationale: reduces technical debt, makes rollouts safer, and enables zero-downtime deploys.

---

## 3. No Placeholders Policy
- Do not add “reserved” or “future” columns.
- Avoid NULL-heavy designs that are placeholders for future features.
- If you must prepare for future changes, prefer multi-phase migrations + feature toggles.

---

## 4. Architecture & Ownership
Follow this layering:
routers → services → repositories → DB

Only the repository/ORM layer should touch the DB schema directly. Keep backward-compatibility toggling logic in the service layer.

---

## 5. Migration Workflow (developer checklist)
1. Modify ORM models in code.
2. Generate migration: `alembic revision --autogenerate -m "short description"`.
3. Review the generated diff manually — DO NOT rely solely on autogenerate.
4. Add any required data transformations into the Alembic script (idempotent).
5. Run migrations locally: `alembic upgrade head`.
6. Run unit tests and integration/smoke tests (see section 8).
7. Open a Migration PR using the PR template below.
8. Merge only after required approvals and passing CI.

Never rely on SQLAlchemy auto-create patterns in production.

---

## 6. Backward Compatibility & Multi-phase Changes
When changing/removing fields follow a phased approach:

Phase 1 (Release N)
- Add the new field and keep the old.
- Application writes to both if needed; read from the old field.

Phase 2 (Release N+1)
- Switch reading to the new field; mark old as deprecated.

Phase 3 (Release N+2)
- Remove the old field via migration.

API versioning: Breaking API changes => create `/api/v2/…`. Avoid breaking `/api/v1/`.

---

## 7. Data Migration Best Practices
- Prefer embedding pure, idempotent transformations inside Alembic scripts.
- Keep transformations testable and small; consider batching or background jobs for large datasets.
- Validate results with copyable SQL queries in the PR.

Examples: string→enum, JSON restructuring, date normalization.

---

## 8. Testing & CI (recommended minimal setup)
- Unit tests: run with SQLite for quick schema validation.
- Integration / Smoke tests: run against a temporary Postgres (Docker) in CI before merge.
- Migrations must run cleanly against:
  - an empty DB, and
  - a realistic DB snapshot (where practical).
- CI job suggestions (GitHub Actions):
  - lint (python/JS), unit-tests, type-check
  - migration-check (autogenerate diff sanity + `alembic upgrade --sql` dry-run)
  - **postgres-migration-check** (Postgres-based autogenerate for higher fidelity)
  - smoke-integration (optional, use a service container postgres)

Suggested job names: test, lint, migration-check, postgres-migration-check, smoke-test.

### 8.1 Postgres Migration Check (CI Job)

The `postgres-migration-check` workflow (`.github/workflows/postgres-migration-check.yml`) provides
higher-fidelity schema drift detection by running Alembic autogenerate against a real Postgres
database instead of SQLite.

**What it does:**
1. Starts a Postgres 15 service container in CI
2. Applies all existing migrations (`alembic upgrade head`)
3. Runs `alembic revision --autogenerate` to detect any uncommitted schema changes
4. Fails the build if new migration files are generated, with an actionable error message
5. Verifies that migration SQL can be generated (`alembic upgrade --sql`)

**Why Postgres instead of SQLite?**
- Postgres-specific types (e.g., `ARRAY`, `JSONB`, `UUID`) are not supported by SQLite
- Postgres constraints and indexes may behave differently
- Some column type changes are only detected correctly with Postgres
- Production uses Postgres, so CI should match production fidelity

**Limitations:**
- The autogenerate check may not detect all types of drift (e.g., certain constraint changes)
- Postgres-specific features like extensions must be enabled in the service container
- The check adds ~1-2 minutes to CI time due to Postgres startup

**Fallback:**
- If the Postgres-based check fails unexpectedly (e.g., service container issues), you can:
  1. Re-run the CI job (transient failures)
  2. Run the check locally: `DATABASE_URL=postgresql://... alembic revision --autogenerate -m "test"`
  3. Use the SQLite-based `migration-check.yml` as a fallback (lower fidelity)

**Local testing:**
```bash
# Start a local Postgres container
docker run -d --name test-postgres -e POSTGRES_USER=test_user \
  -e POSTGRES_PASSWORD=test_password -e POSTGRES_DB=test_db -p 5432:5432 postgres:15

# Run the autogenerate check
export DATABASE_URL=postgresql://test_user:test_password@localhost:5432/test_db
cd backend
poetry run alembic upgrade head
poetry run alembic revision --autogenerate -m "test-check"

# Clean up
docker stop test-postgres && docker rm test-postgres
```

---

## 9. Production Characteristics & Scaling (your stage)
- 1M expense+income rows is reasonable for this stage. With proper indexing and careful migrations it will run fine on a single managed Postgres instance.
- Plan for backups before migrations once you move beyond PoC.

---

## 10. Backups & Snapshots (current approach)
- You indicated no backups now and prefer manual export/import via JSON/CSV.
- Recommendation: start with periodic JSON/CSV exports (manual or scheduled) and, before any production migration, take a logical export (pg_dump) or a managed backup snapshot if platform supports it.

---

## 11. Monitoring & Alerts (recommendation)
For small/low-cost project:
- Error & exception tracking: Sentry (free tier) — easy to integrate with Python/FastAPI.
- Uptime checks: UptimeRobot (free) for endpoint health.
- Metrics: Grafana Cloud (free tier) for lightweight dashboards, or use Render metrics if available.
These give observability without heavy infra.

---

## 12. Release Cadence & Naming
Recommendation for your goals:
- Milestone-driven & pragmatic: release when a milestone is done (e.g., every 2–4 weeks or on-demand for portfolio/learning).
- Versioning: use semantic tags vMAJOR.MINOR.PATCH. For schema rollout phases, reference releases as "Release N" mapped to a tag (e.g., v0.3.0).

---

## 13. Branch & Protection Policies (best-practice)
- Protect `main` branch:
  - Require pull requests for merges.
  - Require status checks (CI) to pass before merge.
  - Require at least one approval (you can self-approve or add the assistant as reviewer).
  - Disable force pushes on `main`.
- Use feature/topic branches per-PR: `copilot/add-...` or `feat/<short-desc>`.

---

## 14. Feature Flags (lightweight approach)
Start simple:
- Global flags via environment variables for coarse-grained toggles.
- For per-user or progressive rollout, add a small `feature_flags` table and a helper in service layer to evaluate flags.
- If you need advanced rollout later, adopt Unleash OSS or a hosted service.

---

## 15. Alembic Naming & Conventions

> **📖 Full conventions guide:** See [alembic_conventions.md](alembic_conventions.md) for detailed naming rules, header templates, and commit message examples.

**Quick summary:**
- Migration revision message: concise slug e.g., `add_category_id_to_expenses`
- File naming: Alembic revision id + message: `abc123_add_category_id_to_expenses.py`
- Migration header should include: Author, Date, Purpose, and Estimated runtime
- Commit message format: `db: <action> <target>`

---

## 16. Migration PR Template (copy this into PR body)
Title:
(e.g.) Add category_id to expenses (db migration + service changes)

Summary:
- One-line description and rationale.

Files changed:
- Alembic revision file(s)
- ORM model files updated
- Service/repository files updated

Migration details:
- Forward migration steps
- Downgrade steps (or "not reversible")
- Data migration summary and idempotency notes
- Estimated runtime on production

Backups & Pre-checks:
- Backup/snapshot plan? (link or "none")
- Migration tested in staging / local run? (link/log)

Rollout plan (map to Phase 1/2/3):
- Phase 1: DB changes — target release
- Phase 2: Switch reads to new field — target release
- Phase 3: Remove old field — target release

Feature flags:
- Flag name and behavior (if applicable)

Validation & Monitoring:
- Post-migration validation SQL (copyable)
- Dashboards/alerts to watch

Performance considerations:
- Indexes added/changed and reason
- Impact on common queries

Rollback plan:
- Steps to rollback (if supported) & owner (@zeevbensender)

Tests:
- Unit/integration tests added (CI links)
- Manual validation performed (links/logs)

Approval:
- DB reviewer: @zeevbensender and project assistant
- Service reviewer: @zeevbensender and project assistant
- Release manager: @zeevbensender and project assistant

---

## 17. Operational Notes & Runbook Snippets
- Before running a migration that touches large tables:
  - Create an export or snapshot.
  - Run the migration on a copy with similar data sizes where possible.
  - Monitor locks and long-running queries during the rollout (Sentry/Uptime/Grafana).

---

## 18. Appendix: Example Alembic Header (add to top of revision)

> **📖 See [alembic_conventions.md](alembic_conventions.md) for complete header template and commit message examples.**

```python
"""add_category_id_to_expenses

Revision ID: abc123def456
Revises: 789ghi012jkl
Create Date: 2025-12-03 10:30:00.000000

# Author: zeevbensender
# Date: 2025-12-03
# Purpose: Add category_id column to expenses (backwards compatible, phase 1)
# Estimated runtime: < 1 second
"""
```

---

## 19. Summary
This single document:
- Preserves the strict engineering principles (no placeholders, phased breaking changes).
- Adds a pragmatic PR checklist and operational guidance tailored to your current deployment (Render, low-cost, single-owner).
- Recommends simple, low-cost monitoring and feature-flag patterns that are easy to migrate later.

---

If you'd like, I can:
- Commit this as `backend/db_migration_guidelines.md` in the repo. The migration PR template is at [`.github/PULL_REQUEST_TEMPLATE/migration_pr_template.md`](../.github/PULL_REQUEST_TEMPLATE/migration_pr_template.md).
- Produce a GitHub Actions migration-check workflow and a PR body template file ready to paste.

What I still need to finalize any automated snippets or CI workflows:
- If you want CI templates added: the Python environment and test command(s) you use (e.g., `poetry run pytest` or `pipenv run pytest`) and whether frontend tests should run in the same workflow.
- If you want monitoring links embedded: the Sentry/Grafana dashboard URLs (or confirmation to use the services I recommended).