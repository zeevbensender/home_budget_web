"""SQLAlchemy model for feature flags."""

from sqlalchemy import Boolean, Column, Integer, String, Text, UniqueConstraint

from app.core.database import Base


class FeatureFlag(Base):
    """
    Feature flag model for database-based feature toggles.

    This table supports:
    - Global flags (user_id is NULL) - applies to all users
    - Per-user flags (user_id is set) - overrides global flag for specific user

    Attributes:
        id: Primary key
        name: Flag name (e.g., "NEW_DASHBOARD", "BETA_EXPORT")
        enabled: Whether the flag is enabled
        user_id: Optional user ID for per-user flags (NULL for global)
        description: Optional description of what the flag controls
    """

    __tablename__ = "feature_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=False)
    user_id = Column(Integer, nullable=True, index=True)
    description = Column(Text, nullable=True)

    # Unique constraint: one flag per name + user_id combination
    __table_args__ = (
        UniqueConstraint("name", "user_id", name="uq_feature_flag_name_user"),
    )

    def __repr__(self) -> str:
        user_info = f"user_id={self.user_id}" if self.user_id else "global"
        return f"<FeatureFlag(name='{self.name}', enabled={self.enabled}, {user_info})>"
