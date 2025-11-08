# 💪 Volume Optimizer Pro

**Professional API for optimizing hypertrophy training volume with tiered subscriptions and advanced analytics.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-green.svg)](https://fastapi.tiangolo.com)
[![License: Commercial](https://img.shields.io/badge/License-Commercial-yellow.svg)](LICENSE)

---

## 🚀 Features

### Core Functionality
- **Science-Based Volume Recommendations**: Using MEV, MAV, and MRV principles
- **10 Muscle Groups**: Chest, Back, Shoulders, Biceps, Triceps, Quads, Hamstrings, Glutes, Calves, Abs
- **Personalized Analysis**: Based on training level, progress, and recovery status
- **Professional API**: RESTful design with comprehensive documentation

### Monetization Features
- **Tiered Subscriptions**: Free, Pro ($19/mo), Enterprise ($199/mo)
- **API Key Authentication**: Secure access control
- **Rate Limiting**: Usage tracking and enforcement
- **Training History**: Track progress over time (Pro+)
- **Advanced Analytics**: Insights and trends (Pro+)
- **Admin Dashboard**: System-wide statistics (Enterprise)

---

## 💰 Pricing & Tiers

### 🆓 Free Tier
- ✅ 100 requests per day
- ✅ Chest volume optimization
- ✅ Basic recommendations
- ✅ Community support

### 🚀 Pro Tier - **$19/month**
- ✅ **10,000 requests per day**
- ✅ **All 10 muscle groups**
- ✅ **Training history tracking**
- ✅ **Progress analytics**
- ✅ **Volume landmarks data**
- ✅ Priority email support

### 🏢 Enterprise Tier - **$199/month**
- ✅ **Unlimited requests**
- ✅ **All Pro features**
- ✅ **Admin dashboard**
- ✅ **System-wide analytics**
- ✅ **Custom integrations**
- ✅ **Dedicated support**
- ✅ **SLA guarantees**

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/volume-optimizer.git
cd volume-optimizer

# Install dependencies
uv sync

# Copy environment example
cp .env.example .env

# Edit .env with your configuration
# IMPORTANT: Change SECRET_KEY in production!

# Run the application
uv run uvicorn src.api:app --reload
```

The API will be available at `http://localhost:8000`

### Docker Setup

```bash
# Using Docker Compose (recommended for development)
docker-compose up -d

# The API will be available at http://localhost:8000
# Redis will be running on localhost:6379
```

---

## 🎯 Quick Start Guide

### 1. Register for a Free Account

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Get Your API Key

```bash
curl -X GET "http://localhost:8000/auth/api-keys" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Response:
```json
[
  {
    "id": 1,
    "key": "vo_AbC123XyZ...",
    "name": "Default API Key",
    "created_at": "2025-11-07T20:00:00",
    "last_used_at": null
  }
]
```

### 3. Make Your First Request

```bash
curl -X POST "http://localhost:8000/v1/predict-volume" \
  -H "X-API-Key: vo_AbC123XyZ..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_sets": 12,
    "training_level": "intermediate",
    "progress": "no",
    "recovered": "yes",
    "muscle_group": "chest"
  }'
```

Response:
```json
{
  "volume_prediction": "Increase to at least 15 sets per week (MAV)",
  "current_sets": 12,
  "muscle_group": "chest",
  "training_level": "intermediate",
  "landmarks": null
}
```

---

## 📚 API Documentation

### Interactive Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

#### Public Endpoints
- `GET /` - Welcome and pricing information
- `GET /health` - Health check
- `GET /muscle-groups` - List all muscle groups

#### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user info
- `POST /auth/api-keys` - Create API key
- `GET /auth/api-keys` - List API keys
- `DELETE /auth/api-keys/{key_id}` - Delete API key

#### Volume Optimization
- `POST /v1/predict-volume` - Get volume recommendations

#### Training History (Pro+)
- `GET /v1/history` - Get training history
- `GET /v1/analytics` - Get analytics and insights

#### Subscription Management
- `GET /subscription/info` - Get subscription info
- `POST /subscription/upgrade` - Upgrade tier

#### Admin (Enterprise)
- `GET /admin/stats` - System-wide statistics

---

## 🏗️ Architecture

### Tech Stack
- **Framework**: FastAPI
- **Database**: SQLAlchemy (async) + SQLite (or PostgreSQL in production)
- **Authentication**: JWT tokens + API keys
- **Rate Limiting**: SlowAPI + Redis
- **Testing**: pytest + httpx
- **Documentation**: OpenAPI/Swagger

### Project Structure
```
volume-optimizer/
├── src/
│   ├── api.py              # Main FastAPI application
│   ├── auth.py             # Authentication & authorization
│   ├── config.py           # Configuration management
│   ├── database.py         # Database models & session
│   ├── models.py           # Pydantic models
│   ├── volume_calculator.py # Core calculation logic
│   └── volume_data.py      # Volume landmarks data
├── tests/
│   ├── test_api.py         # API endpoint tests
│   └── test_calculator.py  # Calculator logic tests
├── .env.example            # Environment variables template
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker image definition
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

---

## 🔒 Security

### Best Practices

1. **Change Default Secrets**
   ```bash
   # Generate a secure secret key
   openssl rand -hex 32
   # Add to .env: SECRET_KEY=your-generated-key
   ```

2. **Use HTTPS in Production**
   - Deploy behind a reverse proxy (nginx, Caddy)
   - Enable SSL/TLS certificates

3. **Database Security**
   - Use PostgreSQL in production (not SQLite)
   - Enable connection encryption
   - Use connection pooling

4. **Rate Limiting**
   - Configure Redis for production
   - Adjust rate limits based on your needs

---

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v
```

---

## 🚀 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `DEBUG=False`
- [ ] Configure Redis for rate limiting
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS for your domain
- [ ] Set up monitoring and logging
- [ ] Enable backups for database
- [ ] Configure email for notifications
- [ ] Set up payment processing (Stripe)

### Environment Variables

```bash
# Application
APP_NAME="Volume Optimizer Pro"
DEBUG=False

# Database (use PostgreSQL in production)
DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname"

# Security
SECRET_KEY="your-super-secret-key-minimum-32-characters"
ALGORITHM="HS256"

# Rate Limiting
REDIS_URL="redis://your-redis-host:6379"
RATE_LIMIT_ENABLED=True

# Subscription Limits
FREE_TIER_DAILY_LIMIT=100
PRO_TIER_DAILY_LIMIT=10000
ENTERPRISE_TIER_DAILY_LIMIT=1000000
```

### Deploy with Docker

```bash
# Build production image
docker build -t volume-optimizer-pro .

# Run with production settings
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  --name volume-optimizer \
  volume-optimizer-pro
```

---

## 💡 Usage Examples

### Python Client

```python
import requests

API_KEY = "vo_your_api_key_here"
BASE_URL = "http://localhost:8000"

headers = {"X-API-Key": API_KEY}

# Get volume recommendation
response = requests.post(
    f"{BASE_URL}/v1/predict-volume",
    headers=headers,
    json={
        "current_sets": 15,
        "training_level": "intermediate",
        "progress": "no",
        "recovered": "yes",
        "muscle_group": "chest"
    }
)

print(response.json())
# Output: {"volume_prediction": "Increase to at least 15 sets per week (MAV)", ...}

# Get subscription info
response = requests.get(
    f"{BASE_URL}/subscription/info",
    headers=headers
)

print(response.json())
# Output: {"tier": "free", "daily_limit": 100, "usage_today": 1, ...}
```

### JavaScript Client

```javascript
const API_KEY = "vo_your_api_key_here";
const BASE_URL = "http://localhost:8000";

// Get volume recommendation
const response = await fetch(`${BASE_URL}/v1/predict-volume`, {
  method: "POST",
  headers: {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    current_sets: 15,
    training_level: "intermediate",
    progress: "no",
    recovered: "yes",
    muscle_group: "chest"
  })
});

const data = await response.json();
console.log(data);
```

---

## 📈 Monetization Strategy

### Revenue Streams

1. **Subscription Revenue**
   - Free tier: Lead generation
   - Pro tier: $19/month × target users
   - Enterprise tier: $199/month × business clients

2. **API Usage**
   - Rate limits enforce tier upgrades
   - Usage tracking for billing

3. **Future Opportunities**
   - Mobile app (iOS/Android)
   - White-label solutions
   - Training program partnerships
   - Affiliate marketing

### Growth Strategy

1. **Free Tier**: Attract users with value
2. **Pro Tier**: Convert with advanced features
3. **Enterprise**: Target gyms, trainers, apps
4. **Integration**: Partner with fitness platforms

---

## 🤝 Support

### Getting Help

- **Documentation**: `http://localhost:8000/docs`
- **Email**: support@volumeoptimizer.pro
- **Issues**: [GitHub Issues](https://github.com/yourusername/volume-optimizer/issues)

### Support by Tier

- **Free**: Community support (GitHub Issues)
- **Pro**: Priority email support (24-48h response)
- **Enterprise**: Dedicated support (4h response SLA)

---

## 📝 License

Commercial License - See LICENSE file for details.

For commercial use inquiries, contact: sales@volumeoptimizer.pro

---

## 🙏 Acknowledgments

- Volume landmarks based on research by Dr. Mike Israetel and Renaissance Periodization
- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [uv](https://github.com/astral-sh/uv)

---

## 🗺️ Roadmap

### Phase 1 (Current) ✅
- [x] Core volume calculator
- [x] API authentication
- [x] Tiered subscriptions
- [x] Rate limiting
- [x] Training history

### Phase 2 🚧
- [ ] Payment integration (Stripe)
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Mobile SDK

### Phase 3 📋
- [ ] Machine learning recommendations
- [ ] Exercise database integration
- [ ] Social features
- [ ] Coaching marketplace

---

**Ready to optimize your training volume? Start for free today!**

```bash
uv run uvicorn src.api:app --reload
```

Visit `http://localhost:8000/docs` to get started.
