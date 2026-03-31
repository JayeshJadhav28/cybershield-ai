"""
Tests for awareness module — quiz sessions, grading, badges, scenarios, summary.
"""

import uuid
import pytest
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from database import get_db
from models.user import User
from models.quiz import QuizQuestion, QuizSession, QuizAnswer, Scenario
from models.auth import OTPToken
from services.quiz_service import QuizService, quiz_service
from utils.security import hash_otp


def _seed_quiz_questions(db: Session, category: str = "phishing", count: int = 5) -> list:
    """Seed quiz questions for testing."""
    questions = []
    for i in range(count):
        q = QuizQuestion(
            id=uuid.uuid4(),
            category=category,
            difficulty=1 + (i % 3),
            question_text=f"Test question {i + 1} for {category}?",
            options=[f"Option A{i}", f"Option B{i}", f"Option C{i}", f"Option D{i}"],
            correct_option_index=i % 4,
            explanation=f"Explanation for question {i + 1}.",
            language="en",
            tags=["test"],
        )
        db.add(q)
        questions.append(q)
    db.commit()
    return questions


def _seed_scenario(db: Session, category: str = "kyc_otp") -> Scenario:
    """Seed a scenario for testing."""
    scenario = Scenario(
        id=uuid.uuid4(),
        title="Test Fake KYC Call",
        description="A test scenario about a fake KYC phone call.",
        category=category,
        scenario_type="chat",
        estimated_time_minutes=5,
        steps=[
            {
                "type": "message",
                "role": "caller",
                "message": "Hello, this is bank customer care. Your KYC has expired.",
            },
            {
                "type": "choice",
                "prompt": "What do you do?",
                "options": [
                    "Share your OTP",
                    "Hang up and call the bank directly",
                    "Share your Aadhaar number",
                    "Ask for more details",
                ],
                "correct_index": 1,
                "feedback": {
                    "0": "Never share OTP!",
                    "1": "Correct! Always verify independently.",
                    "2": "Never share documents over phone!",
                    "3": "Better to hang up and verify.",
                },
            },
        ],
        language="en",
    )
    db.add(scenario)
    db.commit()
    return scenario


def _create_user(db: Session, email: str = "quizuser@test.com") -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email=email,
        display_name="Quiz Tester",
        role="user",
    )
    db.add(user)
    db.commit()
    return user


def _get_auth_token(client, db, email="quizuser@test.com"):
    """Helper to get auth token for testing authenticated endpoints."""
    otp_plain = "123456"
    otp_record = OTPToken(
        id=uuid.uuid4(),
        email=email,
        otp_hash=hash_otp(otp_plain),
        purpose="login",
        expires_at=datetime.now(timezone.utc).__add__(
            __import__("datetime").timedelta(minutes=5)
        ),
    )
    db.add(otp_record)
    db.commit()

    resp = client.post(
        "/api/v1/auth/verify-otp",
        json={"email": email, "otp": otp_plain, "purpose": "login"},
    )
    return resp.json()["access_token"]


# ═══════════════════════════════════════════
# QUIZ SERVICE UNIT TESTS
# ═══════════════════════════════════════════

class TestQuizServiceUnit:

    def test_badge_gold(self):
        assert QuizService._compute_badge(95) == "gold"
        assert QuizService._compute_badge(90) == "gold"
        assert QuizService._compute_badge(100) == "gold"

    def test_badge_silver(self):
        assert QuizService._compute_badge(70) == "silver"
        assert QuizService._compute_badge(85) == "silver"
        assert QuizService._compute_badge(89) == "silver"

    def test_badge_bronze(self):
        assert QuizService._compute_badge(50) == "bronze"
        assert QuizService._compute_badge(69) == "bronze"

    def test_badge_none(self):
        assert QuizService._compute_badge(0) is None
        assert QuizService._compute_badge(49) is None
        assert QuizService._compute_badge(30) is None


# ═══════════════════════════════════════════
# QUIZ SERVICE INTEGRATION TESTS
# ═══════════════════════════════════════════

