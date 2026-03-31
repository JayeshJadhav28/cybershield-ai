"""
Quiz and scenario models — awareness module.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, SmallInteger, Boolean, Text, DateTime,
    Enum as SAEnum, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base
from models.db_types import json_type


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category = Column(
        SAEnum(
            "deepfake", "phishing", "upi_qr", "kyc_otp", "general",
            name="quiz_category", create_type=True
        ),
        nullable=False,
        index=True,
    )
    difficulty = Column(SmallInteger, nullable=False, default=1)
    question_text = Column(Text, nullable=False)
    options = Column(json_type(), nullable=False)  # ["option A", "option B", "option C", "option D"]
    correct_option_index = Column(SmallInteger, nullable=False)
    explanation = Column(Text, nullable=False)
    language = Column(String(5), nullable=False, default="en", index=True)
    tags = Column(json_type(), default=list)  # ["india", "upi", "bank", ...]
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

    __table_args__ = (
        CheckConstraint("difficulty >= 1 AND difficulty <= 3", name="ck_difficulty_range"),
        CheckConstraint(
            "correct_option_index >= 0 AND correct_option_index <= 3",
            name="ck_correct_option_range"
        ),
    )

    # Relationships
    answers = relationship("QuizAnswer", back_populates="question")

    def __repr__(self):
        return f"<QuizQuestion {self.category} difficulty={self.difficulty}>"


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,  # NULL = anonymous
        index=True,
    )
    org_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )
    category = Column(
        SAEnum(
            "deepfake", "phishing", "upi_qr", "kyc_otp", "general",
            name="quiz_category", create_type=False  # Already created by QuizQuestion
        ),
        nullable=False,
    )
    total_questions = Column(SmallInteger, nullable=False, default=10)
    correct_count = Column(SmallInteger, default=0)
    score_pct = Column(SmallInteger, default=0)
    badge_earned = Column(String(20), nullable=True)  # 'bronze', 'silver', 'gold', NULL
    started_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        CheckConstraint("score_pct >= 0 AND score_pct <= 100", name="ck_score_pct_range"),
    )

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    organization = relationship("Organization", back_populates="quiz_sessions")
    answers = relationship("QuizAnswer", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<QuizSession {self.category} score={self.score_pct}%>"


class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_index = Column(SmallInteger, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    answered_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("quiz_session_id", "question_id", name="uq_session_question"),
        CheckConstraint(
            "selected_option_index >= 0 AND selected_option_index <= 3",
            name="ck_selected_option_range"
        ),
    )

    # Relationships
    session = relationship("QuizSession", back_populates="answers")
    question = relationship("QuizQuestion", back_populates="answers")

    def __repr__(self):
        return f"<QuizAnswer correct={self.is_correct}>"


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(
        SAEnum(
            "deepfake", "phishing", "upi_qr", "kyc_otp", "general",
            name="quiz_category", create_type=False
        ),
        nullable=False,
    )
    scenario_type = Column(String(20), nullable=False, default="chat")  # chat, email, call
    steps = Column(json_type(), nullable=False)
    # [
    #   {role: "attacker", message: "Dear customer...", type: "message"},
    #   {type: "choice", prompt: "What do you do?", options: [...], correct_index: 1, feedback: {...}},
    # ]
    language = Column(String(5), nullable=False, default="en")
    estimated_time_minutes = Column(SmallInteger, default=5)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Scenario {self.title}>"