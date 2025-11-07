"""Professional FastAPI application with tiered subscriptions and advanced features."""

from datetime import datetime
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import (
    check_rate_limit,
    create_access_token,
    generate_api_key,
    get_current_user,
    get_password_hash,
    require_tier,
    verify_password,
)
from src.config import settings
from src.database import (
    APIKey,
    TrainingHistory,
    UsageLog,
    User,
    get_db,
    init_db,
)
from src.models import (
    AnalyticsResponse,
    APIKeyCreate,
    APIKeyResponse,
    SubscriptionInfo,
    SubscriptionUpgrade,
    Token,
    TrainingHistoryResponse,
    UserLogin,
    UserRegister,
    VolumeRequest,
    VolumeResponse,
)
from src.volume_calculator import recommend_volume
from src.volume_data import get_available_muscle_groups, volume_landmarks

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
# 💪 Volume Optimizer Pro - Professional Training Volume API

## Features by Tier

### 🆓 Free Tier
- ✅ 100 requests per day
- ✅ Chest volume optimization
- ✅ Basic recommendations

### 🚀 Pro Tier - $19/month
- ✅ 10,000 requests per day
- ✅ All 10 muscle groups
- ✅ Training history tracking
- ✅ Progress analytics
- ✅ Priority support

### 🏢 Enterprise Tier - $199/month
- ✅ Unlimited requests
- ✅ All Pro features
- ✅ Admin dashboard
- ✅ Custom integrations
- ✅ Dedicated support

## Getting Started

1. Register at `/auth/register` to get your free account
2. Create an API key at `/auth/api-keys`
3. Use your API key in the `X-API-Key` header
4. Start optimizing your training volume!

## Support

