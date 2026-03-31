"""
Analysis request/response schemas — email, URL, QR, audio, video.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field, HttpUrl, field_validator

from schemas.common import RiskLabel, AnalysisType


# ═══════════════════════════════════════════
# SHARED RESULT SCHEMAS
# ═══════════════════════════════════════════

class HighlightedPhrase(BaseModel):
    """A flagged phrase from the analyzed content."""
    text: str = Field(..., description="The suspicious phrase")
    reason: str = Field(..., description="Why this phrase is flagged")


class FlaggedURL(BaseModel):
    """A flagged URL from the analyzed content."""
    url: str
    flags: List[str] = Field(..., description="List of suspicious indicators")


class SenderAnalysis(BaseModel):
    """Analysis of the email sender."""
    email: str
    flags: List[str] = Field(default_factory=list)


class ContributingFactor(BaseModel):
    """A factor that contributed to the risk score."""
    factor: str = Field(..., description="Factor identifier")
    weight: float = Field(0.0, ge=0.0, le=1.0, description="Contribution weight")
    description: str = Field("", description="Human-readable description")
    raw_score: Optional[float] = Field(None, description="Raw model score if applicable")


class ExplanationHighlights(BaseModel):
    """Highlighted elements in the explanation."""
    phrases: List[HighlightedPhrase] = Field(default_factory=list)
    urls: List[FlaggedURL] = Field(default_factory=list)
    sender: Optional[SenderAnalysis] = None
    domain_analysis: Optional[Dict[str, Any]] = None


class AnalysisExplanation(BaseModel):
    """Explainable AI output for any analysis."""
    summary: str = Field(..., description="One-paragraph human-readable summary")
    highlights: Optional[ExplanationHighlights] = None
    contributing_factors: List[ContributingFactor] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    """Standard response for all analysis endpoints."""
    analysis_id: str = Field(..., description="Unique analysis ID (UUID)")
    risk_score: int = Field(..., ge=0, le=100, description="Risk score 0-100")
    risk_label: RiskLabel = Field(..., description="Risk classification")
    processing_time_ms: int = Field(..., description="Processing latency in milliseconds")
    explanation: AnalysisExplanation
    tip: str = Field(..., description="Contextual safety advice")

    model_config = {"json_schema_extra": {
        "example": {
            "analysis_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "risk_score": 82,
            "risk_label": "dangerous",
            "processing_time_ms": 1240,
            "explanation": {
                "summary": "This email shows strong phishing indicators.",
                "highlights": {
                    "phrases": [{"text": "URGENT", "reason": "Urgency tactic"}],
                    "urls": [{"url": "http://fake.com", "flags": ["Non-HTTPS"]}],
                },
                "contributing_factors": [
                    {"factor": "suspicious_domain", "weight": 0.3, "description": "Fake domain"}
                ]
            },
            "tip": "Never share OTP or passwords via email links."
        }
    }}


# ═══════════════════════════════════════════
# EMAIL ANALYSIS
# ═══════════════════════════════════════════

class EmailAnalysisRequest(BaseModel):
    """Request to analyze a suspicious email."""
    subject: str = Field(
        ...,
        max_length=500,
        description="Email subject line"
    )
    body: str = Field(
        ...,
        max_length=50000,
        description="Email body text"
    )
    sender: str = Field(
        ...,
        max_length=255,
        description="Sender email address"
    )
    urls: Optional[List[str]] = Field(
        default_factory=list,
        max_length=20,
        description="URLs found in the email"
    )

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Subject cannot be empty or whitespace only")
        return v.strip()

    @field_validator("body")
    @classmethod
    def body_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Body cannot be empty or whitespace only")
        return v.strip()

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v):
        v = v.strip()
        if not v or "@" not in v:
            raise ValueError("Sender must be a valid email address")
        return v

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v):
        if v:
            cleaned = []
            for url in v:
                url = url.strip()
                if url:
                    cleaned.append(url)
            return cleaned
        return []

    model_config = {"json_schema_extra": {
        "example": {
            "subject": "URGENT: Your account will be suspended",
            "body": "Dear Customer, verify your account immediately...",
            "sender": "security@sbi-alerts.xyz",
            "urls": ["http://sbi-verify-account.xyz/login"]
        }
    }}


# ═══════════════════════════════════════════
# URL ANALYSIS
# ═══════════════════════════════════════════

class URLAnalysisRequest(BaseModel):
    """Request to analyze a suspicious URL."""
    url: str = Field(
        ...,
        max_length=2048,
        description="URL to analyze"
    )

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        # Basic URL validation — allow with or without scheme
        if not v.startswith(("http://", "https://", "upi://")):
            v = "https://" + v
        return v

    model_config = {"json_schema_extra": {
        "example": {"url": "https://secure-payment-verify.com/upi/confirm"}
    }}


# ═══════════════════════════════════════════
# QR ANALYSIS
# ═══════════════════════════════════════════

class QRDecodedContent(BaseModel):
    """Decoded QR code content."""
    raw: str = Field(..., description="Raw decoded string")
    type: str = Field(..., description="Content type: upi, url, text, unknown")
    parsed: Optional[Dict[str, Any]] = Field(
        None,
        description="Parsed content (UPI fields, URL parts, etc.)"
    )


class QRAnalysisResponse(BaseModel):
    """Response for QR code analysis."""
    analysis_id: str
    decoded: QRDecodedContent
    risk_score: int = Field(..., ge=0, le=100)
    risk_label: RiskLabel
    processing_time_ms: int
    explanation: AnalysisExplanation
    tip: str


# ═══════════════════════════════════════════
# AUDIO ANALYSIS
# ═══════════════════════════════════════════

class AudioMetadata(BaseModel):
    """Metadata extracted from audio file."""
    duration_seconds: float
    sample_rate: int
    format: str


class AudioAnalysisResponse(BaseModel):
    """Response for audio deepfake analysis."""
    analysis_id: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_label: RiskLabel
    processing_time_ms: int
    audio_metadata: AudioMetadata
    explanation: AnalysisExplanation
    tip: str


# ═══════════════════════════════════════════
# VIDEO ANALYSIS
# ═══════════════════════════════════════════

class VideoMetadata(BaseModel):
    """Metadata extracted from video file."""
    duration_seconds: float
    resolution: str
    fps: int
    frames_analyzed: int


class FrameAnalysisSummary(BaseModel):
    """Summary of per-frame deepfake analysis."""
    total_frames: int
    suspicious_frames: int
    anomaly_distribution: str = ""


class VideoExplanation(AnalysisExplanation):
    """Extended explanation for video with frame analysis."""
    frame_analysis: Optional[FrameAnalysisSummary] = None


class VideoAnalysisResponse(BaseModel):
    """Response for video deepfake analysis."""
    analysis_id: str
    risk_score: int = Field(..., ge=0, le=100)
    risk_label: RiskLabel
    processing_time_ms: int
    video_metadata: VideoMetadata
    explanation: VideoExplanation
    tip: str


# ═══════════════════════════════════════════
# ANALYSIS HISTORY (for reports)
# ═══════════════════════════════════════════

class AnalysisSummary(BaseModel):
    """Summary of a past analysis for list views."""
    id: str
    type: AnalysisType
    risk_score: int
    risk_label: RiskLabel
    explanation_summary: str
    processing_time_ms: Optional[int] = None
    is_demo: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisDetailResponse(BaseModel):
    """Full detail of a past analysis."""
    id: str
    type: AnalysisType
    risk_score: int
    risk_label: RiskLabel
    explanation_summary: str
    model_scores: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[int] = None
    raw_metadata: Optional[Dict[str, Any]] = None
    highlighted_elements: Optional[List[Dict[str, Any]]] = None
    contributing_factors: Optional[List[Dict[str, Any]]] = None
    is_demo: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalysisListResponse(BaseModel):
    """Paginated list of analyses."""
    total: int
    page: int
    limit: int
    analyses: List[AnalysisSummary]