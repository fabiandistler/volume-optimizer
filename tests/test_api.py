"""Tests for API endpoints."""

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.api import app
from src.database import Base, get_db


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_db():
    """Create a test database."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with async_session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_db):
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(client: AsyncClient):
    """Create a test user and return auth headers."""
    # Register user
    response = await client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Get API key
    response = await client.get(
        "/auth/api-keys", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    api_key = response.json()[0]["key"]

    return {"X-API-Key": api_key}


# ============================================================================
# PUBLIC ENDPOINTS
# ============================================================================


@pytest.mark.asyncio
async def test_root(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "pricing" in data


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_muscle_groups(client: AsyncClient):
    """Test muscle groups listing."""
    response = await client.get("/muscle-groups")
    assert response.status_code == 200
    data = response.json()
    assert "muscle_groups" in data
    assert "chest" in data["muscle_groups"]
    assert "back" in data["muscle_groups"]


# ============================================================================
# AUTHENTICATION
# ============================================================================


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test that duplicate email registration fails."""
    email = "duplicate@example.com"

    # First registration
    response = await client.post(
        "/auth/register", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 200

    # Second registration with same email
    response = await client.post(
        "/auth/register", json={"email": email, "password": "password123"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    """Test user login."""
    # Register first
    await client.post(
        "/auth/register",
        json={"email": "loginuser@example.com", "password": "password123"},
    )

    # Login
    response = await client.post(
        "/auth/login",
        json={"email": "loginuser@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/auth/login",
        json={"email": "nonexistent@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, test_user):
    """Test getting current user info."""
    response = await client.get("/auth/me", headers=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["subscription_tier"] == "free"


# ============================================================================
# VOLUME PREDICTION
# ============================================================================


@pytest.mark.asyncio
async def test_predict_volume_chest(client: AsyncClient, test_user):
    """Test volume prediction for chest (free tier)."""
    response = await client.post(
        "/v1/predict-volume",
        json={
            "current_sets": 12,
            "training_level": "intermediate",
            "progress": "yes",
            "recovered": "yes",
            "muscle_group": "chest",
        },
        headers=test_user,
    )
    assert response.status_code == 200
    data = response.json()
    assert "volume_prediction" in data
    assert data["muscle_group"] == "chest"


@pytest.mark.asyncio
async def test_predict_volume_pro_muscle_group_free_tier(
    client: AsyncClient, test_user
):
    """Test that free tier cannot access pro muscle groups."""
    response = await client.post(
        "/v1/predict-volume",
        json={
            "current_sets": 12,
            "training_level": "intermediate",
            "progress": "yes",
            "recovered": "yes",
            "muscle_group": "back",
        },
        headers=test_user,
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_predict_volume_without_auth(client: AsyncClient):
    """Test that prediction requires authentication."""
    response = await client.post(
        "/v1/predict-volume",
        json={
            "current_sets": 12,
            "training_level": "intermediate",
            "progress": "yes",
            "recovered": "yes",
            "muscle_group": "chest",
        },
    )
    assert response.status_code == 401


# ============================================================================
# SUBSCRIPTION
# ============================================================================


@pytest.mark.asyncio
async def test_get_subscription_info(client: AsyncClient, test_user):
    """Test getting subscription info."""
    response = await client.get("/subscription/info", headers=test_user)
    assert response.status_code == 200
    data = response.json()
    assert data["tier"] == "free"
    assert data["daily_limit"] == 100
    assert "chest" in data["available_muscle_groups"]


@pytest.mark.asyncio
async def test_upgrade_subscription(client: AsyncClient, test_user):
    """Test subscription upgrade."""
    response = await client.post(
        "/subscription/upgrade",
        json={"tier": "pro", "payment_method_id": None},
        headers=test_user,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["new_tier"] == "pro"


# ============================================================================
# TRAINING HISTORY (Pro feature)
# ============================================================================


@pytest.mark.asyncio
async def test_history_free_tier(client: AsyncClient, test_user):
    """Test that free tier cannot access training history."""
    response = await client.get("/v1/history", headers=test_user)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_analytics_free_tier(client: AsyncClient, test_user):
    """Test that free tier cannot access analytics."""
    response = await client.get("/v1/analytics", headers=test_user)
    assert response.status_code == 403


# ============================================================================
# API KEY MANAGEMENT
# ============================================================================


@pytest.mark.asyncio
async def test_create_api_key(client: AsyncClient, test_user):
    """Test creating a new API key."""
    response = await client.post(
        "/auth/api-keys", json={"name": "My New Key"}, headers=test_user
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My New Key"
    assert "key" in data
    assert data["key"].startswith("vo_")


@pytest.mark.asyncio
async def test_list_api_keys(client: AsyncClient, test_user):
    """Test listing API keys."""
    response = await client.get("/auth/api-keys", headers=test_user)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least the default key


@pytest.mark.asyncio
async def test_delete_api_key(client: AsyncClient):
    """Test deleting an API key."""
    # Register and get token
    response = await client.post(
        "/auth/register",
        json={"email": "deletekey@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create a new key
    response = await client.post(
        "/auth/api-keys", json={"name": "Key to Delete"}, headers=headers
    )
    key_id = response.json()["id"]

    # Delete the key
    response = await client.delete(f"/auth/api-keys/{key_id}", headers=headers)
    assert response.status_code == 200

    # Verify it's deleted
    response = await client.get("/auth/api-keys", headers=headers)
    keys = response.json()
    assert not any(k["id"] == key_id for k in keys)
