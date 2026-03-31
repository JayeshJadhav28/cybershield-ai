"""
Tests for reports, admin, and demo routes.
"""

import uuid
import pytest
from datetime import datetime, timezone, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from database import get_db
from models.user import User
from models.auth import OTPToken
from models.analysis import Analysis, AnalysisDetail
from models.quiz import QuizSession, QuizQuestion
from models.config import ScoringConfig
from utils.security import hash_otp


def _create_user(db, email="report@test.com", role="user"):
    user = User(id=uuid.uuid4(), email=email, role=role, display_name="Tester")
    db.add(user)
    db.commit()
    return user


def _get_token(client, db, email="report@test.com"):
    otp = "123456"
    rec = OTPToken(
        id=uuid.uuid4(), email=email, otp_hash=hash_otp(otp),
        purpose="login",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
    )
    db.add(rec)
    db.commit()
    resp = client.post("/api/v1/auth/verify-otp", json={"email": email, "otp": otp, "purpose": "login"})
    return resp.json()["access_token"]


def _create_analysis(db, user_id, atype="email", score=50, label="suspicious"):
    a = Analysis(
        id=uuid.uuid4(), user_id=user_id, type=atype,
        input_hash="a" * 64, risk_score=score, risk_label=label,
        explanation_summary=f"Test {atype} analysis",
        model_scores={"phish": 0.5}, processing_time_ms=100,
    )
    db.add(a)
    d = AnalysisDetail(id=uuid.uuid4(), analysis_id=a.id, raw_metadata={"test": True})
    db.add(d)
    db.commit()
    return a


def _seed_scoring_config(db):
    existing = db.query(ScoringConfig).filter(ScoringConfig.org_id.is_(None)).first()
    if existing:
        return existing
    cfg = ScoringConfig(
        id=uuid.uuid4(), org_id=None,
        audio_weight=0.35, video_weight=0.35, phish_weight=0.30,
        safe_threshold=30, dangerous_threshold=70,
    )
    db.add(cfg)
    db.commit()
    return cfg


# ═══════════════════════════════════════════
# REPORTS TESTS
# ═══════════════════════════════════════════

