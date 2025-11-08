"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, PositiveInt


# Volume calculation models
class VolumeRequest(BaseModel):
    """Request model for volume recommendations."""

    current_sets: PositiveInt = Field(
        ..., description="Current weekly set volume", example=12
    )
    training_level: Literal["beginner", "intermediate", "advanced"] = Field(
        ..., description="Training experience level", example="intermediate"
    )
    progress: Literal["yes", "no", "unclear"] = Field(
        ..., description="Are you making progress?", example="no"
    )
    recovered: Literal["yes", "no"] = Field(
        ..., description="Are you fully recovered between workouts?", example="yes"
    )
    muscle_group: str = Field(
        default="chest", description="Target muscle group", example="chest"
    )


class VolumeResponse(BaseModel):
    """Response model for volume recommendations."""

    volume_prediction: str
    current_sets: int
    muscle_group: str
    training_level: str
    landmarks: dict[str, int] | None = None


# Authentication models
class UserRegister(BaseModel):
    """User registration model."""

    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login model."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response."""

    access_token: str
    token_type: str = "bearer"


class APIKeyCreate(BaseModel):
    """API key creation model."""

    name: str = Field(..., min_length=1, max_length=255, example="My App Key")


class APIKeyResponse(BaseModel):
    """API key response model."""

    id: int
    key: str
    name: str
    created_at: datetime
    last_used_at: datetime | None


# Subscription models
class SubscriptionInfo(BaseModel):
    """Subscription information model."""

    tier: Literal["free", "pro", "enterprise"]
    daily_limit: int
    usage_today: int
    available_muscle_groups: list[str]


class SubscriptionUpgrade(BaseModel):
    """Subscription upgrade request."""

    tier: Literal["pro", "enterprise"]
    payment_method_id: str | None = None  # For future Stripe integration


# Analytics models
class TrainingHistoryResponse(BaseModel):
    """Training history response."""

    id: int
    muscle_group: str
    current_sets: int
    recommended_sets: str
    training_level: str
    progress: str
    recovered: str
    created_at: datetime


class AnalyticsResponse(BaseModel):
    """Analytics response for user's training data."""

    total_workouts_logged: int
    muscle_groups_tracked: list[str]
    average_weekly_volume: dict[str, float]
    progress_trend: dict[str, int]  # yes, no, unclear counts
    recent_history: list[TrainingHistoryResponse]
