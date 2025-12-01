# Migration PR Template

Use this template for PRs that include Alembic migrations. Paste and fill out the sections below in the PR body.

## Title
(eg) Add category_id to expenses (db migration + service changes)

## Summary
- Brief description and rationale

## Files changed
- Alembic revision file(s)
- ORM models updated
- Service/repository changes

## Migration details
- Forward steps
- Downgrade steps (or note if not reversible)
- Data migration summary and idempotency notes
- Estimated runtime

## Backups & Pre-checks
- Backup plan (link or none)
- Local/staging run results (links)

## Rollout Plan (Phase N -> N+1 -> N+2)
- Phase 1: DB changes — target release
- Phase 2: Switch reads — target release
- Phase 3: Remove old field — target release

## Validation & Monitoring
- Post-migration SQL checks (copyable)
- Dashboards/alerts to watch

### Grafana Dashboard Links
<!-- Fill in the URLs to relevant Grafana dashboards for monitoring this migration -->
| Dashboard | URL |
|-----------|-----|
| Overview | `<GRAFANA_URL>/d/home-budget-overview` |
| API Performance | `<GRAFANA_URL>/d/home-budget-api` |
| Database Metrics | `<GRAFANA_URL>/d/home-budget-db` |

<!-- See docs/grafana-prometheus-integration.md for setup instructions -->

## Tests
- Unit/integration tests added
- CI links

## Approval
- DB reviewer: @zeevbensender and project assistant
- Service reviewer: @zeevbensender and project assistant
- Release manager: @zeevbensender and project assistant