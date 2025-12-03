"""
Feature flag helper module for phased rollouts.

This module provides a minimal feature-flag implementation that supports:
1. Environment variable-based flags (for global on/off toggles)
2. Optional database-based flags (for per-user or progressive rollouts)

Usage:
    from app.core.feature_flags import is_feature_enabled

    # Simple env-var check
    if is_feature_enabled("NEW_DASHBOARD"):
        # new code path
    else:
        # old code path

    # DB-based check with user context
    if is_feature_enabled("NEW_DASHBOARD", user_id=current_user.id, db=db):
        # new code path for specific user
"""

import os
from typing import Optional

from sqlalchemy.orm import Session


def get_flag_from_env(flag_name: str) -> Optional[bool]:
    """
    Check if a feature flag is set via environment variable.

    Environment variable naming convention: FF_{FLAG_NAME} = "true" | "false" | "1" | "0"

    Args:
        flag_name: The feature flag name (case-insensitive, will be uppercased)

    Returns:
        True if enabled, False if disabled, None if not set
    """
    env_key = f"FF_{flag_name.upper()}"
    env_value = os.getenv(env_key, "").lower()

    if env_value in ("true", "1", "yes", "on"):
        return True
    elif env_value in ("false", "0", "no", "off"):
        return False
    return None


def get_flag_from_db(
    flag_name: str,
    db: Session,
    user_id: Optional[int] = None,
) -> Optional[bool]:
    """
    Check if a feature flag is enabled in the database.

    This allows for per-user or percentage-based rollouts stored in DB.

    Args:
        flag_name: The feature flag name
        db: SQLAlchemy database session
        user_id: Optional user ID for per-user flag checks

    Returns:
        True if enabled, False if disabled, None if not found
    """
    # Import here to avoid circular imports
    from app.models.feature_flag import FeatureFlag

    try:
        # First check for user-specific flag if user_id is provided
        if user_id is not None:
            user_flag = (
                db.query(FeatureFlag)
                .filter(
                    FeatureFlag.name == flag_name,
                    FeatureFlag.user_id == user_id,
                )
                .first()
            )
            if user_flag is not None:
                return user_flag.enabled

        # Fall back to global flag (user_id is NULL)
        global_flag = (
            db.query(FeatureFlag)
            .filter(
                FeatureFlag.name == flag_name,
                FeatureFlag.user_id.is_(None),
            )
            .first()
        )
        if global_flag is not None:
            return global_flag.enabled

    except Exception:
        # If DB query fails (e.g., table doesn't exist yet), return None
        return None

    return None


def is_feature_enabled(
    flag_name: str,
    default: bool = False,
    user_id: Optional[int] = None,
    db: Optional[Session] = None,
) -> bool:
    """
    Check if a feature flag is enabled.

    Resolution order:
    1. Environment variable (FF_{FLAG_NAME}) - highest priority
    2. Database (if db session is provided) - user-specific, then global
    3. Default value - fallback

    Args:
        flag_name: The feature flag name
        default: Default value if flag is not found anywhere
        user_id: Optional user ID for per-user DB flag checks
        db: Optional SQLAlchemy database session for DB-based flags

    Returns:
        True if the feature is enabled, False otherwise

    Examples:
        # Simple env-var based flag
        if is_feature_enabled("NEW_EXPORT_FORMAT"):
            return export_v2()
        return export_v1()

        # DB-based flag with user context
        if is_feature_enabled("BETA_FEATURES", user_id=user.id, db=db):
            show_beta_ui()
    """
    # 1. Check environment variable first (highest priority)
    env_result = get_flag_from_env(flag_name)
    if env_result is not None:
        return env_result

    # 2. Check database if session is provided
    if db is not None:
        db_result = get_flag_from_db(flag_name, db, user_id)
        if db_result is not None:
            return db_result

    # 3. Return default
    return default
