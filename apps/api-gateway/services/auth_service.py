"""
Authentication service — OTP lifecycle, JWT management, user creation.
"""

import uuid
import secrets
import asyncio
from services.email_service import send_otp_email
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from config import settings
from models.user import User
from models.auth import OTPToken, RefreshToken
from utils.security import (
    generate_otp,
    hash_otp,
    verify_otp,
    create_access_token,
    generate_refresh_token_string,
    hash_password,
    verify_password,
)


class AuthService:
    """Handles all authentication operations."""

    def __init__(self):
        # Development-only cache for the latest plain OTP per email.
        self._dev_otp_cache: dict[str, str] = {}

    # ═══════════════════════════════════════════
    # OTP OPERATIONS
    # ═══════════════════════════════════════════

    def request_otp(
        self,
        db: Session,
        email: str,
        purpose: str = "login",
    ) -> Tuple[str, int]:
        """
        Generate and store an OTP for the given email.
        Returns (masked_message, expires_in_seconds).
        Raises ValueError if rate limited.
        """
        email = email.lower().strip()
        now = datetime.now(timezone.utc)

        # Rate limit: no more than 1 OTP per 60 seconds per email
        recent_otp = (
            db.query(OTPToken)
            .filter(
                OTPToken.email == email,
                OTPToken.created_at > now - timedelta(seconds=60),
            )
            .first()
        )
        if recent_otp:
            raise ValueError("Please wait 60 seconds before requesting another OTP")

        # Invalidate any existing unused OTPs for this email
        db.query(OTPToken).filter(
            OTPToken.email == email,
            OTPToken.used_at.is_(None),
        ).delete()

        # Generate new OTP
        otp_plain = generate_otp(length=6)
        self._dev_otp_cache[email] = otp_plain
        otp_hashed = hash_otp(otp_plain)
        expires_at = now + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)

        otp_token = OTPToken(
            id=uuid.uuid4(),
            email=email,
            otp_hash=otp_hashed,
            purpose=purpose,
            attempts=0,
            max_attempts=3,
            expires_at=expires_at,
        )
        db.add(otp_token)
        db.commit()

        # Send OTP (MVP: print to console; production: email service)
        self._deliver_otp(email, otp_plain, purpose)

        expires_in = settings.OTP_EXPIRE_MINUTES * 60
        masked_email = self._mask_email(email)
        return f"OTP sent to {masked_email}", expires_in

    def get_dev_otp_for_email(self, email: str) -> Optional[str]:
        """Return the latest generated plain OTP for local development workflows."""
        return self._dev_otp_cache.get(email.lower().strip())

    def verify_otp_and_authenticate(
        self,
        db: Session,
        email: str,
        otp_plain: str,
        purpose: str = "login",
    ) -> Tuple[User, str, str, int]:
        """
        Verify OTP and return authenticated user with tokens.
        Returns (user, access_token, refresh_token, expires_in).
        Raises ValueError on failure.
        """
        email = email.lower().strip()
        now = datetime.now(timezone.utc)

        # Find the most recent valid OTP for this email
        otp_record = (
            db.query(OTPToken)
            .filter(
                OTPToken.email == email,
                OTPToken.purpose == purpose,
                OTPToken.used_at.is_(None),
                OTPToken.expires_at > now,
            )
            .order_by(OTPToken.created_at.desc())
            .first()
        )

        if not otp_record:
            raise ValueError("No valid OTP found. Please request a new one.")

        # Check attempt limit
        if otp_record.attempts >= otp_record.max_attempts:
            raise ValueError("Maximum OTP attempts exceeded. Please request a new OTP.")

        # Verify OTP
        if not verify_otp(otp_plain, otp_record.otp_hash):
            otp_record.attempts += 1
            db.commit()
            remaining = otp_record.max_attempts - otp_record.attempts
            raise ValueError(f"Invalid OTP. {remaining} attempt(s) remaining.")

        # Mark OTP as used
        otp_record.used_at = now
        db.commit()

        # Get or create user
        user = self._get_or_create_user(db, email, purpose)

        # Update last login
        user.last_login_at = now
        if purpose in ("signup", "verify"):
            user.email_verified = True
        db.commit()

        # Generate tokens
        access_token, refresh_token, expires_in = self._create_token_pair(db, user)

        return user, access_token, refresh_token, expires_in

    # ═══════════════════════════════════════════
    # TOKEN OPERATIONS
    # ═══════════════════════════════════════════

    def refresh_access_token(
        self,
        db: Session,
        refresh_token_str: str,
    ) -> Tuple[str, int]:
        """
        Issue a new access token using a valid refresh token.
        Returns (new_access_token, expires_in).
        Raises ValueError if refresh token is invalid.
        """
        now = datetime.now(timezone.utc)

        # Find refresh token in database
        # We store hashed, but for MVP simplicity we match directly
        # In production, hash the incoming token and compare
        refresh_record = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token_hash == self._hash_token(refresh_token_str),
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
            .first()
        )

        if not refresh_record:
            raise ValueError("Invalid or expired refresh token")

        # Get user
        user = db.query(User).filter(User.id == refresh_record.user_id).first()
        if not user or not user.is_active:
            raise ValueError("User account is inactive")

        # Create new access token
        access_token = create_access_token(
            data=self._build_jwt_payload(user),
        )
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return access_token, expires_in

    def logout(self, db: Session, user_id: uuid.UUID) -> None:
        """Revoke all refresh tokens for a user."""
        now = datetime.now(timezone.utc)
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
        ).update({"revoked_at": now})
        db.commit()

    def get_user_by_id(self, db: Session, user_id: uuid.UUID) -> Optional[User]:
        """Fetch user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_user_profile(self, db: Session, user: User) -> dict:
        """Build full user profile with stats and org memberships."""
        from models.analysis import Analysis
        from models.quiz import QuizSession

        # Count analyses
        total_analyses = (
            db.query(Analysis)
            .filter(Analysis.user_id == user.id)
            .count()
        )

        # Count completed quizzes
        quizzes_completed = (
            db.query(QuizSession)
            .filter(
                QuizSession.user_id == user.id,
                QuizSession.completed_at.isnot(None),
            )
            .count()
        )

        # Collect badges
        badge_sessions = (
            db.query(QuizSession)
            .filter(
                QuizSession.user_id == user.id,
                QuizSession.badge_earned.isnot(None),
            )
            .all()
        )
        badges = list(set(
            f"{s.category}_{s.badge_earned}" for s in badge_sessions
        ))

        # Organization memberships
        orgs = []
        for membership in user.org_memberships:
            orgs.append({
                "id": str(membership.organization.id),
                "name": membership.organization.name,
                "role": membership.role,
            })

        return {
            "id": str(user.id),
            "email": user.email,
            "display_name": user.display_name,
            "role": user.role,
            "email_verified": user.email_verified,
            "organizations": orgs,
            "stats": {
                "total_analyses": total_analyses,
                "quizzes_completed": quizzes_completed,
                "badges_earned": badges,
            },
            "created_at": user.created_at,
        }

    def update_profile(
        self, db: Session, user: User, display_name: Optional[str], phone: Optional[str]
    ) -> User:
        """Update user profile fields."""
        if display_name is not None:
            user.display_name = display_name
        if phone is not None:
            user.phone = phone
        db.commit()
        db.refresh(user)
        return user

    # ═══════════════════════════════════════════
    # PRIVATE HELPERS
    # ═══════════════════════════════════════════

    def _get_or_create_user(self, db: Session, email: str, purpose: str) -> User:
        """Find existing user or create new one."""
        user = db.query(User).filter(User.email == email).first()

        if user:
            return user

        # Auto-create user on first login/signup
        user = User(
            id=uuid.uuid4(),
            email=email,
            display_name=email.split("@")[0],
            role="user",
            email_verified=(purpose in ("signup", "verify")),
        )
        db.add(user)
        db.flush()  # Get the ID without committing
        return user

    def _create_token_pair(
        self, db: Session, user: User
    ) -> Tuple[str, str, int]:
        """Create access + refresh token pair."""
        # Access token (JWT)
        access_token = create_access_token(
            data=self._build_jwt_payload(user),
        )
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        # Refresh token (opaque string stored in DB)
        refresh_token_plain = generate_refresh_token_string()
        refresh_token_hashed = self._hash_token(refresh_token_plain)

        refresh_record = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash=refresh_token_hashed,
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(refresh_record)
        db.flush()

        return access_token, refresh_token_plain, expires_in

    def _build_jwt_payload(self, user: User) -> dict:
        """Build JWT claims from user."""
        orgs = []
        for membership in user.org_memberships:
            orgs.append({
                "id": str(membership.org_id),
                "role": membership.role,
            })

        return {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "orgs": orgs,
        }

    def _deliver_otp(self, email: str, otp: str, purpose: str) -> None:
        """
        Deliver OTP to user using email service (async).
        """
        # Schedule async email sending in background
        asyncio.create_task(send_otp_email(to_email=email, otp=otp, purpose=purpose))

    def _send_email_otp(self, email: str, otp: str, purpose: str) -> None:
        """Send OTP via SMTP (production)."""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        subject = f"CyberShield AI — Your verification code: {otp}"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #0a0a0f; color: #e4e4e7; padding: 40px;">
            <div style="max-width: 400px; margin: auto; background: #111118; padding: 32px; border-radius: 12px; border: 1px solid #2a2a3a;">
                <h2 style="color: #06b6d4; margin-top: 0;">🛡️ CyberShield AI</h2>
                <p>Your verification code is:</p>
                <div style="font-size: 32px; font-weight: bold; letter-spacing: 8px; text-align: center; padding: 20px; background: #1a1a24; border-radius: 8px; color: #06b6d4;">
                    {otp}
                </div>
                <p style="color: #71717a; font-size: 14px; margin-top: 16px;">
                    This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.<br>
                    If you didn't request this, please ignore this email.
                </p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.FROM_EMAIL
        msg["To"] = email
        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.FROM_EMAIL, email, msg.as_string())
        except Exception as e:
            print(f"⚠️ Failed to send OTP email: {e}")
            # Fall back to console
            print(f"  🔐 OTP for {email}: {otp}")

    @staticmethod
    def _mask_email(email: str) -> str:
        """Mask email for display: u***r@example.com"""
        parts = email.split("@")
        if len(parts) != 2:
            return "***"
        local = parts[0]
        domain = parts[1]
        if len(local) <= 1:
            masked_local = local[0] + "***"
        else:
            masked_local = local[0] + "***" + local[-1]
        return f"{masked_local}@{domain}"

    @staticmethod
    def _hash_token(token: str) -> str:
        """Hash a refresh token for storage. Uses SHA-256 (not bcrypt — needs exact match lookup)."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()


# Singleton instance
auth_service = AuthService()