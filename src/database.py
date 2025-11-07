"""Database models and session management."""

from datetime import datetime
from enum import Enum
from typing import AsyncGenerator

from sqlalchemy import DateTime, ForeignKey, String, Integer, Boolean, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


class SubscriptionTier(str, Enum):
    """Available subscription tiers."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model for authentication and subscription management."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(50), default=SubscriptionTier.FREE
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    api_keys: Mapped[list["APIKey"]] = relationship(back_populates="user")
    training_history: Mapped[list["TrainingHistory"]] = relationship(
        back_populates="user"
    )
    usage_logs: Mapped[list["UsageLog"]] = relationship(back_populates="user")


class APIKey(Base):
    """API Key model for authentication."""

    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")


class TrainingHistory(Base):
    """Training history for tracking user's workout volume over time."""

    __tablename__ = "training_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    muscle_group: Mapped[str] = mapped_column(String(50))
    current_sets: Mapped[int] = mapped_column(Integer)
    recommended_sets: Mapped[str] = mapped_column(String(255))
    training_level: Mapped[str] = mapped_column(String(50))
    progress: Mapped[str] = mapped_column(String(10))
    recovered: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="training_history")


class UsageLog(Base):
    """Usage log for tracking API usage and rate limiting."""

    __tablename__ = "usage_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    endpoint: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="usage_logs")


# Database engine and session
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database sessions."""
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
