# Feature Flags Guide

This document explains how to use feature flags in the Home Budget Web application for phased rollouts and controlled feature releases.

## Overview

Feature flags allow you to:
- Gradually roll out new features to users
- Quickly disable problematic features without deployments
- A/B test different implementations
- Enable features for specific users (beta testers)

## Implementation

The feature flag system supports two storage mechanisms:

### 1. Environment Variable Flags (Global)

For simple on/off toggles that apply globally, use environment variables:

```bash
# Enable a feature
FF_NEW_DASHBOARD=true

# Disable a feature
FF_NEW_DASHBOARD=false
```

**Naming convention:** `FF_{FLAG_NAME}` where `FLAG_NAME` is uppercase with underscores.

**Accepted values:** `true`, `1`, `yes`, `on` (enabled) or `false`, `0`, `no`, `off` (disabled)

### 2. Database Flags (Per-User or Global)

For per-user flags or more complex rollout strategies, use the `feature_flags` database table:

```sql
-- Global flag (applies to all users)
INSERT INTO feature_flags (name, enabled, description)
VALUES ('BETA_FEATURES', true, 'Enable beta features for all users');

-- Per-user flag (overrides global for specific user)
INSERT INTO feature_flags (name, enabled, user_id, description)
VALUES ('BETA_FEATURES', true, 42, 'Enable beta features for user 42');
```

## Usage in Code

### Basic Usage (Environment Variable Only)

```python
from app.core.feature_flags import is_feature_enabled

if is_feature_enabled("NEW_EXPORT_FORMAT"):
    return export_v2()
else:
    return export_v1()
```

### With Default Value

```python
# Returns True if flag is not set anywhere
if is_feature_enabled("EXPERIMENTAL_FEATURE", default=True):
    use_experimental()
```

### With Database (Per-User Flags)

```python
from app.core.feature_flags import is_feature_enabled
from app.core.database import get_db

def get_dashboard(user_id: int, db: Session):
    if is_feature_enabled("NEW_DASHBOARD", user_id=user_id, db=db):
        return new_dashboard()
    return old_dashboard()
```

## Resolution Order

When checking a flag, the system uses this priority:

1. **Environment variable** (`FF_{FLAG_NAME}`) - highest priority
2. **Database per-user flag** (if `user_id` provided)
3. **Database global flag** (where `user_id` is NULL)
4. **Default value** - lowest priority

This means environment variables can always override database settings, which is useful for emergency disables.

## Database Schema

The `feature_flags` table has the following structure:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(100) | Flag name (e.g., "NEW_DASHBOARD") |
| enabled | BOOLEAN | Whether the flag is enabled |
| user_id | INTEGER | Optional user ID (NULL for global flags) |
| description | TEXT | Optional description of the flag |

**Unique constraint:** One flag per `(name, user_id)` combination.

## Phased Rollout Example

Here's how to do a phased rollout of a new feature:

### Phase 1: Internal Testing
```sql
-- Enable for internal testers only
INSERT INTO feature_flags (name, enabled, user_id, description)
VALUES ('NEW_REPORTS', true, 1, 'Admin user testing');
```

### Phase 2: Beta Users (10%)
```sql
-- Enable for first 10 users
INSERT INTO feature_flags (name, enabled, user_id, description)
SELECT 'NEW_REPORTS', true, id, 'Beta rollout phase 2'
FROM users WHERE id <= 10;
```

### Phase 3: All Users
```sql
-- Enable globally
INSERT INTO feature_flags (name, enabled, description)
VALUES ('NEW_REPORTS', true, 'General availability');
```

### Phase 4: Remove Flag
Once the feature is stable, remove the flag from code and database.

## Emergency Disable

To immediately disable a feature across all users:

```bash
# Set environment variable (requires restart/redeploy)
FF_PROBLEMATIC_FEATURE=false
```

Or via database:
```sql
-- Update global flag
UPDATE feature_flags SET enabled = false WHERE name = 'PROBLEMATIC_FEATURE' AND user_id IS NULL;
```

## Best Practices

1. **Use descriptive flag names:** `EXPENSE_BULK_EXPORT_V2` is better than `FLAG_123`

2. **Document flags:** Always add a description when creating database flags

3. **Clean up old flags:** Remove flags from code and database once features are stable

4. **Default to disabled:** New features should default to `False` for safety

5. **Test both paths:** Ensure both enabled and disabled code paths are tested

6. **Monitor rollouts:** Watch error rates and performance when enabling new features

## Example Service Implementation

See `app/services/expense_service.py` for real examples of feature flag usage in the service layer.

## Migration

The feature flags table is created by migration `2a3b4c5d6e7f_add_feature_flags_table.py`.

Run migrations with:
```bash
# Using Makefile
make migrate

# Or directly
alembic upgrade head
```
