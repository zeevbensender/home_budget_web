# Migration PR Template

## Title
(eg) Add category_id to expenses (db migration + service changes)

## Summary
- Brief description of the schema change(s)
- A short rationale for the change

## Files changed
- List of Alembic revision file(s)
- ORM model files updated
- Service/repository files updated

## Migration details
- Forward migration steps (what the migration does)
- Downgrade steps (what the migration does on downgrade) — mark if not reversible
- Data migration summary (transformations performed)
- Expected migration runtime on production (approximate)

## Backups & Pre-checks
- Backup/snapshot plan completed? (yes/no + link)
- Migration run in staging with production-like data? (yes/no + link to logs)

## Rollout plan
- Phase 1: DB changes (migrate) — target release
- Phase 2: Switch reads to new field (app change) — target release
- Phase 3: Remove old field — target release

## Feature flags / toggles
- Feature flag name (if applicable)

## Validation & Monitoring
- Post-migration validation queries (copyable SQL)
- Monitoring dashboards and alerts to watch during and after rollout

## Performance considerations
- Indexes added/changed and reason
- Expected effect on common queries

## Rollback plan
- Steps to rollback (if supported)
- Who is the rollback owner (name / pager / github handle)

## Tests
- Unit / integration tests added and passing (links to CI)
- Manual validation performed (list and link to results)

## Approval
- Reviewers:
  - DB reviewer:
  - Service reviewer:
  - Release manager:
