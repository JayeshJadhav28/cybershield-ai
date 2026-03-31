"""
Authentication request/response schemas.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, EmailStr

from schemas.common import UserRole


# ── OTP ──

class RequestOTPRequest(BaseModel):
    """Request to send an OTP."""
    email: EmailStr = Field(..., description="User email address")
    purpose: str = Field(
        "login",
        pattern="^(login|signup|verify)$",
        description="OTP purpose: login, signup, or verify"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "email": "user@example.com",
            "purpose": "login"
        }
    }}


class RequestOTPResponse(BaseModel):
    """Response after OTP is sent."""
    status: str = "sent"
    message: str
    expires_in_seconds: int = 300
    dev_otp: Optional[str] = None


class VerifyOTPRequest(BaseModel):
    """Request to verify an OTP."""
    email: EmailStr = Field(..., description="Email the OTP was sent to")
    otp: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern="^[0-9]{6}$",
        description="6-digit OTP code"
    )
    purpose: str = Field(
        "login",
        pattern="^(login|signup|verify)$"
    )

    model_config = {"json_schema_extra": {
        "example": {
            "email": "user@example.com",
            "otp": "482916",
            "purpose": "login"
        }
    }}


# ── Tokens ──

class TokenResponse(BaseModel):
    """JWT token pair returned after successful auth."""
    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="Refresh token (long-lived)")
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access token TTL in seconds")
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Request to refresh an access token."""
    refresh_token: str = Field(..., description="Valid refresh token")


class RefreshTokenResponse(BaseModel):
    """New access token after refresh."""
    access_token: str
    expires_in: int


class LogoutResponse(BaseModel):
    status: str = "logged_out"


# ── User ──

class OrgMembershipSummary(BaseModel):
    """Organization membership summary for user profile."""
    id: str
    name: str
    role: str


class UserStats(BaseModel):
    """Quick stats for user profile."""
    total_analyses: int = 0
    quizzes_completed: int = 0
    badges_earned: List[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    display_name: Optional[str] = None
    role: UserRole
    email_verified: bool = False
    organizations: List[OrgMembershipSummary] = Field(default_factory=list)
    stats: Optional[UserStats] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Request to update user profile."""
    display_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)