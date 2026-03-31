"""
Awareness routes — quizzes, scenarios, learning resources, user summary.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user_optional, get_current_user_required, rate_limit_dependency
from services.quiz_service import quiz_service

from schemas.quiz import (
    QuizQuestionResponse,
    QuizQuestionsListResponse,
    StartQuizSessionRequest,
    QuizSessionResponse,
    SubmitQuizAnswersRequest,
    QuizAnswerResult,
    QuizResultResponse,
    ScenarioSummary,
    ScenarioListResponse,
    ScenarioDetailResponse,
    ScenarioStep,
    AwarenessSummaryResponse,
    CategoryScore,
    BadgeInfo,
)
from schemas.common import QuizCategory

router = APIRouter()


# ═══════════════════════════════════════════
# QUIZ QUESTIONS
# ═══════════════════════════════════════════

@router.get(
    "/quizzes",
    response_model=QuizQuestionsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get quiz questions",
    description="Fetch randomized quiz questions for a category. No auth required.",
)
async def get_quizzes(
    category: QuizCategory = Query(..., description="Quiz category"),
    language: str = Query("en", max_length=5, description="Language code"),
    db: Session = Depends(get_db),
):
    questions = quiz_service.get_questions(db, category.value, language)

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No questions found for category '{category.value}' in language '{language}'",
        )

    return QuizQuestionsListResponse(
        category=category,
        language=language,
        total_questions=len(questions),
        questions=[
            QuizQuestionResponse(
                id=str(q.id),
                question_text=q.question_text,
                options=q.options,
                difficulty=q.difficulty,
            )
            for q in questions
        ],
    )


@router.get(
    "/quizzes/categories",
    status_code=status.HTTP_200_OK,
    summary="Get available quiz categories",
    description="Returns categories that have active questions with counts.",
)
async def get_categories(
    language: str = Query("en", max_length=5),
    db: Session = Depends(get_db),
):
    categories = quiz_service.get_available_categories(db, language)
    return {"categories": categories}


# ═══════════════════════════════════════════
# QUIZ SESSIONS
# ═══════════════════════════════════════════

@router.post(
    "/quiz-sessions",
    response_model=QuizSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a quiz session",
    description="Create a new quiz session. Returns session ID and questions. Works without auth.",
)
async def start_quiz_session(
    request: StartQuizSessionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
    _rate_limit=Depends(rate_limit_dependency),
):
    user_id = current_user.id if current_user else None

    try:
        session, questions = quiz_service.start_session(
            db=db,
            category=request.category.value,
            language=request.language,
            user_id=user_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    return QuizSessionResponse(
        session_id=str(session.id),
        category=request.category,
        total_questions=session.total_questions,
        questions=[
            QuizQuestionResponse(
                id=str(q.id),
                question_text=q.question_text,
                options=q.options,
                difficulty=q.difficulty,
            )
            for q in questions
        ],
    )


@router.post(
    "/quiz-sessions/{session_id}/answers",
    response_model=QuizResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit quiz answers",
    description="Submit all answers for a quiz session. Returns graded results with explanations and badge.",
)
async def submit_quiz_answers(
    session_id: str,
    request: SubmitQuizAnswersRequest,
    db: Session = Depends(get_db),
    _rate_limit=Depends(rate_limit_dependency),
):
    answers_data = [
        {
            "question_id": a.question_id,
            "selected_option_index": a.selected_option_index,
        }
        for a in request.answers
    ]

    try:
        result = quiz_service.submit_answers(
            db=db,
            session_id=session_id,
            answers=answers_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    return QuizResultResponse(
        session_id=result["session_id"],
        category=result["category"],
        total_questions=result["total_questions"],
        correct_count=result["correct_count"],
        score_pct=result["score_pct"],
        badge_earned=result["badge_earned"],
        results=[
            QuizAnswerResult(**r) for r in result["results"]
        ],
    )


# ═══════════════════════════════════════════
# SCENARIOS
# ═══════════════════════════════════════════

@router.get(
    "/scenarios",
    response_model=ScenarioListResponse,
    status_code=status.HTTP_200_OK,
    summary="List available scenarios",
    description="Get all active scenario simulations, optionally filtered by category.",
)
async def list_scenarios(
    category: QuizCategory = Query(None, description="Filter by category"),
    language: str = Query("en", max_length=5),
    db: Session = Depends(get_db),
):
    cat_value = category.value if category else None
    scenarios = quiz_service.get_scenarios(db, category=cat_value, language=language)

    return ScenarioListResponse(
        scenarios=[
            ScenarioSummary(
                id=str(s.id),
                title=s.title,
                description=s.description,
                category=s.category,
                scenario_type=s.scenario_type,
                estimated_time_minutes=s.estimated_time_minutes or 5,
            )
            for s in scenarios
        ]
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get scenario details",
    description="Get full scenario with all interactive steps.",
)
async def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db),
):
    scenario = quiz_service.get_scenario_by_id(db, scenario_id)

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    steps = []
    for i, step_data in enumerate(scenario.steps or []):
        steps.append(ScenarioStep(
            step=i + 1,
            type=step_data.get("type", "message"),
            role=step_data.get("role"),
            message=step_data.get("message"),
            prompt=step_data.get("prompt"),
            options=step_data.get("options"),
            correct_index=step_data.get("correct_index"),
            feedback=step_data.get("feedback"),
        ))

    return ScenarioDetailResponse(
        id=str(scenario.id),
        title=scenario.title,
        description=scenario.description,
        category=scenario.category,
        scenario_type=scenario.scenario_type,
        steps=steps,
        estimated_time_minutes=scenario.estimated_time_minutes or 5,
    )


# ═══════════════════════════════════════════
# AWARENESS SUMMARY
# ═══════════════════════════════════════════

@router.get(
    "/summary",
    response_model=AwarenessSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get awareness summary",
    description="Returns aggregated quiz and scenario stats for the authenticated user.",
)
async def get_awareness_summary(
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    summary = quiz_service.get_user_summary(db, user_id=current_user.id)

    badges = []
    for b in summary.get("badges", []):
        badges.append(BadgeInfo(
            category=b["category"],
            badge=b["badge"],
            earned_at=b.get("earned_at", ""),
        ))

    category_scores = {}
    for cat, scores in summary.get("category_scores", {}).items():
        category_scores[cat] = CategoryScore(
            attempts=scores["attempts"],
            best_score=scores["best_score"],
            average_score=scores["average_score"],
        )

    return AwarenessSummaryResponse(
        user_id=summary["user_id"],
        total_quizzes_completed=summary["total_quizzes_completed"],
        average_score_pct=summary["average_score_pct"],
        badges=badges,
        category_scores=category_scores,
        weakest_category=summary.get("weakest_category"),
        scenarios_completed=summary.get("scenarios_completed", 0),
    )