class TestReports:

    @pytest.fixture(autouse=True)
    def setup(self, db_session, override_get_db):
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.db = db_session
        yield
        app.dependency_overrides.clear()

    def test_analysis_history_unauthenticated(self):
        resp = self.client.get("/api/v1/reports/analyses")
        assert resp.status_code == 401

    def test_analysis_history_empty(self):
        token = _get_token(self.client, self.db, "empty@test.com")
        resp = self.client.get(
            "/api/v1/reports/analyses",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["analyses"] == []

    def test_analysis_history_with_data(self):
        token = _get_token(self.client, self.db, "history@test.com")
        user = self.db.query(User).filter_by(email="history@test.com").first()
        _create_analysis(self.db, user.id, "email", 80, "dangerous")
        _create_analysis(self.db, user.id, "url", 20, "safe")
        _create_analysis(self.db, user.id, "audio", 55, "suspicious")

        resp = self.client.get(
            "/api/v1/reports/analyses",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()
        assert data["total"] == 3
        assert len(data["analyses"]) == 3

    def test_analysis_history_type_filter(self):
        token = _get_token(self.client, self.db, "filter@test.com")
        user = self.db.query(User).filter_by(email="filter@test.com").first()
        _create_analysis(self.db, user.id, "email")
        _create_analysis(self.db, user.id, "email")
        _create_analysis(self.db, user.id, "url")

        resp = self.client.get(
            "/api/v1/reports/analyses?type=email",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()
        assert data["total"] == 2

    def test_analysis_history_pagination(self):
        token = _get_token(self.client, self.db, "paginate@test.com")
        user = self.db.query(User).filter_by(email="paginate@test.com").first()
        for i in range(5):
            _create_analysis(self.db, user.id, "email", 50 + i)

        resp = self.client.get(
            "/api/v1/reports/analyses?page=1&limit=2",
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()
        assert data["total"] == 5
        assert len(data["analyses"]) == 2
        assert data["page"] == 1

    def test_analysis_detail(self):
        token = _get_token(self.client, self.db, "detail@test.com")
        user = self.db.query(User).filter_by(email="detail@test.com").first()
        analysis = _create_analysis(self.db, user.id, "email", 75, "dangerous")

        resp = self.client.get(
            f"/api/v1/reports/analyses/{analysis.id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["risk_score"] == 75
        assert data["risk_label"] == "dangerous"
        assert data["raw_metadata"] is not None

    def test_analysis_detail_not_found(self):
        token = _get_token(self.client, self.db, "notfound@test.com")
        resp = self.client.get(
            f"/api/v1/reports/analyses/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404

    def test_analysis_detail_wrong_user(self):
        """User can only view their own analyses."""
        token1 = _get_token(self.client, self.db, "user1@test.com")
        user1 = self.db.query(User).filter_by(email="user1@test.com").first()
        analysis = _create_analysis(self.db, user1.id)

        token2 = _get_token(self.client, self.db, "user2@test.com")
        resp = self.client.get(
            f"/api/v1/reports/analyses/{analysis.id}",
            headers={"Authorization": f"Bearer {token2}"},
        )
        assert resp.status_code == 404

    def test_quiz_history(self):
        token = _get_token(self.client, self.db, "quizhist@test.com")
        user = self.db.query(User).filter_by(email="quizhist@test.com").first()

        session = QuizSession(
            id=uuid.uuid4(), user_id=user.id, category="phishing",
            total_questions=10, correct_count=8, score_pct=80,
            badge_earned="silver", completed_at=datetime.now(timezone.utc),
        )
        self.db.add(session)
        self.db.commit()

        resp = self.client.get(
            "/api/v1/reports/quizzes",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["sessions"][0]["badge_earned"] == "silver"

    def test_quiz_history_category_filter(self):
        token = _get_token(self.client, self.db, "quizfilter@test.com")
        user = self.db.query(User).filter_by(email="quizfilter@test.com").first()

        for cat in ["phishing", "phishing", "deepfake"]:
            self.db.add(QuizSession(
                id=uuid.uuid4(), user_id=user.id, category=cat,
                total_questions=5, correct_count=3, score_pct=60,
                completed_at=datetime.now(timezone.utc),
            ))
        self.db.commit()

        resp = self.client.get(
            "/api/v1/reports/quizzes?category=phishing",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.json()["total"] == 2


# ═══════════════════════════════════════════
# ADMIN TESTS
# ═══════════════════════════════════════════

class TestAdmin:

    @pytest.fixture(autouse=True)
    def setup(self, db_session, override_get_db):
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.db = db_session
        _seed_scoring_config(self.db)
        yield
        app.dependency_overrides.clear()

    def test_metrics_authenticated(self):
        token = _get_token(self.client, self.db, "admin@test.com")
        resp = self.client.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "total_analyses" in data
        assert "analyses_by_type" in data
        assert "risk_distribution" in data
        assert "quiz_metrics" in data

    def test_metrics_unauthenticated(self):
        resp = self.client.get("/api/v1/admin/metrics")
        assert resp.status_code == 401

    def test_get_scoring_config(self):
        token = _get_token(self.client, self.db, "config@test.com")
        resp = self.client.get(
            "/api/v1/admin/scoring-config",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_threshold"] == 30
        assert data["dangerous_threshold"] == 70
        assert float(data["audio_weight"]) == 0.35

    def test_update_scoring_config_requires_admin(self):
        token = _get_token(self.client, self.db, "nonadmin@test.com")
        resp = self.client.patch(
            "/api/v1/admin/scoring-config",
            json={"safe_threshold": 25},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403

    def test_update_scoring_config_as_admin(self):
        # Create admin user
        otp = "111111"
        rec = OTPToken(
            id=uuid.uuid4(), email="superadmin@test.com", otp_hash=hash_otp(otp),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(rec)
        self.db.commit()

        resp = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "superadmin@test.com", "otp": otp, "purpose": "login"},
        )
        token = resp.json()["access_token"]

        # Make user admin
        user = self.db.query(User).filter_by(email="superadmin@test.com").first()
        user.role = "admin"
        self.db.commit()

        resp = self.client.patch(
            "/api/v1/admin/scoring-config",
            json={"safe_threshold": 25, "dangerous_threshold": 75},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_threshold"] == 25
        assert data["dangerous_threshold"] == 75

    def test_update_scoring_config_invalid_thresholds(self):
        otp = "222222"
        rec = OTPToken(
            id=uuid.uuid4(), email="badadmin@test.com", otp_hash=hash_otp(otp),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(rec)
        self.db.commit()

        resp = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "badadmin@test.com", "otp": otp, "purpose": "login"},
        )
        token = resp.json()["access_token"]
        user = self.db.query(User).filter_by(email="badadmin@test.com").first()
        user.role = "admin"
        self.db.commit()

        resp = self.client.patch(
            "/api/v1/admin/scoring-config",
            json={"safe_threshold": 80, "dangerous_threshold": 50},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400


# ═══════════════════════════════════════════
# DEMO TESTS
# ═══════════════════════════════════════════

class TestDemo:

    @pytest.fixture(autouse=True)
    def setup(self, db_session, override_get_db):
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.db = db_session
        yield
        app.dependency_overrides.clear()

    def test_get_demo_samples(self):
        resp = self.client.get("/api/v1/demo/samples")
        assert resp.status_code == 200
        data = resp.json()
        assert "samples" in data
        assert len(data["samples"]) >= 5

        # Check structure
        for sample in data["samples"]:
            assert "id" in sample
            assert "type" in sample
            assert "title" in sample
            assert "expected_label" in sample

    def test_get_demo_sample_by_id(self):
        resp = self.client.get("/api/v1/demo/samples/demo_phishing_email_dangerous")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == "demo_phishing_email_dangerous"
        assert data["type"] == "email"
        assert data["expected_label"] == "dangerous"
        assert "data" in data
        assert "subject" in data["data"]

    def test_get_demo_sample_not_found(self):
        resp = self.client.get("/api/v1/demo/samples/nonexistent")
        assert resp.status_code == 404

    def test_demo_samples_have_all_types(self):
        resp = self.client.get("/api/v1/demo/samples")
        types = set(s["type"] for s in resp.json()["samples"])
        assert "email" in types
        assert "url" in types

    def test_demo_email_can_be_analyzed(self):
        """Test that demo email data can be submitted to the email analyzer."""
        sample_resp = self.client.get("/api/v1/demo/samples/demo_phishing_email_dangerous")
        sample_data = sample_resp.json()["data"]

        analyze_resp = self.client.post(
            "/api/v1/analyze/email",
            json=sample_data,
        )
        assert analyze_resp.status_code == 200
        result = analyze_resp.json()
        assert result["risk_score"] >= 40
        assert result["risk_label"] in ["suspicious", "dangerous"]

    def test_demo_safe_email_analyzed(self):
        sample_resp = self.client.get("/api/v1/demo/samples/demo_safe_email")
        sample_data = sample_resp.json()["data"]

        analyze_resp = self.client.post("/api/v1/analyze/email", json=sample_data)
        assert analyze_resp.status_code == 200
        result = analyze_resp.json()
        assert result["risk_score"] < 60

    def test_demo_url_can_be_analyzed(self):
        sample_resp = self.client.get("/api/v1/demo/samples/demo_dangerous_url")
        sample_data = sample_resp.json()["data"]

        analyze_resp = self.client.post("/api/v1/analyze/url", json=sample_data)
        assert analyze_resp.status_code == 200
        result = analyze_resp.json()
        assert result["risk_score"] >= 30


# ═══════════════════════════════════════════
# SEED SCRIPT TESTS
# ═══════════════════════════════════════════

class TestSeedScript:

    def test_seed_quiz_questions(self, db_session):
        from data.seed_db import seed_quiz_questions
        count = seed_quiz_questions(db_session)
        assert count >= 28

        questions = db_session.query(QuizQuestion).all()
        assert len(questions) >= 28

        # Check categories
        categories = set(q.category for q in questions)
        assert "phishing" in categories
        assert "upi_qr" in categories
        assert "kyc_otp" in categories
        assert "deepfake" in categories
        assert "general" in categories

    def test_seed_scenarios(self, db_session):
        from data.seed_db import seed_scenarios
        from models.quiz import Scenario
        count = seed_scenarios(db_session)
        assert count >= 2

        scenarios = db_session.query(Scenario).all()
        assert len(scenarios) >= 2
        assert any(s.title == "The Fake KYC Call" for s in scenarios)
        assert any(s.title == "Phishing Email at Work" for s in scenarios)

    def test_seed_idempotent(self, db_session):
        """Running seed twice should not create duplicates."""
        from data.seed_db import seed_quiz_questions, seed_scenarios
        c1 = seed_quiz_questions(db_session)
        c2 = seed_quiz_questions(db_session)
        assert c1 == c2  # Second run returns same count without inserting

        s1 = seed_scenarios(db_session)
        s2 = seed_scenarios(db_session)
        assert s1 == s2

    def test_seed_default_config(self, db_session):
        from data.seed_db import seed_default_scoring_config
        seed_default_scoring_config(db_session)

        config = db_session.query(ScoringConfig).filter(
            ScoringConfig.org_id.is_(None)
        ).first()
        assert config is not None
        assert config.safe_threshold == 30
        assert config.dangerous_threshold == 70