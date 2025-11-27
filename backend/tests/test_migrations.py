"""
Test that migrations can be run in offline mode (SQL generation).
This validates the migration syntax without requiring a running database.
"""

import subprocess
import sys


def test_migration_generates_valid_sql():
    """Verify that the migration can generate SQL in offline mode."""
    result = subprocess.run(
        [
            sys.executable, "-m", "alembic", "upgrade", "head", "--sql"
        ],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/home_budget_web/home_budget_web/backend",
        env={
            "DATABASE_URL": "postgresql://budget:budget@localhost:5432/budget_db",
            "PATH": "/usr/bin",
        }
    )
    
    # Should complete without errors
    assert result.returncode == 0, f"Migration failed: {result.stderr}"
    
    # Should generate expected SQL statements
    output = result.stdout
    assert "CREATE TABLE expenses" in output
    assert "CREATE TABLE incomes" in output
    assert "PRIMARY KEY (id)" in output
    
    # Verify expected columns for expenses
    assert "date DATE NOT NULL" in output
    assert "business VARCHAR(255)" in output
    assert "category VARCHAR(100) NOT NULL" in output
    assert "amount NUMERIC(12, 2) NOT NULL" in output
    assert "account VARCHAR(100) NOT NULL" in output
    assert "currency VARCHAR(10) NOT NULL" in output
    assert "notes TEXT" in output


def test_migration_downgrade_generates_valid_sql():
    """Verify that the migration downgrade can generate SQL in offline mode."""
    result = subprocess.run(
        [
            sys.executable, "-m", "alembic", "downgrade", "cb740587175f:base", "--sql"
        ],
        capture_output=True,
        text=True,
        cwd="/home/runner/work/home_budget_web/home_budget_web/backend",
        env={
            "DATABASE_URL": "postgresql://budget:budget@localhost:5432/budget_db",
            "PATH": "/usr/bin",
        }
    )
    
    # Should complete without errors
    assert result.returncode == 0, f"Downgrade failed: {result.stderr}"
    
    # Should generate DROP TABLE statements
    output = result.stdout
    assert "DROP TABLE expenses" in output
    assert "DROP TABLE incomes" in output
