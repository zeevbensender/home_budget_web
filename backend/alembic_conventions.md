# Alembic Naming & Commit Conventions

**Project:** Home Budget Web  
**Backend:** FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL  
**Purpose:** Standardize migration file naming, header comments, and commit messages.

---

## 1. Migration File Naming

Alembic generates migration files with the following format:

```
<revision_id>_<message_slug>.py
```

### 1.1 Message Slug Guidelines

- Use **lowercase** with **underscores** as word separators
- Keep it **concise** but descriptive (2-5 words)
- Use **verb + noun** format when possible
- Describe **what** the migration does, not why

**Good examples:**
- `add_category_id_to_expenses`
- `create_feature_flags_table`
- `remove_deprecated_status_column`
- `add_index_on_expenses_date`

**Bad examples:**
- `update` (too vague)
- `fix_issue_42` (references external issue, not descriptive)
- `Add_Category_ID_To_Expenses` (wrong case)
- `add-category-id` (uses hyphens instead of underscores)

### 1.2 Generating Migrations

```bash
# Standard migration generation
alembic revision --autogenerate -m "add_category_id_to_expenses"

# Manual migration (when autogenerate is not suitable)
alembic revision -m "migrate_legacy_status_values"
```

---

## 2. Migration File Header Template

Add metadata comments inside the existing Alembic-generated docstring (after the `Create Date` line) to provide context for reviewers and future developers. Do not replace the docstring — add the comment lines within it.

### 2.1 Standard Header Template

```python
"""add_category_id_to_expenses

Revision ID: abc123def456
Revises: 789ghi012jkl
Create Date: 2025-12-03 10:30:00.000000

# Author: your_github_username
# Date: 2025-12-03
# Purpose: Add category_id column to expenses table (phase 1 of category refactor)
# Estimated runtime: < 1 second (column add, no data migration)
"""
```

### 2.2 Header Fields

| Field | Required | Description |
|-------|----------|-------------|
| **Author** | Yes | GitHub username of the migration author |
| **Date** | Yes | Date the migration was created (YYYY-MM-DD) |
| **Purpose** | Yes | Brief description of what and why |
| **Estimated runtime** | Recommended | Expected execution time on production |
| **Phase** | If applicable | Reference to multi-phase migration (e.g., "phase 1 of 3") |
| **Breaking changes** | If applicable | Note any backward-incompatible changes |

### 2.3 Extended Header for Complex Migrations

For migrations involving data transformations or multi-phase changes:

```python
"""migrate_expense_categories_to_enum

Revision ID: abc123def456
Revises: 789ghi012jkl
Create Date: 2025-12-03 10:30:00.000000

# Author: zeevbensender
# Date: 2025-12-03
# Purpose: Convert category strings to enum values (phase 2 of category refactor)
# Estimated runtime: ~30 seconds (data migration on 100k rows)
# Phase: 2 of 3 (see migration plan in PR #42)
# Breaking changes: None (old column retained until phase 3)
# Rollback notes: Safe to rollback, enum values are preserved in old column
"""
```

---

## 3. Commit Message Conventions

### 3.1 Format

```
db: <action> <target> [additional context]
```

### 3.2 Examples

```bash
# Adding new schema elements
git commit -m "db: add category_id column to expenses table"
git commit -m "db: create feature_flags table"

# Modifying existing schema
git commit -m "db: add index on expenses(date, category)"
git commit -m "db: make notes column nullable in incomes"

# Data migrations
git commit -m "db: migrate legacy status values to enum"

# Multi-phase migrations
git commit -m "db: add new_category column (phase 1 of category refactor)"

# Removing schema elements
git commit -m "db: drop deprecated status column from expenses"
```

### 3.3 Commit Message Guidelines

- Start with `db:` prefix for all migration commits
- Use present tense ("add" not "added")
- Be specific about the table and column names
- Reference the phase if part of a multi-step migration
- Keep under 72 characters when possible

---

## 4. Quick Reference

### 4.1 Checklist for New Migrations

- [ ] Message slug is lowercase with underscores
- [ ] Header comment includes Author, Date, Purpose
- [ ] Estimated runtime noted for non-trivial migrations
- [ ] Commit message follows `db: <action> <target>` format
- [ ] Migration reviewed manually (not just autogenerate output)

### 4.2 Example: Complete Migration File

```python
"""add_category_id_to_expenses

Revision ID: abc123def456
Revises: 789ghi012jkl
Create Date: 2025-12-03 10:30:00.000000

# Author: zeevbensender
# Date: 2025-12-03
# Purpose: Add category_id column to expenses for FK relationship (phase 1)
# Estimated runtime: < 1 second
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, Sequence[str], None] = '789ghi012jkl'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add category_id column to expenses table."""
    op.add_column('expenses', sa.Column('category_id', sa.Integer(), nullable=True))
    op.create_index('ix_expenses_category_id', 'expenses', ['category_id'])


def downgrade() -> None:
    """Remove category_id column from expenses table."""
    op.drop_index('ix_expenses_category_id', table_name='expenses')
    op.drop_column('expenses', 'category_id')
```

---

## 5. Related Documentation

- [DB Migration Guidelines](db_migration_guidelines.md) — Full migration workflow and PR template
- [DB Schema Guidelines](db_schema_guidelines.md) — Schema evolution rules
- [Migration Runbook](../docs/migration-runbook.md) — Backup, rollback, and escalation procedures
- [Migration PR Template](../.github/PULL_REQUEST_TEMPLATE/migration_pr_template.md) — PR checklist

---

*Last updated: 2025-12-03*  
*Document owner: @zeevbensender*