For questions or support, contact: support@volumeoptimizer.pro
    """,
    contact={
        "name": "Volume Optimizer Support",
        "email": "support@volumeoptimizer.pro",
    },
    license_info={
        "name": "Commercial License",
        "url": "https://volumeoptimizer.pro/license",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


# ============================================================================
# PUBLIC ENDPOINTS (No authentication required)
# ============================================================================


@app.get("/", tags=["Info"])
async def root():
    """Welcome endpoint with API information."""
    return {
        "message": "Welcome to Volume Optimizer Pro API",
        "version": settings.app_version,
        "docs": "/docs",
        "get_started": "/auth/register",
        "pricing": {
            "free": {"price": 0, "daily_limit": settings.free_tier_daily_limit},
            "pro": {
                "price": settings.pro_price_monthly / 100,
                "daily_limit": settings.pro_tier_daily_limit,
            },
            "enterprise": {
                "price": settings.enterprise_price_monthly / 100,
                "daily_limit": settings.enterprise_tier_daily_limit,
            },
        },
    }


@app.get("/health", tags=["Info"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/muscle-groups", tags=["Info"])
async def list_muscle_groups():
    """List all available muscle groups and their volume landmarks."""
    return {
        "muscle_groups": list(volume_landmarks.keys()),
        "landmarks": volume_landmarks,
        "note": "Free tier has access to 'chest' only. Upgrade to Pro for all muscle groups.",
    }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================


@app.post("/auth/register", response_model=Token, tags=["Authentication"])
async def register(
    user_data: UserRegister, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Register a new user account (Free tier by default)."""
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        subscription_tier="free",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create default API key
    api_key = APIKey(
        key=generate_api_key(), name="Default API Key", user_id=user.id, is_active=True
    )
    db.add(api_key)
    await db.commit()

    # Generate access token
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/auth/login", response_model=Token, tags=["Authentication"])
async def login(
    credentials: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Login to get an access token."""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive"
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", tags=["Authentication"])
async def get_current_user_info(user: Annotated[User, Depends(get_current_user)]):
    """Get current authenticated user information."""
    return {
        "id": user.id,
        "email": user.email,
        "subscription_tier": user.subscription_tier,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }


@app.post("/auth/api-keys", response_model=APIKeyResponse, tags=["Authentication"])
async def create_api_key(
    key_data: APIKeyCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a new API key for the authenticated user."""
    api_key = APIKey(
        key=generate_api_key(), name=key_data.name, user_id=user.id, is_active=True
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return APIKeyResponse(
        id=api_key.id,
        key=api_key.key,
        name=api_key.name,
        created_at=api_key.created_at,
        last_used_at=api_key.last_used_at,
    )


@app.get("/auth/api-keys", response_model=list[APIKeyResponse], tags=["Authentication"])
async def list_api_keys(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """List all API keys for the authenticated user."""
    result = await db.execute(select(APIKey).where(APIKey.user_id == user.id))
    keys = result.scalars().all()

    return [
        APIKeyResponse(
            id=key.id,
            key=key.key,
            name=key.name,
            created_at=key.created_at,
            last_used_at=key.last_used_at,
        )
        for key in keys
    ]


@app.delete("/auth/api-keys/{key_id}", tags=["Authentication"])
async def delete_api_key(
    key_id: int,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete an API key."""
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user.id)
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    await db.delete(api_key)
    await db.commit()

    return {"message": "API key deleted successfully"}


# ============================================================================
# VOLUME OPTIMIZATION ENDPOINTS
# ============================================================================


@app.post("/v1/predict-volume", response_model=VolumeResponse, tags=["Volume Optimization"])
async def predict_volume_v1(
    request: VolumeRequest,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get volume recommendations (supports all tiers).

    Free tier: chest only
    Pro/Enterprise: all muscle groups
    """
    # Check rate limit
    await check_rate_limit(user, db, "/v1/predict-volume")

    # Check if muscle group is available for user's tier
    available_groups = get_available_muscle_groups(user.subscription_tier)
    if request.muscle_group not in available_groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Muscle group '{request.muscle_group}' requires Pro or Enterprise tier. "
            f"Available for your tier: {available_groups}. Upgrade at /subscription/info",
        )

    # Calculate recommendation
    try:
        prediction = recommend_volume(
            current_sets=request.current_sets,
            training_level=request.training_level,
            progress=request.progress,
            recovered=request.recovered,
            muscle_group=request.muscle_group,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Save to training history (Pro and Enterprise only)
    if user.subscription_tier in ["pro", "enterprise"]:
        history = TrainingHistory(
            user_id=user.id,
            muscle_group=request.muscle_group,
            current_sets=request.current_sets,
            recommended_sets=prediction,
            training_level=request.training_level,
            progress=request.progress,
            recovered=request.recovered,
        )
        db.add(history)
        await db.commit()

    return VolumeResponse(
        volume_prediction=prediction,
        current_sets=request.current_sets,
        muscle_group=request.muscle_group,
        training_level=request.training_level,
        landmarks=volume_landmarks[request.muscle_group][request.training_level]
        if user.subscription_tier != "free"
        else None,
    )


# ============================================================================
# TRAINING HISTORY & ANALYTICS (Pro and Enterprise only)
# ============================================================================


@app.get(
    "/v1/history",
    response_model=list[TrainingHistoryResponse],
    tags=["Training History"],
)
async def get_training_history(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    muscle_group: str | None = None,
    limit: int = 50,
):
    """Get training history (Pro and Enterprise only)."""
    # Require Pro or Enterprise tier
    if user.subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Training history requires Pro or Enterprise tier. Upgrade at /subscription/upgrade",
        )

    await check_rate_limit(user, db, "/v1/history")

    query = select(TrainingHistory).where(TrainingHistory.user_id == user.id)

    if muscle_group:
        query = query.where(TrainingHistory.muscle_group == muscle_group)

    query = query.order_by(TrainingHistory.created_at.desc()).limit(limit)

    result = await db.execute(query)
    history = result.scalars().all()

    return [
        TrainingHistoryResponse(
            id=h.id,
            muscle_group=h.muscle_group,
            current_sets=h.current_sets,
            recommended_sets=h.recommended_sets,
            training_level=h.training_level,
            progress=h.progress,
            recovered=h.recovered,
            created_at=h.created_at,
        )
        for h in history
    ]


@app.get("/v1/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get training analytics and insights (Pro and Enterprise only)."""
    # Require Pro or Enterprise tier
    if user.subscription_tier == "free":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analytics require Pro or Enterprise tier. Upgrade at /subscription/upgrade",
        )

    await check_rate_limit(user, db, "/v1/analytics")

    # Get all training history
    result = await db.execute(
        select(TrainingHistory)
        .where(TrainingHistory.user_id == user.id)
        .order_by(TrainingHistory.created_at.desc())
    )
    all_history = result.scalars().all()

    if not all_history:
        return AnalyticsResponse(
            total_workouts_logged=0,
            muscle_groups_tracked=[],
            average_weekly_volume={},
            progress_trend={"yes": 0, "no": 0, "unclear": 0},
            recent_history=[],
        )

    # Calculate analytics
    muscle_groups = list(set(h.muscle_group for h in all_history))

    # Average volume per muscle group
    avg_volume = {}
    for mg in muscle_groups:
        mg_history = [h for h in all_history if h.muscle_group == mg]
        avg_volume[mg] = sum(h.current_sets for h in mg_history) / len(mg_history)

    # Progress trend
    progress_trend = {"yes": 0, "no": 0, "unclear": 0}
    for h in all_history:
        progress_trend[h.progress] = progress_trend.get(h.progress, 0) + 1

    # Recent history (last 10)
    recent = all_history[:10]

    return AnalyticsResponse(
        total_workouts_logged=len(all_history),
        muscle_groups_tracked=muscle_groups,
        average_weekly_volume=avg_volume,
        progress_trend=progress_trend,
        recent_history=[
            TrainingHistoryResponse(
                id=h.id,
                muscle_group=h.muscle_group,
                current_sets=h.current_sets,
                recommended_sets=h.recommended_sets,
                training_level=h.training_level,
                progress=h.progress,
                recovered=h.recovered,
                created_at=h.created_at,
            )
            for h in recent
        ],
    )


# ============================================================================
# SUBSCRIPTION MANAGEMENT
# ============================================================================


@app.get("/subscription/info", response_model=SubscriptionInfo, tags=["Subscription"])
async def get_subscription_info(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get current subscription information and usage."""
    # Get today's usage
    today = datetime.utcnow().date()
    result = await db.execute(
        select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user.id, func.date(UsageLog.created_at) == today
        )
    )
    usage_today = result.scalar_one()

    # Get daily limit
    limits = {
        "free": settings.free_tier_daily_limit,
        "pro": settings.pro_tier_daily_limit,
        "enterprise": settings.enterprise_tier_daily_limit,
    }
    daily_limit = limits.get(user.subscription_tier, limits["free"])

    return SubscriptionInfo(
        tier=user.subscription_tier,
        daily_limit=daily_limit,
        usage_today=usage_today,
        available_muscle_groups=get_available_muscle_groups(user.subscription_tier),
    )


@app.post("/subscription/upgrade", tags=["Subscription"])
async def upgrade_subscription(
    upgrade_data: SubscriptionUpgrade,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Upgrade subscription tier.

    NOTE: This is a demo endpoint. In production, integrate with Stripe or similar payment processor.
    """
    # Validate upgrade path
    tier_hierarchy = {"free": 0, "pro": 1, "enterprise": 2}
    current_level = tier_hierarchy[user.subscription_tier]
    target_level = tier_hierarchy[upgrade_data.tier]

    if target_level <= current_level:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot downgrade or maintain current tier. Contact support for downgrades.",
        )

    # In production, process payment here with Stripe
    # For now, just upgrade the user
    user.subscription_tier = upgrade_data.tier
    await db.commit()

    return {
        "message": f"Successfully upgraded to {upgrade_data.tier} tier!",
        "new_tier": upgrade_data.tier,
        "note": "This is a demo. In production, payment processing would occur here.",
    }


# ============================================================================
# ADMIN ENDPOINTS (Enterprise only)
# ============================================================================


@app.get("/admin/stats", tags=["Admin"])
async def get_admin_stats(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get system-wide statistics (Enterprise only)."""
    if user.subscription_tier != "enterprise":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin endpoints require Enterprise tier",
        )

    # Total users
    total_users = await db.scalar(select(func.count(User.id)))

    # Users by tier
    users_by_tier = {}
    for tier in ["free", "pro", "enterprise"]:
        count = await db.scalar(
            select(func.count(User.id)).where(User.subscription_tier == tier)
        )
        users_by_tier[tier] = count

    # Total API requests today
    today = datetime.utcnow().date()
    requests_today = await db.scalar(
        select(func.count(UsageLog.id)).where(func.date(UsageLog.created_at) == today)
    )

    # Total training history entries
    total_history = await db.scalar(select(func.count(TrainingHistory.id)))

    return {
        "total_users": total_users,
        "users_by_tier": users_by_tier,
        "requests_today": requests_today,
        "total_training_history_entries": total_history,
        "timestamp": datetime.utcnow().isoformat(),
    }


# Legacy endpoint for backward compatibility (deprecated)
@app.get("/predict-volume/{current_sets}/{training_level}/{progress}/{recovered}", deprecated=True, tags=["Legacy"])
async def predict_volume_legacy(
    current_sets: int,
    training_level: str,
    progress: str,
    recovered: str,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Legacy endpoint for backward compatibility. Use /v1/predict-volume instead."""
    await check_rate_limit(user, db, "/predict-volume")

    result = recommend_volume(current_sets, training_level, progress, recovered, "chest")
    return {"volume_prediction": result}
