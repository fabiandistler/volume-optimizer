"""Authentication and authorization utilities."""

import secrets
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import APIKey, User, get_db

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return f"vo_{secrets.token_urlsafe(48)}"


async def get_user_by_api_key(
    api_key: str, db: AsyncSession
) -> User | None:
    """Get user by API key."""
    result = await db.execute(
        select(APIKey)
        .where(APIKey.key == api_key, APIKey.is_active == True)
        .join(User)
        .where(User.is_active == True)
    )
    key = result.scalar_one_or_none()

    if key:
        # Update last used timestamp
        key.last_used_at = datetime.utcnow()
        await db.commit()
        return key.user

    return None


async def get_current_user(
    api_key: Annotated[str | None, Security(api_key_header)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user from API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Get yours at /auth/register",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    user = await get_user_by_api_key(api_key, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return user


async def check_rate_limit(
    user: User, db: AsyncSession, endpoint: str
) -> None:
    """Check if user has exceeded their rate limit."""
    from sqlalchemy import func, and_
    from src.database import UsageLog

    # Get usage count for today
    today = datetime.utcnow().date()
    result = await db.execute(
        select(func.count(UsageLog.id))
        .where(
            and_(
                UsageLog.user_id == user.id,
                func.date(UsageLog.created_at) == today,
            )
        )
    )
    usage_count = result.scalar_one()

    # Check against tier limits
    limits = {
        "free": settings.free_tier_daily_limit,
        "pro": settings.pro_tier_daily_limit,
        "enterprise": settings.enterprise_tier_daily_limit,
    }

    limit = limits.get(user.subscription_tier, limits["free"])

    if usage_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Your {user.subscription_tier} tier allows {limit} requests per day. Upgrade at /subscription/upgrade",
        )

    # Log usage
    usage_log = UsageLog(user_id=user.id, endpoint=endpoint)
    db.add(usage_log)
    await db.commit()


async def require_tier(
    user: Annotated[User, Depends(get_current_user)],
    required_tier: str,
) -> User:
    """Require a specific subscription tier or higher."""
    tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}

    user_tier_level = tier_hierarchy.get(user.subscription_tier, 0)
    required_tier_level = tier_hierarchy.get(required_tier, 0)

    if user_tier_level < required_tier_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This endpoint requires {required_tier} tier or higher. Upgrade at /subscription/upgrade",
        )

    return user
