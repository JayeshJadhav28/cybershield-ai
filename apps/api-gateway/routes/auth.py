"""
Authentication routes — OTP flow, token management, user profile.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from dependencies import get_current_user_required, get_current_user_optional, rate_limit_dependency
from services.auth_service import auth_service
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

router = APIRouter()


# ═══════════════════════════════════════════
# OTP ENDPOINTS
# ═══════════════════════════════════════════

@router.post(
    "/request-otp",
    response_model=RequestOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Request an OTP",
    description="Send a 6-digit OTP to the provided email address. Rate limited to 1 request per 60 seconds per email.",
)
async def request_otp(
    request: RequestOTPRequest,
    db: Session = Depends(get_db),
    _rate_limit=Depends(rate_limit_dependency),
):
    try:
        message, expires_in = auth_service.request_otp(
            db=db,
            email=request.email,
            purpose=request.purpose,
        )
        dev_otp = None
        if not settings.SMTP_HOST:
            dev_otp = auth_service.get_dev_otp_for_email(request.email)
        return RequestOTPResponse(
            status="sent",
            message=message,
            expires_in_seconds=expires_in,
            dev_otp=dev_otp,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )


@router.post(
    "/verify-otp",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify OTP and authenticate",
    description="Verify the 6-digit OTP. Returns JWT access token and refresh token on success. Auto-creates user account on first login.",
)
async def verify_otp(
    request: VerifyOTPRequest,
    db: Session = Depends(get_db),
    _rate_limit=Depends(rate_limit_dependency),
):
    try:
        user, access_token, refresh_token, expires_in = (
            auth_service.verify_otp_and_authenticate(
                db=db,
                email=request.email,
                otp_plain=request.otp,
                purpose=request.purpose,
            )
        )

        # Build user response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            display_name=user.display_name,
            role=user.role,
            email_verified=user.email_verified,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=expires_in,
            user=user_response,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


# ═══════════════════════════════════════════
# TOKEN MANAGEMENT
# ═══════════════════════════════════════════

@router.post(
    "/refresh",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token.",
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    try:
        access_token, expires_in = auth_service.refresh_access_token(
            db=db,
            refresh_token_str=request.refresh_token,
        )
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=expires_in,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout",
    description="Revoke all refresh tokens for the current user.",
)
async def logout(
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    auth_service.logout(db=db, user_id=current_user.id)
    return LogoutResponse(status="logged_out")


# ═══════════════════════════════════════════
# USER PROFILE
# ═══════════════════════════════════════════

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Returns the authenticated user's profile including org memberships and stats.",
)
async def get_me(
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    profile = auth_service.get_user_profile(db=db, user=current_user)
    return UserResponse(**profile)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update display name and/or phone number.",
)
async def update_me(
    update: UserProfileUpdate,
    current_user=Depends(get_current_user_required),
    db: Session = Depends(get_db),
):
    user = auth_service.update_profile(
        db=db,
        user=current_user,
        display_name=update.display_name,
        phone=update.phone,
    )
    profile = auth_service.get_user_profile(db=db, user=user)
    return UserResponse(**profile)