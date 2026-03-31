"""
Audit log model — tracks all significant actions for compliance.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Text, DateTime, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID

from database import Base
from models.db_types import json_type, ip_address_type


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_type = Column(
        SAEnum("user", "system", name="actor_type", create_type=True),
        nullable=False,
    )
    actor_id = Column(UUID(as_uuid=True), nullable=True)  # NULL for system actions
    action = Column(String(100), nullable=False)
    # Examples: 'analysis.created', 'quiz.completed', 'user.login', 'config.updated'
    target_type = Column(
        SAEnum(
            "analysis", "quiz", "config", "user",
            name="audit_target_type", create_type=True
        ),
        nullable=False,
    )
    target_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_ = Column("metadata", json_type(), default=dict)  # Renamed to avoid Python builtin conflict
    ip_address = Column(ip_address_type(), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self):
        return f"<AuditLog {self.action} target={self.target_type}/{self.target_id}>"