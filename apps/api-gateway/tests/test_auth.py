"""
Test authentication system — OTP flow, JWT tokens, user management.
"""

import uuid
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from database import get_db
from models.user import User
from models.auth import OTPToken, RefreshToken
from services.auth_service import AuthService, auth_service
from utils.security import (
    generate_otp,
    hash_otp,
    verify_otp,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
    generate_refresh_token_string,
)


# ═══════════════════════════════════════════
# UNIT TESTS — Security Utilities
# ═══════════════════════════════════════════

class TestSecurityUtils:

    def test_otp_generation_length(self):
        otp = generate_otp(6)
        assert len(otp) == 6
        assert otp.isdigit()

    def test_otp_generation_randomness(self):
        otps = {generate_otp(6) for _ in range(100)}
        assert len(otps) > 50  # Should have significant variety

    def test_otp_hash_and_verify(self):
        otp = "123456"
        hashed = hash_otp(otp)
        assert hashed != otp
        assert verify_otp(otp, hashed) is True
        assert verify_otp("654321", hashed) is False

    def test_password_hash_and_verify(self):
        password = "SecurePassword123!"
        hashed = hash_password(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_jwt_create_and_decode(self):
        payload = {"sub": "user-123", "email": "test@example.com", "role": "user"}
        token = create_access_token(data=payload)
        decoded = decode_token(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"
        assert decoded["type"] == "access"

    def test_jwt_expired_token(self):
        payload = {"sub": "user-123"}
        token = create_access_token(data=payload, expires_delta=timedelta(seconds=-1))
        decoded = decode_token(token)
        assert decoded is None

    def test_jwt_invalid_token(self):
        decoded = decode_token("completely.invalid.token")
        assert decoded is None

    def test_refresh_token_generation(self):
        token = generate_refresh_token_string()
        assert len(token) > 20
        # Each should be unique
        token2 = generate_refresh_token_string()
        assert token != token2


# ═══════════════════════════════════════════
# UNIT TESTS — Auth Service
# ═══════════════════════════════════════════

class TestAuthServiceUnit:

    def test_mask_email_normal(self):
        assert AuthService._mask_email("testuser@example.com") == "t***r@example.com"

    def test_mask_email_short(self):
        assert AuthService._mask_email("ab@test.com") == "a***b@test.com"

    def test_mask_email_single_char(self):
        result = AuthService._mask_email("a@test.com")
        assert "***" in result
        assert "@test.com" in result

    def test_hash_token_deterministic(self):
        token = "test-token-value"
        hash1 = AuthService._hash_token(token)
        hash2 = AuthService._hash_token(token)
        assert hash1 == hash2
        assert hash1 != token

    def test_hash_token_different_inputs(self):
        hash1 = AuthService._hash_token("token-1")
        hash2 = AuthService._hash_token("token-2")
        assert hash1 != hash2


# ═══════════════════════════════════════════
# INTEGRATION TESTS — Auth Service with DB
# ═══════════════════════════════════════════

class TestAuthServiceIntegration:

    def test_request_otp_creates_record(self, db_session):
        """Test OTP creation stores hashed OTP in database."""
        with patch.object(auth_service, '_deliver_otp'):
            message, expires_in = auth_service.request_otp(
                db=db_session,
                email="new@example.com",
                purpose="login",
            )

        assert "OTP sent" in message
        assert expires_in == 300  # 5 minutes

        # Verify OTP record exists
        otp_record = db_session.query(OTPToken).filter_by(email="new@example.com").first()
        assert otp_record is not None
        assert otp_record.purpose == "login"
        assert otp_record.attempts == 0
        assert otp_record.used_at is None

    def test_request_otp_rate_limited(self, db_session):
        """Test rate limiting on OTP requests."""
        with patch.object(auth_service, '_deliver_otp'):
            auth_service.request_otp(db=db_session, email="rate@test.com")

        # Second request within 60 seconds should fail
        with pytest.raises(ValueError, match="wait 60 seconds"):
            with patch.object(auth_service, '_deliver_otp'):
                auth_service.request_otp(db=db_session, email="rate@test.com")

    def test_request_otp_invalidates_previous(self, db_session):
        """Test that requesting new OTP invalidates previous unused ones."""
        # Create an old OTP record manually
        old_otp = OTPToken(
            id=uuid.uuid4(),
            email="old@test.com",
            otp_hash=hash_otp("111111"),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
            created_at=datetime.now(timezone.utc) - timedelta(minutes=2),  # 2 min ago (past rate limit)
        )
        db_session.add(old_otp)
        db_session.commit()

        with patch.object(auth_service, '_deliver_otp'):
            auth_service.request_otp(db=db_session, email="old@test.com")

        # Old unused OTPs should be deleted
        remaining = db_session.query(OTPToken).filter_by(email="old@test.com").count()
        assert remaining == 1  # Only the new one

    def test_verify_otp_success_creates_user(self, db_session):
        """Test successful OTP verification creates a new user."""
        otp_plain = "123456"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="newuser@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        user, access_token, refresh_token, expires_in = (
            auth_service.verify_otp_and_authenticate(
                db=db_session,
                email="newuser@test.com",
                otp_plain=otp_plain,
                purpose="login",
            )
        )

        assert user is not None
        assert user.email == "newuser@test.com"
        assert user.role == "user"
        assert access_token is not None
        assert refresh_token is not None
        assert expires_in > 0

        # Token should be valid
        decoded = decode_token(access_token)
        assert decoded["sub"] == str(user.id)

    def test_verify_otp_success_existing_user(self, db_session):
        """Test OTP login with existing user."""
        # Create user
        existing_user = User(
            id=uuid.uuid4(),
            email="existing@test.com",
            display_name="Existing",
            role="user",
        )
        db_session.add(existing_user)
        db_session.flush()

        otp_plain = "654321"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="existing@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        user, access_token, _, _ = auth_service.verify_otp_and_authenticate(
            db=db_session,
            email="existing@test.com",
            otp_plain=otp_plain,
            purpose="login",
        )

        assert user.id == existing_user.id
        assert user.display_name == "Existing"

    def test_verify_otp_wrong_code(self, db_session):
        """Test OTP verification with wrong code."""
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="wrong@test.com",
            otp_hash=hash_otp("123456"),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        with pytest.raises(ValueError, match="Invalid OTP"):
            auth_service.verify_otp_and_authenticate(
                db=db_session,
                email="wrong@test.com",
                otp_plain="999999",
                purpose="login",
            )

        # Attempts should be incremented
        db_session.refresh(otp_record)
        assert otp_record.attempts == 1

    def test_verify_otp_expired(self, db_session):
        """Test OTP verification with expired OTP."""
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="expired@test.com",
            otp_hash=hash_otp("123456"),
            purpose="login",
            expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Already expired
        )
        db_session.add(otp_record)
        db_session.commit()

        with pytest.raises(ValueError, match="No valid OTP"):
            auth_service.verify_otp_and_authenticate(
                db=db_session,
                email="expired@test.com",
                otp_plain="123456",
                purpose="login",
            )

    def test_verify_otp_max_attempts(self, db_session):
        """Test OTP verification after max attempts reached."""
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="maxed@test.com",
            otp_hash=hash_otp("123456"),
            purpose="login",
            attempts=3,
            max_attempts=3,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        with pytest.raises(ValueError, match="Maximum OTP attempts"):
            auth_service.verify_otp_and_authenticate(
                db=db_session,
                email="maxed@test.com",
                otp_plain="123456",
                purpose="login",
            )

    def test_refresh_token_flow(self, db_session):
        """Test refresh token creates new access token."""
        # Create user and initial token pair
        user = User(
            id=uuid.uuid4(),
            email="refresh@test.com",
            role="user",
        )
        db_session.add(user)
        db_session.flush()

        # Simulate login to get refresh token
        otp_plain = "111111"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="refresh@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        _, _, refresh_token, _ = auth_service.verify_otp_and_authenticate(
            db=db_session,
            email="refresh@test.com",
            otp_plain=otp_plain,
            purpose="login",
        )

        # Use refresh token
        new_access, expires_in = auth_service.refresh_access_token(
            db=db_session,
            refresh_token_str=refresh_token,
        )

        assert new_access is not None
        decoded = decode_token(new_access)
        assert decoded["sub"] == str(user.id)

    def test_refresh_token_invalid(self, db_session):
        """Test refresh with invalid token fails."""
        with pytest.raises(ValueError, match="Invalid or expired"):
            auth_service.refresh_access_token(
                db=db_session,
                refresh_token_str="completely-fake-token",
            )

    def test_logout_revokes_tokens(self, db_session):
        """Test logout revokes all refresh tokens."""
        user = User(
            id=uuid.uuid4(),
            email="logout@test.com",
            role="user",
        )
        db_session.add(user)
        db_session.flush()

        # Create refresh token
        rt = RefreshToken(
            id=uuid.uuid4(),
            user_id=user.id,
            token_hash="fake-hash",
            expires_at=datetime.now(timezone.utc) + timedelta(days=30),
        )
        db_session.add(rt)
        db_session.commit()

        auth_service.logout(db=db_session, user_id=user.id)

        db_session.refresh(rt)
        assert rt.revoked_at is not None

    def test_get_user_profile(self, db_session):
        """Test profile includes stats."""
        user = User(
            id=uuid.uuid4(),
            email="profile@test.com",
            display_name="Profile User",
            role="user",
        )
        db_session.add(user)
        db_session.commit()

        profile = auth_service.get_user_profile(db=db_session, user=user)
        assert profile["email"] == "profile@test.com"
        assert profile["display_name"] == "Profile User"
        assert profile["stats"]["total_analyses"] == 0
        assert profile["stats"]["quizzes_completed"] == 0

    def test_update_profile(self, db_session):
        """Test profile update."""
        user = User(
            id=uuid.uuid4(),
            email="update@test.com",
            role="user",
        )
        db_session.add(user)
        db_session.commit()

        updated = auth_service.update_profile(
            db=db_session,
            user=user,
            display_name="New Name",
            phone="+919876543210",
        )
        assert updated.display_name == "New Name"
        assert updated.phone == "+919876543210"

    def test_email_case_insensitive(self, db_session):
        """Test that email matching is case-insensitive."""
        otp_plain = "123456"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="case@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        db_session.add(otp_record)
        db_session.commit()

        user, _, _, _ = auth_service.verify_otp_and_authenticate(
            db=db_session,
            email="CASE@TEST.COM",
            otp_plain=otp_plain,
            purpose="login",
        )
        assert user.email == "case@test.com"


# ═══════════════════════════════════════════
# API ENDPOINT TESTS
# ═══════════════════════════════════════════

class TestAuthEndpoints:
    """Test auth endpoints via HTTP using TestClient."""

    @pytest.fixture(autouse=True)
    def setup_client(self, db_session, override_get_db):
        """Set up test client with overridden DB."""
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
        self.db = db_session
        yield
        app.dependency_overrides.clear()

    def test_request_otp_endpoint(self):
        response = self.client.post(
            "/api/v1/auth/request-otp",
            json={"email": "endpoint@test.com", "purpose": "login"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"
        assert "OTP sent" in data["message"]
        assert data["expires_in_seconds"] == 300

    def test_request_otp_invalid_email(self):
        response = self.client.post(
            "/api/v1/auth/request-otp",
            json={"email": "not-an-email", "purpose": "login"}
        )
        assert response.status_code == 422

    def test_verify_otp_endpoint_success(self):
        # First create OTP
        otp_plain = "123456"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="verify@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={
                "email": "verify@test.com",
                "otp": otp_plain,
                "purpose": "login",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "verify@test.com"

    def test_verify_otp_endpoint_wrong_code(self):
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="wrongep@test.com",
            otp_hash=hash_otp("123456"),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={
                "email": "wrongep@test.com",
                "otp": "999999",
                "purpose": "login",
            }
        )
        assert response.status_code == 401

    def test_me_endpoint_unauthorized(self):
        response = self.client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_endpoint_authenticated(self):
        # Create user + get token
        otp_plain = "111111"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="metest@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        login_response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "metest@test.com", "otp": otp_plain, "purpose": "login"}
        )
        token = login_response.json()["access_token"]

        # Now call /me
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "metest@test.com"
        assert "stats" in data

    def test_refresh_endpoint(self):
        # Login to get refresh token
        otp_plain = "222222"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="refreshep@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        login_response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "refreshep@test.com", "otp": otp_plain, "purpose": "login"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh
        response = self.client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["expires_in"] > 0

    def test_refresh_endpoint_invalid_token(self):
        response = self.client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token-here"}
        )
        assert response.status_code == 401

    def test_logout_endpoint(self):
        # Login
        otp_plain = "333333"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="logoutest@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        login_response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "logoutest@test.com", "otp": otp_plain, "purpose": "login"}
        )
        token = login_response.json()["access_token"]

        # Logout
        response = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["status"] == "logged_out"

    def test_update_profile_endpoint(self):
        # Login
        otp_plain = "444444"
        otp_record = OTPToken(
            id=uuid.uuid4(),
            email="updateep@test.com",
            otp_hash=hash_otp(otp_plain),
            purpose="login",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )
        self.db.add(otp_record)
        self.db.commit()

        login_response = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "updateep@test.com", "otp": otp_plain, "purpose": "login"}
        )
        token = login_response.json()["access_token"]

        # Update
        response = self.client.patch(
            "/api/v1/auth/me",
            json={"display_name": "Updated Name", "phone": "+911234567890"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"

    def test_full_auth_flow(self):
        """Test complete flow: request OTP → verify → /me → refresh → logout."""
        email = "fullflow@test.com"

        # 1. Request OTP
        resp1 = self.client.post(
            "/api/v1/auth/request-otp",
            json={"email": email, "purpose": "login"}
        )
        assert resp1.status_code == 200

        # Get OTP from DB (since we can't read console in tests)
        otp_record = self.db.query(OTPToken).filter_by(email=email).first()
        # We need the plain OTP — in tests we create it manually
        # For the full flow test, inject a known OTP
        otp_plain = "555555"
        otp_record.otp_hash = hash_otp(otp_plain)
        self.db.commit()

        # 2. Verify OTP
        resp2 = self.client.post(
            "/api/v1/auth/verify-otp",
            json={"email": email, "otp": otp_plain, "purpose": "login"}
        )
        assert resp2.status_code == 200
        tokens = resp2.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]

        # 3. Get profile
        resp3 = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert resp3.status_code == 200
        assert resp3.json()["email"] == email

        # 4. Refresh token
        resp4 = self.client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert resp4.status_code == 200
        new_access = resp4.json()["access_token"]

        # 5. Verify new token works
        resp5 = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_access}"}
        )
        assert resp5.status_code == 200

        # 6. Logout
        resp6 = self.client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {new_access}"}
        )
        assert resp6.status_code == 200

        # 7. Old refresh token should be revoked
        resp7 = self.client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert resp7.status_code == 401