class TestQuizServiceIntegration:

    def test_get_questions(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 5)
        result = quiz_service.get_questions(db_session, "phishing")
        assert len(result) == 5

    def test_get_questions_empty_category(self, db_session):
        result = quiz_service.get_questions(db_session, "nonexistent")
        assert len(result) == 0

    def test_get_questions_respects_limit(self, db_session):
        _seed_quiz_questions(db_session, "deepfake", 15)
        result = quiz_service.get_questions(db_session, "deepfake", limit=5)
        assert len(result) == 5

    def test_get_questions_randomized(self, db_session):
        _seed_quiz_questions(db_session, "upi_qr", 10)
        r1 = quiz_service.get_questions(db_session, "upi_qr")
        r2 = quiz_service.get_questions(db_session, "upi_qr")
        ids1 = [str(q.id) for q in r1]
        ids2 = [str(q.id) for q in r2]
        # Same set but potentially different order (randomized)
        assert set(ids1) == set(ids2)

    def test_start_session(self, db_session):
        _seed_quiz_questions(db_session, "phishing", 5)
        session, questions = quiz_service.start_session(db_session, "phishing")

        assert session.id is not None
        assert session.category == "phishing"
        assert session.total_questions == 5
        assert session.completed_at is None
        assert len(questions) == 5

    def test_start_session_no_questions(self, db_session):
        with pytest.raises(ValueError, match="No questions"):
            quiz_service.start_session(db_session, "nonexistent_cat")

    def test_submit_answers_all_correct(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 5)
        session, _ = quiz_service.start_session(db_session, "phishing")

        answers = [
            {"question_id": str(q.id), "selected_option_index": q.correct_option_index}
            for q in questions
        ]

        result = quiz_service.submit_answers(db_session, str(session.id), answers)

        assert result["correct_count"] == 5
        assert result["score_pct"] == 100
        assert result["badge_earned"] == "gold"
        assert len(result["results"]) == 5
        assert all(r["is_correct"] for r in result["results"])

    def test_submit_answers_all_wrong(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 5)
        session, _ = quiz_service.start_session(db_session, "phishing")

        answers = [
            {
                "question_id": str(q.id),
                "selected_option_index": (q.correct_option_index + 1) % 4,
            }
            for q in questions
        ]

        result = quiz_service.submit_answers(db_session, str(session.id), answers)

        assert result["correct_count"] == 0
        assert result["score_pct"] == 0
        assert result["badge_earned"] is None

    def test_submit_answers_mixed(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 10)
        session, _ = quiz_service.start_session(db_session, "phishing")

        answers = []
        for i, q in enumerate(questions):
            if i < 7:  # 7 correct out of 10
                answers.append({"question_id": str(q.id), "selected_option_index": q.correct_option_index})
            else:
                answers.append({"question_id": str(q.id), "selected_option_index": (q.correct_option_index + 1) % 4})

        result = quiz_service.submit_answers(db_session, str(session.id), answers)

        assert result["correct_count"] == 7
        assert result["score_pct"] == 70
        assert result["badge_earned"] == "silver"

    def test_submit_answers_already_completed(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 3)
        session, _ = quiz_service.start_session(db_session, "phishing")

        answers = [
            {"question_id": str(q.id), "selected_option_index": 0}
            for q in questions
        ]

        quiz_service.submit_answers(db_session, str(session.id), answers)

        with pytest.raises(ValueError, match="already completed"):
            quiz_service.submit_answers(db_session, str(session.id), answers)

    def test_submit_answers_invalid_session(self, db_session):
        with pytest.raises(ValueError, match="not found"):
            quiz_service.submit_answers(db_session, str(uuid.uuid4()), [])

    def test_submit_answers_explanations_returned(self, db_session):
        questions = _seed_quiz_questions(db_session, "phishing", 3)
        session, _ = quiz_service.start_session(db_session, "phishing")

        answers = [
            {"question_id": str(q.id), "selected_option_index": 0}
            for q in questions
        ]

        result = quiz_service.submit_answers(db_session, str(session.id), answers)

        for r in result["results"]:
            assert "explanation" in r
            assert len(r["explanation"]) > 0

    def test_get_scenarios(self, db_session):
        _seed_scenario(db_session, "kyc_otp")
        scenarios = quiz_service.get_scenarios(db_session)
        assert len(scenarios) >= 1

    def test_get_scenario_by_id(self, db_session):
        scenario = _seed_scenario(db_session)
        fetched = quiz_service.get_scenario_by_id(db_session, str(scenario.id))
        assert fetched is not None
        assert fetched.title == scenario.title

    def test_get_scenario_not_found(self, db_session):
        result = quiz_service.get_scenario_by_id(db_session, str(uuid.uuid4()))
        assert result is None

    def test_user_summary_no_sessions(self, db_session):
        user = _create_user(db_session)
        summary = quiz_service.get_user_summary(db_session, user.id)

        assert summary["total_quizzes_completed"] == 0
        assert summary["average_score_pct"] == 0
        assert summary["badges"] == []
        assert summary["weakest_category"] is None

    def test_user_summary_with_sessions(self, db_session):
        user = _create_user(db_session, "summary@test.com")

        # Create completed sessions
        for cat, score, badge in [
            ("phishing", 90, "gold"),
            ("phishing", 60, "bronze"),
            ("upi_qr", 50, "bronze"),
        ]:
            session = QuizSession(
                id=uuid.uuid4(),
                user_id=user.id,
                category=cat,
                total_questions=10,
                correct_count=score // 10,
                score_pct=score,
                badge_earned=badge,
                completed_at=datetime.now(timezone.utc),
            )
            db_session.add(session)

        db_session.commit()

        summary = quiz_service.get_user_summary(db_session, user.id)

        assert summary["total_quizzes_completed"] == 3
        assert summary["average_score_pct"] > 0
        assert len(summary["badges"]) >= 1
        assert "phishing" in summary["category_scores"]
        assert "upi_qr" in summary["category_scores"]
        assert summary["category_scores"]["phishing"]["attempts"] == 2
        assert summary["category_scores"]["phishing"]["best_score"] == 90
        assert summary["weakest_category"] == "upi_qr"

    def test_available_categories(self, db_session):
        _seed_quiz_questions(db_session, "phishing", 5)
        _seed_quiz_questions(db_session, "deepfake", 3)

        cats = quiz_service.get_available_categories(db_session)
        cat_names = [c["category"] for c in cats]

        assert "phishing" in cat_names
        assert "deepfake" in cat_names


