"""
Configuration models — scoring thresholds, weights.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, SmallInteger, Boolean, DateTime,
    ForeignKey, Numeric, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class ScoringConfig(Base):
    __tablename__ = "scoring_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,  # NULL = global default
    )
    audio_weight = Column(Numeric(3, 2), nullable=False, default=0.35)
    video_weight = Column(Numeric(3, 2), nullable=False, default=0.35)
    phish_weight = Column(Numeric(3, 2), nullable=False, default=0.30)
    safe_threshold = Column(SmallInteger, nullable=False, default=30)
    dangerous_threshold = Column(SmallInteger, nullable=False, default=70)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        CheckConstraint(
            "safe_threshold >= 0 AND safe_threshold <= 100",
            name="ck_safe_threshold_range"
        ),
        CheckConstraint(
            "dangerous_threshold >= 0 AND dangerous_threshold <= 100",
            name="ck_dangerous_threshold_range"
        ),
        CheckConstraint(
            "safe_threshold < dangerous_threshold",
            name="ck_threshold_order"
        ),
    )

    # Relationships
    organization = relationship("Organization", back_populates="scoring_configs")

    def __repr__(self):
        return f"<ScoringConfig org={self.org_id} safe<{self.safe_threshold} dangerous>={self.dangerous_threshold}>"