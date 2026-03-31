"""
CyberShield AI Assistant — FastAPI routes.

POST /assistant/chat             → Conversational cybersecurity Q&A
POST /assistant/generate-quiz    → AI-generated quiz questions
GET  /assistant/news             → India cyber news feed
GET  /assistant/tip              → Random daily tip
GET  /assistant/resources        → Curated India cyber resources
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from dependencies import get_current_user_optional
from schemas.chat import (
    ChatRequest, ChatResponse,
    QuizGenRequest, QuizGenResponse, QuizGenQuestion,
    DailyTipResponse, NewsResponse, NewsItem,
)
from services.chatbot_service import chat_response, generate_quiz, get_daily_tip
from services.news_service import fetch_news, get_india_resources

router = APIRouter()

# ── Prompt-injection blocklist ───────────────────────────────────

_INJECTION_PHRASES = [
    "ignore previous instructions", "ignore all instructions",
    "you are now", "act as a hacker", "forget your rules",
    "system prompt", "reveal your prompt", "disregard",
    "pretend you are", "jailbreak",
]


@router.post("/chat", response_model=ChatResponse)
async def assistant_chat(
    request: ChatRequest,
    current_user=Depends(get_current_user_optional),
):
    """Chat with the cybersecurity assistant. Supports general, india_news, and quiz_gen modes."""
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    # Block prompt injection (skip for quiz_gen since topics can look unusual)
    if request.mode != "quiz_gen":
        last = messages[-1]["content"].lower()
        if any(p in last for p in _INJECTION_PHRASES):
            return ChatResponse(
                reply=(
                    "⚠️ I detected a potential prompt-injection attempt. "
                    "I only provide **defensive** cybersecurity guidance. "
                    "Please rephrase your question."
                ),
                facts=[],
                mode=request.mode,
            )

    result = await chat_response(messages=messages, mode=request.mode)

    return ChatResponse(
        reply=result["reply"],
        facts=result["facts"],
        mode=request.mode,
    )


@router.post("/generate-quiz", response_model=QuizGenResponse)
async def assistant_generate_quiz(
    request: QuizGenRequest,
    current_user=Depends(get_current_user_optional),
):
    """Generate cybersecurity quiz questions with AI."""
    raw = await generate_quiz(
        topic=request.topic,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
        category=request.category,
    )
    questions = [QuizGenQuestion(**q) for q in raw]
    return QuizGenResponse(topic=request.topic, questions=questions)


@router.get("/news", response_model=NewsResponse)
async def assistant_news(limit: int = 10, india_only: bool = True):
    """Fetch latest cybersecurity news."""
    raw = await fetch_news(limit=limit, india_only=india_only)
    articles = [NewsItem(**a) for a in raw]
    return NewsResponse(articles=articles, resources=get_india_resources())


@router.get("/tip", response_model=DailyTipResponse)
async def assistant_tip():
    """Random India cybersecurity tip."""
    return DailyTipResponse(**(await get_daily_tip()))


@router.get("/resources")
async def assistant_resources():
    """Curated India cyber resources."""
    return {"resources": get_india_resources()}