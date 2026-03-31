"""
Test database connection and model creation.
"""

import uuid
from datetime import datetime, timezone

from models.user import User
from models.organization import Organization
from models.analysis import Analysis
from models.quiz import QuizQuestion
from models.config import ScoringConfig


def test_create_user(db_session):
    """Test creating a user record."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        display_name="Test User",
        role="user",
    )
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(email="test@example.com").first()
    assert fetched is not None
    assert fetched.email == "test@example.com"
    assert fetched.role == "user"
    assert fetched.is_active is True


def test_create_organization(db_session):
    """Test creating an organization."""
    org = Organization(
        id=uuid.uuid4(),
        name="HDFC Bank",
        type="bank",
        contact_email="security@hdfc.com",
    )
    db_session.add(org)
    db_session.commit()

    fetched = db_session.query(Organization).filter_by(name="HDFC Bank").first()
    assert fetched is not None
    assert fetched.type == "bank"


def test_create_analysis(db_session):
    """Test creating an analysis record."""
    analysis = Analysis(
        id=uuid.uuid4(),
        type="email",
        input_hash="a" * 64,
        risk_score=85,
        risk_label="dangerous",
        explanation_summary="Phishing detected",
        model_scores={"phish": 0.92},
        processing_time_ms=1200,
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.query(Analysis).first()
    assert fetched.risk_score == 85
    assert fetched.risk_label == "dangerous"
    assert fetched.model_scores["phish"] == 0.92


def test_create_quiz_question(db_session):
    """Test creating a quiz question."""
    question = QuizQuestion(
        id=uuid.uuid4(),
        category="phishing",
        difficulty=1,
        question_text="Is this email safe?",
        options=["Yes", "No", "Maybe", "Report it"],
        correct_option_index=3,
        explanation="Always report suspicious emails.",
        language="en",
        tags=["india", "email"],
    )
    db_session.add(question)
    db_session.commit()

    fetched = db_session.query(QuizQuestion).first()
    assert fetched.category == "phishing"
    assert fetched.options[3] == "Report it"
    assert fetched.correct_option_index == 3


def test_user_analysis_relationship(db_session):
    """Test user → analyses relationship."""
    user = User(
        id=uuid.uuid4(),
        email="analyst@test.com",
        role="user",
    )
    db_session.add(user)
    db_session.flush()

    analysis = Analysis(
        id=uuid.uuid4(),
        user_id=user.id,
        type="url",
        input_hash="b" * 64,
        risk_score=55,
        risk_label="suspicious",
        explanation_summary="Suspicious URL detected",
    )
    db_session.add(analysis)
    db_session.commit()

    fetched_user = db_session.query(User).filter_by(email="analyst@test.com").first()
    assert len(fetched_user.analyses) == 1
    assert fetched_user.analyses[0].risk_score == 55


def test_scoring_config_defaults(db_session):
    """Test scoring config with default values."""
    config = ScoringConfig(
        id=uuid.uuid4(),
        org_id=None,  # Global default
    )
    db_session.add(config)
    db_session.commit()

    fetched = db_session.query(ScoringConfig).first()
    assert float(fetched.audio_weight) == 0.35
    assert float(fetched.video_weight) == 0.35
    assert float(fetched.phish_weight) == 0.30
    assert fetched.safe_threshold == 30
    assert fetched.dangerous_threshold == 70


def test_anonymous_analysis(db_session):
    """Test creating analysis without user (anonymous)."""
    analysis = Analysis(
        id=uuid.uuid4(),
        user_id=None,  # Anonymous
        type="audio",
        input_hash="c" * 64,
        risk_score=72,
        risk_label="dangerous",
        explanation_summary="Deepfake audio detected",
    )
    db_session.add(analysis)
    db_session.commit()

    fetched = db_session.query(Analysis).first()
    assert fetched.user_id is None
    assert fetched.risk_label == "dangerous"