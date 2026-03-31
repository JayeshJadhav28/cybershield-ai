"""
Quiz and awareness service — session management, grading, badges, scenarios.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from models.quiz import QuizQuestion, QuizSession, QuizAnswer, Scenario
from schemas.common import QuizCategory


# Badge thresholds
BADGE_THRESHOLDS = {
    "gold": 90,
    "silver": 70,
    "bronze": 50,
}

DEFAULT_QUESTIONS_PER_SESSION = 10


class QuizService:
    """Manages quiz sessions, grading, and awareness tracking."""

    # ═══════════════════════════════════════════
    # QUIZ QUESTIONS
    # ═══════════════════════════════════════════

    def get_questions(
        self,
        db: Session,
        category: str,
        language: str = "en",
        limit: int = DEFAULT_QUESTIONS_PER_SESSION,
    ) -> List[QuizQuestion]:
        """
        Fetch active questions for a category.
        Returns randomized selection up to limit.
        """
        query = (
            db.query(QuizQuestion)
            .filter(
                QuizQuestion.category == category,
                QuizQuestion.language == language,
                QuizQuestion.is_active == True,
            )
        )

        # Get total available
        total = query.count()

        if total == 0:
            return []

        # Randomize selection
        # SQLite doesn't support func.random() the same way — use Python shuffle
        all_questions = query.all()

        import random
        random.shuffle(all_questions)

        return all_questions[:min(limit, total)]

    def get_question_by_id(
        self, db: Session, question_id: str
    ) -> Optional[QuizQuestion]:
        """Fetch a single question by ID."""
        try:
            qid = uuid.UUID(question_id)
        except (ValueError, AttributeError):
            return None
        return db.query(QuizQuestion).filter(QuizQuestion.id == qid).first()

    def get_available_categories(
        self, db: Session, language: str = "en"
    ) -> List[Dict]:
        """Get categories with question counts."""
        results = (
            db.query(
                QuizQuestion.category,
                func.count(QuizQuestion.id).label("count"),
            )
            .filter(
                QuizQuestion.language == language,
                QuizQuestion.is_active == True,
            )
            .group_by(QuizQuestion.category)
            .all()
        )

        return [
            {"category": row.category, "question_count": row.count}
            for row in results
        ]

    # ═══════════════════════════════════════════
    # QUIZ SESSIONS
    # ═══════════════════════════════════════════

    def start_session(
        self,
        db: Session,
        category: str,
        language: str = "en",
        user_id: Optional[uuid.UUID] = None,
        org_id: Optional[uuid.UUID] = None,
    ) -> Tuple[QuizSession, List[QuizQuestion]]:
        """
        Start a new quiz session.
        Returns (session, questions) tuple.
        Raises ValueError if no questions available.
        """
        questions = self.get_questions(db, category, language)

        if not questions:
            raise ValueError(
                f"No questions available for category '{category}' in language '{language}'"
            )

        session = QuizSession(
            id=uuid.uuid4(),
            user_id=user_id,
            org_id=org_id,
            category=category,
            total_questions=len(questions),
            correct_count=0,
            score_pct=0,
            badge_earned=None,
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        db.commit()

        return session, questions

    def get_session(
        self, db: Session, session_id: str
    ) -> Optional[QuizSession]:
        """Fetch quiz session by ID."""
        try:
            sid = uuid.UUID(session_id)
        except (ValueError, AttributeError):
            return None
        return db.query(QuizSession).filter(QuizSession.id == sid).first()

    def submit_answers(
        self,
        db: Session,
        session_id: str,
        answers: List[Dict],
    ) -> Dict:
        """
        Submit answers for a quiz session.
        Grades each answer, computes score, awards badge.

        Args:
            answers: [{"question_id": "uuid", "selected_option_index": 0}, ...]

        Returns:
            {
                "session_id": str,
                "category": str,
                "total_questions": int,
                "correct_count": int,
                "score_pct": int,
                "badge_earned": str or None,
                "results": [per-question result dicts],
            }

        Raises ValueError if session not found or already completed.
        """
        session = self.get_session(db, session_id)
        if not session:
            raise ValueError("Quiz session not found")

        if session.completed_at is not None:
            raise ValueError("Quiz session already completed")

        # Grade each answer
        results = []
        correct_count = 0

        for answer_data in answers:
            question_id = answer_data["question_id"]
            selected = answer_data["selected_option_index"]

            question = self.get_question_by_id(db, question_id)
            if not question:
                results.append({
                    "question_id": question_id,
                    "question_text": "Question not found",
                    "options": [],
                    "selected_option_index": selected,
                    "correct_option_index": -1,
                    "is_correct": False,
                    "explanation": "This question could not be found.",
                })
                continue

            is_correct = selected == question.correct_option_index
            if is_correct:
                correct_count += 1

            # Save answer record
            answer_record = QuizAnswer(
                id=uuid.uuid4(),
                quiz_session_id=session.id,
                question_id=question.id,
                selected_option_index=selected,
                is_correct=is_correct,
            )
            db.add(answer_record)

            results.append({
                "question_id": str(question.id),
                "question_text": question.question_text,
                "options": question.options,
                "selected_option_index": selected,
                "correct_option_index": question.correct_option_index,
                "is_correct": is_correct,
                "explanation": question.explanation,
            })

        # Compute score
        total = max(1, session.total_questions)
        score_pct = int(round(correct_count / total * 100))

        # Award badge
        badge = self._compute_badge(score_pct)

        # Update session
        session.correct_count = correct_count
        session.score_pct = score_pct
        session.badge_earned = badge
        session.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "session_id": str(session.id),
            "category": session.category,
            "total_questions": session.total_questions,
            "correct_count": correct_count,
            "score_pct": score_pct,
            "badge_earned": badge,
            "results": results,
        }

    # ═══════════════════════════════════════════
    # SCENARIOS
    # ═══════════════════════════════════════════

    def get_scenarios(
        self,
        db: Session,
        category: Optional[str] = None,
        language: str = "en",
    ) -> List[Scenario]:
        """Get active scenarios, optionally filtered by category."""
        query = db.query(Scenario).filter(
            Scenario.is_active == True,
            Scenario.language == language,
        )
        if category:
            query = query.filter(Scenario.category == category)
        return query.all()

    def get_scenario_by_id(
        self, db: Session, scenario_id: str
    ) -> Optional[Scenario]:
        """Fetch a single scenario by ID."""
        try:
            sid = uuid.UUID(scenario_id)
        except (ValueError, AttributeError):
            return None
        return db.query(Scenario).filter(Scenario.id == sid).first()

    # ═══════════════════════════════════════════
    # AWARENESS SUMMARY
    # ═══════════════════════════════════════════

    def get_user_summary(
        self,
        db: Session,
        user_id: uuid.UUID,
    ) -> Dict:
        """
        Compute aggregate awareness stats for a user.
        Returns category scores, badges, weakest area, etc.
        """
        # All completed sessions for this user
        sessions = (
            db.query(QuizSession)
            .filter(
                QuizSession.user_id == user_id,
                QuizSession.completed_at.isnot(None),
            )
            .all()
        )

        total_completed = len(sessions)

        if total_completed == 0:
            return {
                "user_id": str(user_id),
                "total_quizzes_completed": 0,
                "average_score_pct": 0,
                "badges": [],
                "category_scores": {},
                "weakest_category": None,
                "scenarios_completed": 0,
            }

        # Aggregate by category
        category_data = {}
        all_badges = []

        for session in sessions:
            cat = session.category
            if cat not in category_data:
                category_data[cat] = {
                    "attempts": 0,
                    "scores": [],
                    "best_score": 0,
                }

            category_data[cat]["attempts"] += 1
            category_data[cat]["scores"].append(session.score_pct)
            category_data[cat]["best_score"] = max(
                category_data[cat]["best_score"], session.score_pct
            )

            if session.badge_earned:
                all_badges.append({
                    "category": cat,
                    "badge": session.badge_earned,
                    "earned_at": session.completed_at.isoformat() if session.completed_at else None,
                })

        # Build category scores
        category_scores = {}
        for cat, data in category_data.items():
            avg = int(round(sum(data["scores"]) / len(data["scores"]))) if data["scores"] else 0
            category_scores[cat] = {
                "attempts": data["attempts"],
                "best_score": data["best_score"],
                "average_score": avg,
            }

        # Overall average
        all_scores = [s.score_pct for s in sessions]
        overall_avg = int(round(sum(all_scores) / len(all_scores))) if all_scores else 0

        # Weakest category (lowest average)
        weakest = None
        lowest_avg = 101
        for cat, scores in category_scores.items():
            if scores["average_score"] < lowest_avg:
                lowest_avg = scores["average_score"]
                weakest = cat

        # Deduplicate badges — keep best per category
        best_badges = {}
        badge_order = {"gold": 3, "silver": 2, "bronze": 1}
        for b in all_badges:
            cat = b["category"]
            if cat not in best_badges or badge_order.get(b["badge"], 0) > badge_order.get(best_badges[cat]["badge"], 0):
                best_badges[cat] = b
        unique_badges = list(best_badges.values())

        return {
            "user_id": str(user_id),
            "total_quizzes_completed": total_completed,
            "average_score_pct": overall_avg,
            "badges": unique_badges,
            "category_scores": category_scores,
            "weakest_category": weakest,
            "scenarios_completed": 0,  # TODO: track scenario completions
        }

    def get_org_quiz_metrics(
        self,
        db: Session,
        org_id: uuid.UUID,
    ) -> Dict:
        """Get aggregated quiz metrics for an organization."""
        sessions = (
            db.query(QuizSession)
            .filter(
                QuizSession.org_id == org_id,
                QuizSession.completed_at.isnot(None),
            )
            .all()
        )

        total = len(sessions)
        if total == 0:
            return {
                "total_sessions": 0,
                "average_score": 0,
                "weakest_category": None,
                "completion_rate": 0.0,
            }

        # All sessions including incomplete
        all_sessions = (
            db.query(QuizSession)
            .filter(QuizSession.org_id == org_id)
            .count()
        )

        scores = [s.score_pct for s in sessions]
        avg_score = int(round(sum(scores) / len(scores)))

        # Find weakest category
        cat_scores = {}
        for s in sessions:
            if s.category not in cat_scores:
                cat_scores[s.category] = []
            cat_scores[s.category].append(s.score_pct)

        weakest = None
        lowest = 101
        for cat, sc in cat_scores.items():
            avg = sum(sc) / len(sc)
            if avg < lowest:
                lowest = avg
                weakest = cat

        return {
            "total_sessions": total,
            "average_score": avg_score,
            "weakest_category": weakest,
            "completion_rate": round(total / max(1, all_sessions), 2),
        }

    # ═══════════════════════════════════════════
    # PRIVATE HELPERS
    # ═══════════════════════════════════════════

    @staticmethod
    def _compute_badge(score_pct: int) -> Optional[str]:
        """Determine badge based on score percentage."""
        if score_pct >= BADGE_THRESHOLDS["gold"]:
            return "gold"
        elif score_pct >= BADGE_THRESHOLDS["silver"]:
            return "silver"
        elif score_pct >= BADGE_THRESHOLDS["bronze"]:
            return "bronze"
        return None


# Singleton
quiz_service = QuizService()