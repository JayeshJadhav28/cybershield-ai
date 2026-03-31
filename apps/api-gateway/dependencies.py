"""
FastAPI dependencies — authentication, rate limiting, database session.
"""

import time
import uuid
from typing import Optional
from functools import wraps

from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from utils.security import decode_token

security = HTTPBearer(auto_error=False)


class RateLimiter:
    """
    Simple in-memory rate limiter.
    In production, replace with Redis-backed limiter.
    """
    def __init__(self, max_requests: int = 60, period: int = 60):
        self.max_requests = max_requests
        self.period = period  # seconds
        self.requests = {}  # ip -> [(timestamp, count)]

    def is_allowed(self, key: str) -> bool:
        now = time.time()
        
        # Clean old entries
        if key in self.requests:
            self.requests[key] = [
                (ts, cnt) for ts, cnt in self.requests[key] 
                if now - ts < self.period
            ]
        else:
            self.requests[key] = []
        
        # Count recent requests
        total = sum(cnt for ts, cnt in self.requests[key])
        
        if total >= self.max_requests:
            return False
        
        # Record this request
        self.requests[key].append((now, 1))
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def rate_limit_dependency(request: Request):
    """Dependency to apply rate limiting."""
    # Use IP + user agent as key, or user ID if authenticated
    client_ip = request.client.host if request.client else "unknown"
    key = f"{client_ip}:{request.headers.get('user-agent', 'unknown')}"
    
    if not rate_limiter.is_allowed(key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
            headers={"Retry-After": "60"}
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from JWT token if present.
    Returns None if no token or invalid token (anonymous access allowed).
    """
    if not credentials:
        return None
    
    payload = decode_token(credentials.credentials)
    if not payload:
        return None
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    
    try:
        # Convert string UUID back to UUID object for database query
        user_id = uuid.UUID(user_id_str)
    except (ValueError, AttributeError):
        return None
    
    user = db.query(User).filter(User.id == user_id).first()
    return user


async def get_current_user_required(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    """Require authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user


async def require_admin(
    user: User = Depends(get_current_user_required)
) -> User:
    """Require admin or org_admin role."""
    if user.role not in ["admin", "org_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user


async def require_org_admin(
    user: User = Depends(get_current_user_required)
) -> User:
    """Require org_admin role specifically."""
    if user.role != "org_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization admin privileges required"
        )
    return user