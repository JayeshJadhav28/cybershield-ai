"""
CyberShield AI — Pydantic Schemas
All request/response schemas for API validation and serialization.
"""

from schemas.common import (
    RiskLabel,
    AnalysisType,
    QuizCategory,
    UserRole,
    OrgType,
    MembershipRole,
    BadgeLevel,
    ErrorResponse,
    PaginationParams,
    PaginatedResponse,
    HealthResponse,
)

from schemas.auth import (
    RequestOTPRequest,
    RequestOTPResponse,
    VerifyOTPRequest,
    TokenResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    LogoutResponse,
    UserResponse,
    UserProfileUpdate,
    UserStats,
    OrgMembershipSummary,
)

from schemas.analysis import (
    EmailAnalysisRequest,
    URLAnalysisRequest,
    QRDecodedContent,
    QRAnalysisResponse,
    AudioMetadata,
    AudioAnalysisResponse,
    VideoMetadata,
    VideoAnalysisResponse,
    AnalysisResponse,
    AnalysisExplanation,
    ExplanationHighlights,
    HighlightedPhrase,
    FlaggedURL,
    SenderAnalysis,
    ContributingFactor,
    AnalysisSummary,
    AnalysisDetailResponse,
    AnalysisListResponse,
    FrameAnalysisSummary,
    VideoExplanation,
)

from schemas.quiz import (
    QuizQuestionResponse,
    QuizQuestionFull,
    QuizQuestionsListResponse,
    StartQuizSessionRequest,
    QuizSessionResponse,
    QuizAnswerInput,
    SubmitQuizAnswersRequest,
    QuizAnswerResult,
    QuizResultResponse,
    ScenarioSummary,
    ScenarioListResponse,
    ScenarioStep,
    ScenarioDetailResponse,
    CategoryScore,
    BadgeInfo,
    AwarenessSummaryResponse,
)

from schemas.admin import (
    OrgMetricsResponse,
    AnalysisByType,
    RiskDistribution,
    QuizMetrics,
    ScoringConfigUpdate,
    ScoringConfigResponse,
)

from schemas.demo import (
    DemoSample,
    DemoSamplesResponse,
)