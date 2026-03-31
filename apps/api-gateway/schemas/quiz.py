"""
Quiz and awareness module schemas.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, field_validator

from schemas.common import QuizCategory, BadgeLevel


# ═══════════════════════════════════════════
# QUIZ QUESTIONS
# ═══════════════════════════════════════════

class QuizQuestionResponse(BaseModel):
    """A single quiz question (without answer for active quiz)."""
    id: str
    question_text: str
    options: List[str] = Field(..., min_length=2, max_length=6)
    difficulty: int = Field(..., ge=1, le=3)

    model_config = {"from_attributes": True}


class QuizQuestionFull(QuizQuestionResponse):
    """Full quiz question including answer and explanation (for results)."""
    correct_option_index: int
    explanation: str
    category: QuizCategory
    tags: List[str] = Field(default_factory=list)


class QuizQuestionsListResponse(BaseModel):
    """Response for quiz question listing."""
    category: QuizCategory
    language: str = "en"
    total_questions: int
    questions: List[QuizQuestionResponse]


# ═══════════════════════════════════════════
# QUIZ SESSIONS
# ═══════════════════════════════════════════

class StartQuizSessionRequest(BaseModel):
    """Request to start a new quiz session."""
    category: QuizCategory
    language: str = Field("en", max_length=5)

    model_config = {"json_schema_extra": {
        "example": {
            "category": "phishing",
            "language": "en"
        }
    }}


class QuizSessionResponse(BaseModel):
    """Response when a quiz session is created."""
    session_id: str
    category: QuizCategory
    total_questions: int
    questions: List[QuizQuestionResponse]


# ═══════════════════════════════════════════
# QUIZ ANSWERS
# ═══════════════════════════════════════════

class QuizAnswerInput(BaseModel):
    """A single answer submission."""
    question_id: str = Field(..., description="UUID of the question")
    selected_option_index: int = Field(
        ...,
        ge=0,
        le=3,
        description="Index of selected option (0-3)"
    )


class SubmitQuizAnswersRequest(BaseModel):
    """Request to submit all answers for a quiz session."""
    answers: List[QuizAnswerInput] = Field(
        ...,
        min_length=1,
        max_length=20,
        description="List of answers"
    )

    @field_validator("answers")
    @classmethod
    def validate_no_duplicate_questions(cls, v):
        question_ids = [a.question_id for a in v]
        if len(question_ids) != len(set(question_ids)):
            raise ValueError("Duplicate question IDs in answers")
        return v


class QuizAnswerResult(BaseModel):
    """Result for a single answered question."""
    question_id: str
    question_text: str
    options: List[str]
    selected_option_index: int
    correct_option_index: int
    is_correct: bool
    explanation: str


class QuizResultResponse(BaseModel):
    """Final quiz session result."""
    session_id: str
    category: QuizCategory
    total_questions: int
    correct_count: int
    score_pct: int = Field(..., ge=0, le=100)
    badge_earned: Optional[str] = None
    results: List[QuizAnswerResult]


# ═══════════════════════════════════════════
# SCENARIOS
# ═══════════════════════════════════════════

class ScenarioSummary(BaseModel):
    """Scenario list item."""
    id: str
    title: str
    description: str
    category: QuizCategory
    scenario_type: str
    estimated_time_minutes: int = 5

    model_config = {"from_attributes": True}


class ScenarioListResponse(BaseModel):
    """Response for scenario listing."""
    scenarios: List[ScenarioSummary]


class ScenarioStep(BaseModel):
    """A single step in a scenario."""
    step: int
    type: str = Field(..., description="message or choice")
    role: Optional[str] = None
    message: Optional[str] = None
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    feedback: Optional[Dict[str, str]] = None


class ScenarioDetailResponse(BaseModel):
    """Full scenario with steps."""
    id: str
    title: str
    description: str
    category: QuizCategory
    scenario_type: str
    steps: List[ScenarioStep]
    estimated_time_minutes: int = 5

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════
# AWARENESS SUMMARY
# ═══════════════════════════════════════════

class CategoryScore(BaseModel):
    """Score breakdown for a single quiz category."""
    attempts: int = 0
    best_score: int = 0
    average_score: int = 0


class BadgeInfo(BaseModel):
    """Badge earned by user."""
    category: QuizCategory
    badge: str
    earned_at: datetime


class AwarenessSummaryResponse(BaseModel):
    """Aggregate awareness stats for a user."""
    user_id: str
    total_quizzes_completed: int = 0
    average_score_pct: int = 0
    badges: List[BadgeInfo] = Field(default_factory=list)
    category_scores: Dict[str, CategoryScore] = Field(default_factory=dict)
    weakest_category: Optional[str] = None
    scenarios_completed: int = 0