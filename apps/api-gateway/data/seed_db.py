"""
Database seeding script — loads quiz questions, scenarios, and default config.
Run with: python -m data.seed_db
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models.quiz import QuizQuestion, Scenario
from models.config import ScoringConfig


def seed_quiz_questions(db):
    """Load quiz questions from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), "seed_quizzes.json")

    if not os.path.exists(json_path):
        print(f"⚠️  Quiz seed file not found: {json_path}")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        questions_data = json.load(f)

    # Check if already seeded
    existing = db.query(QuizQuestion).count()
    if existing > 0:
        print(f"ℹ️  Quiz questions already seeded ({existing} exist). Skipping.")
        return existing

    count = 0
    for q_data in questions_data:
        question = QuizQuestion(
            id=uuid.uuid4(),
            category=q_data["category"],
            difficulty=q_data.get("difficulty", 1),
            question_text=q_data["question_text"],
            options=q_data["options"],
            correct_option_index=q_data["correct_option_index"],
            explanation=q_data["explanation"],
            language=q_data.get("language", "en"),
            tags=q_data.get("tags", []),
            is_active=True,
        )
        db.add(question)
        count += 1

    db.commit()
    print(f"✅ Seeded {count} quiz questions")
    return count


def seed_scenarios(db):
    """Load scenarios from JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), "seed_scenarios.json")

    if not os.path.exists(json_path):
        print(f"⚠️  Scenario seed file not found: {json_path}")
        return 0

    with open(json_path, "r", encoding="utf-8") as f:
        scenarios_data = json.load(f)

    existing = db.query(Scenario).count()
    if existing > 0:
        print(f"ℹ️  Scenarios already seeded ({existing} exist). Skipping.")
        return existing

    count = 0
    for s_data in scenarios_data:
        scenario = Scenario(
            id=uuid.uuid4(),
            title=s_data["title"],
            description=s_data["description"],
            category=s_data["category"],
            scenario_type=s_data.get("scenario_type", "chat"),
            steps=s_data["steps"],
            language=s_data.get("language", "en"),
            estimated_time_minutes=s_data.get("estimated_time_minutes", 5),
            is_active=True,
        )
        db.add(scenario)
        count += 1

    db.commit()
    print(f"✅ Seeded {count} scenarios")
    return count


def seed_default_scoring_config(db):
    """Ensure global default scoring config exists."""
    existing = (
        db.query(ScoringConfig)
        .filter(ScoringConfig.org_id.is_(None), ScoringConfig.is_active == True)
        .first()
    )

    if existing:
        print("ℹ️  Default scoring config already exists. Skipping.")
        return

    config = ScoringConfig(
        id=uuid.uuid4(),
        org_id=None,
        audio_weight=0.35,
        video_weight=0.35,
        phish_weight=0.30,
        safe_threshold=30,
        dangerous_threshold=70,
        is_active=True,
    )
    db.add(config)
    db.commit()
    print("✅ Seeded default scoring config")


def create_demo_phishing_model():
    """Create a demo phishing ML model if not exists."""
    try:
        from ml.phish_model import PhishingModel
        model = PhishingModel()
        if not model.is_trained:
            print("🤖 Creating demo phishing model...")
            model.create_demo_model()
    except Exception as e:
        print(f"⚠️  Could not create demo phishing model: {e}")


def main():
    """Run all seed operations."""
    print("")
    print("=" * 50)
    print("  🌱 CyberShield AI — Database Seeding")
    print("=" * 50)
    print("")

    db = SessionLocal()

    try:
        # Seed data
        q_count = seed_quiz_questions(db)
        s_count = seed_scenarios(db)
        seed_default_scoring_config(db)

        # Create demo ML model
        create_demo_phishing_model()

        print("")
        print("=" * 50)
        print(f"  ✅ Seeding complete!")
        print(f"     Quiz questions: {q_count}")
        print(f"     Scenarios: {s_count}")
        print("=" * 50)
        print("")

    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()