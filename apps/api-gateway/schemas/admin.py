"""
Admin and organization management schemas.
"""

from typing import Dict, Optional

from pydantic import BaseModel, Field

from schemas.common import QuizCategory


class AnalysisByType(BaseModel):
    """Breakdown of analyses by modality type."""
    email: int = 0
    url: int = 0
    qr: int = 0
    audio: int = 0
    video: int = 0


class RiskDistribution(BaseModel):
    """Distribution of risk labels across analyses."""
    safe: int = 0
    suspicious: int = 0
    dangerous: int = 0


class QuizMetrics(BaseModel):
    """Aggregated quiz metrics."""
    total_sessions: int = 0
    average_score: int = 0
    weakest_category: Optional[str] = None
    completion_rate: float = 0.0


class OrgMetricsResponse(BaseModel):
    """Organization-level analytics dashboard data."""
    org_id: Optional[str] = None
    period: str = "last_30_days"
    total_users: int = 0
    total_analyses: int = 0
    analyses_by_type: AnalysisByType = Field(default_factory=AnalysisByType)
    risk_distribution: RiskDistribution = Field(default_factory=RiskDistribution)
    quiz_metrics: QuizMetrics = Field(default_factory=QuizMetrics)


class ScoringConfigUpdate(BaseModel):
    """Request to update scoring configuration."""
    audio_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    video_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    phish_weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    safe_threshold: Optional[int] = Field(None, ge=0, le=100)
    dangerous_threshold: Optional[int] = Field(None, ge=0, le=100)


class ScoringConfigResponse(BaseModel):
    """Current scoring configuration."""
    id: str
    org_id: Optional[str] = None
    audio_weight: float
    video_weight: float
    phish_weight: float
    safe_threshold: int
    dangerous_threshold: int

    model_config = {"from_attributes": True}