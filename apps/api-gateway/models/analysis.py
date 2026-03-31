"""
Analysis models — stores results from email, URL, QR, audio, video scans.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, SmallInteger, Boolean, Text, Integer,
    DateTime, Enum as SAEnum, ForeignKey, CheckConstraint, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.db_types import json_type


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # NULL = anonymous analysis
        index=True,
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    type = Column(
        SAEnum("email", "url", "qr", "audio", "video", name="analysis_type", create_type=True),
        nullable=False,
        index=True,
    )
    input_hash = Column(String(64), nullable=False, index=True)  # SHA-256
    risk_score = Column(
        SmallInteger, nullable=False,
    )
    risk_label = Column(
        SAEnum("safe", "suspicious", "dangerous", name="risk_label", create_type=True),
        nullable=False,
    )
    explanation_summary = Column(Text, nullable=False)
    model_scores = Column(json_type(), nullable=True)        # Raw model outputs
    processing_time_ms = Column(Integer, nullable=True)  # Latency tracking
    is_demo = Column(Boolean, nullable=False, default=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="ck_risk_score_range"),
    )

    # Relationships
    user = relationship("User", back_populates="analyses")
    organization = relationship("Organization", back_populates="analyses")
    details = relationship("AnalysisDetail", back_populates="analysis", cascade="all, delete-orphan", uselist=False)

    def __repr__(self):
        return f"<Analysis {self.type} score={self.risk_score} label={self.risk_label}>"


class AnalysisDetail(Base):
    __tablename__ = "analysis_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    raw_metadata = Column(json_type(), nullable=False, default=dict)
    # For email: {subject, sender, urls_found, flagged_phrases, ...}
    # For audio: {duration_s, sample_rate, spectral_features, ...}
    # For video: {duration_s, fps, frames_analyzed, anomaly_frames, ...}
    # For URL/QR: {decoded_url, domain, heuristic_flags, ...}

    highlighted_elements = Column(json_type(), default=list)
    # [{type: "phrase", value: "urgent", risk_contribution: 0.15}, ...]

    contributing_factors = Column(json_type(), default=list)
    # [{factor: "suspicious_domain", weight: 0.35, description: "..."}, ...]

    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    analysis = relationship("Analysis", back_populates="details")

    def __repr__(self):
        return f"<AnalysisDetail analysis={self.analysis_id}>"