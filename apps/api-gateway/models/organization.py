"""
Organization and membership models — banks, colleges, govt programmes.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Boolean, Text, DateTime,
    Enum as SAEnum, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(
        SAEnum("bank", "college", "govt", "other", name="org_type", create_type=True),
        nullable=False,
        default="other",
    )
    contact_email = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    memberships = relationship("OrgMembership", back_populates="organization", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="organization")
    quiz_sessions = relationship("QuizSession", back_populates="organization")
    scoring_configs = relationship("ScoringConfig", back_populates="organization")

    def __repr__(self):
        return f"<Organization {self.name} type={self.type}>"


class OrgMembership(Base):
    __tablename__ = "org_memberships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(
        SAEnum("member", "coordinator", "admin", name="membership_role", create_type=True),
        nullable=False,
        default="member",
    )
    joined_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uq_org_user"),
    )

    # Relationships
    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="org_memberships")

    def __repr__(self):
        return f"<OrgMembership org={self.org_id} user={self.user_id} role={self.role}>"