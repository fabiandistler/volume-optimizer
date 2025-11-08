"""Application configuration management."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Application
    app_name: str = "Volume Optimizer Pro"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite+aiosqlite:///./volume_optimizer.db"

    # Security
    secret_key: str = "CHANGE_ME_IN_PRODUCTION_USE_LONG_RANDOM_STRING"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Rate Limiting
    redis_url: str = "redis://localhost:6379"
    rate_limit_enabled: bool = True

    # Subscription Tiers
    free_tier_daily_limit: int = 100
    pro_tier_daily_limit: int = 10000
    enterprise_tier_daily_limit: int = 1000000

    # Pricing (in cents)
    pro_price_monthly: int = 1900  # $19.00
    enterprise_price_monthly: int = 19900  # $199.00


settings = Settings()
