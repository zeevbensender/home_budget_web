"""
Storage module - DEPRECATED (Phase 5 cleanup).

This module has been removed as part of the Phase 5 PostgreSQL migration.
JSON storage is no longer used. All data is stored in PostgreSQL.

If you see this error, update your code to use the repository layer instead.
"""


def load_json(filename, default):
    """Deprecated - JSON storage removed in Phase 5.
    
    Raises:
        RuntimeError: Always raised - JSON storage is no longer supported
    """
    raise RuntimeError(
        "JSON storage has been removed in Phase 5. "
        "Use the repository layer (ExpenseRepository/IncomeRepository) instead. "
        f"Attempted to load: {filename}"
    )


def save_json(filename, data):
    """Deprecated - JSON storage removed in Phase 5.
    
    Raises:
        RuntimeError: Always raised - JSON storage is no longer supported
    """
    raise RuntimeError(
        "JSON storage has been removed in Phase 5. "
        "Use the repository layer (ExpenseRepository/IncomeRepository) instead. "
        f"Attempted to save: {filename}"
    )

