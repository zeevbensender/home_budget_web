"""add_feature_flags_table

Revision ID: 2a3b4c5d6e7f
Revises: 877b61b7b538
Create Date: 2025-12-03

# Author: zeevbensender / copilot
# Purpose: Add feature_flags table for database-based feature toggles
# Estimated runtime: < 1 second (new table)
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a3b4c5d6e7f"
down_revision: Union[str, Sequence[str], None] = "877b61b7b538"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create feature_flags table."""
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "user_id", name="uq_feature_flag_name_user"),
    )
    op.create_index("ix_feature_flags_name", "feature_flags", ["name"])
    op.create_index("ix_feature_flags_user_id", "feature_flags", ["user_id"])


def downgrade() -> None:
    """Drop feature_flags table."""
    op.drop_index("ix_feature_flags_user_id", table_name="feature_flags")
    op.drop_index("ix_feature_flags_name", table_name="feature_flags")
    op.drop_table("feature_flags")
