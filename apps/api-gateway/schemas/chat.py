"""Pydantic schemas for CyberShield Assistant endpoints."""

from __future__ import annotations
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=10_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1, max_length=50)
    # ✅ FIX: added quiz_gen to the pattern
    mode: str = Field(
        default="general",
        pattern="^(general|india_news|quiz_gen)$",
    )


class ChatResponse(BaseModel):
    reply: str
    facts: list[str] = []
    mode: str


class QuizGenRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=200)
    num_questions: int = Field(default=5, ge=1, le=10)
    difficulty: int = Field(default=1, ge=1, le=3)
    category: str = Field(
        default="general",
        pattern="^(deepfake|phishing|upi_qr|kyc_otp|general)$",
    )


class QuizGenQuestion(BaseModel):
    question_text: str
    options: list[str]
    correct_option_index: int
    explanation: str
    difficulty: int
    category: str


class QuizGenResponse(BaseModel):
    topic: str
    questions: list[QuizGenQuestion]
    generated_by: str = "ai"


class DailyTipResponse(BaseModel):
    tip: str
    source: str


class NewsItem(BaseModel):
    title: str
    summary: str
    url: str
    source: str
    published: str
    india_relevant: bool = False


class NewsResponse(BaseModel):
    articles: list[NewsItem]
    resources: list[dict] = []