"""
Shared schema types used across multiple modules.
"""

from datetime import datetime
from typing import Optional, Any
from enum import Enum

from pydantic import BaseModel, Field


# ── Enums ──

class RiskLabel(str, Enum):
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    DANGEROUS = "dangerous"


class AnalysisType(str, Enum):
    EMAIL = "email"
    URL = "url"
    QR = "qr"
    AUDIO = "audio"
    VIDEO = "video"


class QuizCategory(str, Enum):
    DEEPFAKE = "deepfake"
    PHISHING = "phishing"
    UPI_QR = "upi_qr"
    KYC_OTP = "kyc_otp"
    GENERAL = "general"


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    ORG_ADMIN = "org_admin"


class OrgType(str, Enum):
    BANK = "bank"
    COLLEGE = "college"
    GOVT = "govt"
    OTHER = "other"


class MembershipRole(str, Enum):
    MEMBER = "member"
    COORDINATOR = "coordinator"
    ADMIN = "admin"


class BadgeLevel(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"


# ── Base Response Schemas ──

class TimestampMixin(BaseModel):
    created_at: datetime


class ErrorResponse(BaseModel):
    """Standard error response body."""
    error: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Any] = Field(None, description="Additional error details")
    path: Optional[str] = None
    timestamp: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "error": "validation_error",
            "message": "Request validation failed",
            "details": [{"field": "email", "message": "Invalid email format"}],
        }
    }}


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = Field(1, ge=1, description="Page number")
    limit: int = Field(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""
    total: int
    page: int
    limit: int
    items: list = Field(default_factory=list)

    @property
    def total_pages(self) -> int:
        return max(1, -(-self.total // self.limit))  # Ceiling division

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    environment: str