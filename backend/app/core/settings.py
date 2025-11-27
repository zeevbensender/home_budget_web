import os

DEFAULT_CURRENCY = "₪"  # Use ILS by default (you can change later)

# Storage type: "json" or "postgres"
# Default to "json" for testing, set STORAGE_TYPE=postgres for production
STORAGE_TYPE = os.getenv("STORAGE_TYPE", "json")


def get_default_currency():
    return DEFAULT_CURRENCY


def get_storage_type():
    return STORAGE_TYPE