# ═══════════════════════════════════════════
# AWARENESS ROUTE ENDPOINT TESTS
# ═══════════════════════════════════════════

class TestAwarenessEndpoints:

    @pytest.fixture(autouse=True)
    def setup(self, db_session, override_get_db):
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.db = db_session
        yield
        app.dependency_overrides.clear()

    def test_get_quizzes(self):
        _seed_quiz_questions(self.db, "phishing", 5)

        response = self.client.get(
            "/api/v1/awareness/quizzes?category=phishing&language=en"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["category"] == "phishing"
        assert data["total_questions"] == 5
        assert len(data["questions"]) == 5

        # Questions should NOT contain correct answer
        for q in data["questions"]:
            assert "correct_option_index" not in q
            assert "explanation" not in q
            assert "id" in q
            assert "question_text" in q
            assert "options" in q

    def test_get_quizzes_not_found(self):
        response = self.client.get(
            "/api/v1/awareness/quizzes?category=phishing&language=en"
        )
        assert response.status_code == 404

    def test_get_quizzes_invalid_category(self):
        response = self.client.get(
            "/api/v1/awareness/quizzes?category=invalid_cat"
        )
        assert response.status_code == 422

    def test_get_categories(self):
        _seed_quiz_questions(self.db, "phishing", 3)
        _seed_quiz_questions(self.db, "deepfake", 2)

        response = self.client.get("/api/v1/awareness/quizzes/categories")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) >= 2

    def test_start_quiz_session(self):
        _seed_quiz_questions(self.db, "phishing", 5)

        response = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "phishing", "language": "en"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "session_id" in data
        assert data["category"] == "phishing"
        assert data["total_questions"] == 5
        assert len(data["questions"]) == 5

    def test_start_quiz_session_no_questions(self):
        response = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "deepfake"},
        )
        assert response.status_code == 404

    def test_submit_answers_endpoint(self):
        questions = _seed_quiz_questions(self.db, "phishing", 3)

        # Start session
        start_resp = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "phishing"},
        )
        session_id = start_resp.json()["session_id"]
        returned_questions = start_resp.json()["questions"]

        # Submit all correct
        answers = []
        for rq in returned_questions:
            q = next(q for q in questions if str(q.id) == rq["id"])
            answers.append({
                "question_id": rq["id"],
                "selected_option_index": q.correct_option_index,
            })

        response = self.client.post(
            f"/api/v1/awareness/quiz-sessions/{session_id}/answers",
            json={"answers": answers},
        )
        assert response.status_code == 200
        data = response.json()

        assert data["correct_count"] == 3
        assert data["score_pct"] == 100
        assert data["badge_earned"] == "gold"
        assert len(data["results"]) == 3

        # Each result should have explanation
        for r in data["results"]:
            assert r["is_correct"] is True
            assert "explanation" in r
            assert len(r["explanation"]) > 0

    def test_submit_answers_mixed_results(self):
        questions = _seed_quiz_questions(self.db, "phishing", 4)

        start_resp = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "phishing"},
        )
        session_id = start_resp.json()["session_id"]
        rqs = start_resp.json()["questions"]

        # 3 correct, 1 wrong
        answers = []
        for i, rq in enumerate(rqs):
            q = next(q for q in questions if str(q.id) == rq["id"])
            if i < 3:
                answers.append({"question_id": rq["id"], "selected_option_index": q.correct_option_index})
            else:
                answers.append({"question_id": rq["id"], "selected_option_index": (q.correct_option_index + 1) % 4})

        response = self.client.post(
            f"/api/v1/awareness/quiz-sessions/{session_id}/answers",
            json={"answers": answers},
        )
        data = response.json()

        assert data["correct_count"] == 3
        assert data["score_pct"] == 75
        assert data["badge_earned"] == "silver"

    def test_submit_answers_invalid_session(self):
        response = self.client.post(
            f"/api/v1/awareness/quiz-sessions/{uuid.uuid4()}/answers",
            json={"answers": [{"question_id": str(uuid.uuid4()), "selected_option_index": 0}]},
        )
        assert response.status_code == 400

    def test_submit_answers_duplicate_rejected(self):
        """Submitting to already-completed session should fail."""
        questions = _seed_quiz_questions(self.db, "phishing", 2)

        start_resp = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "phishing"},
        )
        session_id = start_resp.json()["session_id"]
        rqs = start_resp.json()["questions"]

        answers = [
            {"question_id": rq["id"], "selected_option_index": 0}
            for rq in rqs
        ]

        # First submission
        self.client.post(
            f"/api/v1/awareness/quiz-sessions/{session_id}/answers",
            json={"answers": answers},
        )

        # Second submission should fail
        response = self.client.post(
            f"/api/v1/awareness/quiz-sessions/{session_id}/answers",
            json={"answers": answers},
        )
        assert response.status_code == 400

    def test_list_scenarios(self):
        _seed_scenario(self.db, "kyc_otp")

        response = self.client.get("/api/v1/awareness/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        assert len(data["scenarios"]) >= 1

        scenario = data["scenarios"][0]
        assert "id" in scenario
        assert "title" in scenario
        assert "category" in scenario

    def test_list_scenarios_by_category(self):
        _seed_scenario(self.db, "kyc_otp")

        response = self.client.get("/api/v1/awareness/scenarios?category=kyc_otp")
        assert response.status_code == 200
        assert len(response.json()["scenarios"]) >= 1

        response2 = self.client.get("/api/v1/awareness/scenarios?category=phishing")
        assert response2.status_code == 200
        # No phishing scenarios seeded
        assert len(response2.json()["scenarios"]) == 0

    def test_get_scenario_detail(self):
        scenario = _seed_scenario(self.db)

        response = self.client.get(f"/api/v1/awareness/scenarios/{scenario.id}")
        assert response.status_code == 200
        data = response.json()

        assert data["title"] == "Test Fake KYC Call"
        assert len(data["steps"]) == 2
        assert data["steps"][0]["type"] == "message"
        assert data["steps"][1]["type"] == "choice"
        assert data["steps"][1]["options"] is not None
        assert len(data["steps"][1]["options"]) == 4

    def test_get_scenario_not_found(self):
        response = self.client.get(f"/api/v1/awareness/scenarios/{uuid.uuid4()}")
        assert response.status_code == 404

    def test_awareness_summary_unauthenticated(self):
        response = self.client.get("/api/v1/awareness/summary")
        assert response.status_code == 401

    def test_awareness_summary_authenticated(self):
        _seed_quiz_questions(self.db, "phishing", 3)
        token = _get_auth_token(self.client, self.db, "aware@test.com")

        response = self.client.get(
            "/api/v1/awareness/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()

        assert "total_quizzes_completed" in data
        assert "average_score_pct" in data
        assert "badges" in data
        assert "category_scores" in data

    def test_full_quiz_flow(self):
        """End-to-end: get questions → start session → submit → check summary."""
        questions = _seed_quiz_questions(self.db, "phishing", 5)
        token = _get_auth_token(self.client, self.db, "fullquiz@test.com")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Check categories
        cat_resp = self.client.get("/api/v1/awareness/quizzes/categories")
        assert cat_resp.status_code == 200

        # 2. Get questions
        q_resp = self.client.get("/api/v1/awareness/quizzes?category=phishing")
        assert q_resp.status_code == 200

        # 3. Start session (authenticated)
        start_resp = self.client.post(
            "/api/v1/awareness/quiz-sessions",
            json={"category": "phishing"},
            headers=headers,
        )
        assert start_resp.status_code == 201
        session_id = start_resp.json()["session_id"]
        rqs = start_resp.json()["questions"]

        # 4. Submit answers (all correct)
        answers = []
        for rq in rqs:
            q = next(q for q in questions if str(q.id) == rq["id"])
            answers.append({"question_id": rq["id"], "selected_option_index": q.correct_option_index})

        submit_resp = self.client.post(
            f"/api/v1/awareness/quiz-sessions/{session_id}/answers",
            json={"answers": answers},
        )
        assert submit_resp.status_code == 200
        assert submit_resp.json()["badge_earned"] == "gold"

        # 5. Check summary
        summary_resp = self.client.get(
            "/api/v1/awareness/summary",
            headers=headers,
        )
        assert summary_resp.status_code == 200
        summary = summary_resp.json()
        assert summary["total_quizzes_completed"] == 1
        assert summary["average_score_pct"] == 100
        assert len(summary["badges"]) >= 1