# Central API Server

**Unified data hub for all Jarvis daemons and dashboards**

## Overview

The Central API is a production-ready Flask REST API that serves as the single source of truth for all system data. All daemons push data to this API instead of isolated JSON files, providing:

- ✅ Centralized data management
- ✅ Token-based authentication
- ✅ Redis caching (with in-memory fallback)
- ✅ Rate limiting
- ✅ Comprehensive logging
- ✅ Swagger API documentation
- ✅ Full test suite
- ✅ launchd service configuration

## Quick Start

### 1. Setup

```bash
cd ~/clawd/central-api
./setup.sh
```

This will:
- Create a virtual environment
- Install dependencies
- Generate a secure API token
- Create `.env` configuration
- Run tests
- Check Redis availability

### 2. Start the Server

**Manual start:**
```bash
./start.sh
```

**Install as service (runs at boot):**
```bash
./install-service.sh
```

### 3. Verify It's Running

```bash
# Health check (no auth required)
curl http://localhost:3003/system/health

# View API docs
open http://localhost:3003/docs
```

## Configuration

### Environment Variables (`.env`)

```bash
API_TOKEN=your_secure_token_here  # Generated during setup
REDIS_ENABLED=true                # Use Redis if available
REDIS_HOST=localhost
REDIS_PORT=6379
FLASK_ENV=production
```

### Config File (`config/config.yaml`)

```yaml
api:
  host: "127.0.0.1"  # Localhost only (secure)
  port: 3003
  debug: false

auth:
  api_token: "YOUR_TOKEN"  # Synced from .env

redis:
  enabled: true
  host: "localhost"
  port: 6379
  default_ttl: 300  # Cache TTL in seconds

rate_limiting:
  enabled: true
  default_limit: "100 per minute"

logging:
  level: "INFO"
  file: "logs/central-api.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5
```

## API Endpoints

### System

- `GET /system/health` - Health check (no auth)
- `GET /system/stats` - System statistics
- `POST /system/cache/clear` - Clear all cached data

### Tasks

- `GET /tasks` - Get all tasks
- `POST /tasks` - Create a new task
- `GET /tasks/<id>` - Get specific task
- `DELETE /tasks/<id>` - Delete a task

### Opportunities

- `GET /opportunities` - Get all opportunities
- `POST /opportunities` - Add new opportunity

### Email

- `GET /email/summary` - Get email summary
- `POST /email/summary` - Update email summary

### Twitter

- `GET /twitter/opportunities` - Get Twitter opportunities
- `POST /twitter/opportunities` - Add Twitter opportunity

### Revenue

- `GET /revenue/metrics` - Get revenue metrics
- `POST /revenue/metrics` - Update revenue metrics

### Fitness

- `GET /fitness/summary?date=YYYY-MM-DD` - Get fitness summary
- `POST /fitness/summary` - Update fitness data

### Golf

- `GET /golf/stats` - Get golf statistics
- `POST /golf/stats` - Update golf stats

### Weather

- `GET /weather/current?location=<loc>` - Get weather
- `POST /weather/current` - Update weather data

## Authentication

All endpoints (except `/system/health`) require authentication.

**Include token in Authorization header:**

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:3003/tasks
```

**Get your token:**
```bash
grep API_TOKEN .env
```

## Using from Python (Daemon Integration)

```python
import requests
import os

class CentralAPIClient:
    """Client for Central API"""
    
    def __init__(self, base_url='http://localhost:3003', token=None):
        self.base_url = base_url
        self.token = token or os.getenv('API_TOKEN')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def add_task(self, task):
        """Add a new task"""
        response = requests.post(
            f'{self.base_url}/tasks',
            json=task,
            headers=self.headers
        )
        return response.json()
    
    def get_tasks(self):
        """Get all tasks"""
        response = requests.get(
            f'{self.base_url}/tasks',
            headers=self.headers
        )
        return response.json()
    
    def update_email_summary(self, unread_count, urgent_count):
        """Update email summary"""
        data = {
            'unread_count': unread_count,
            'urgent_count': urgent_count
        }
        response = requests.post(
            f'{self.base_url}/email/summary',
            json=data,
            headers=self.headers
        )
        return response.json()
    
    def update_revenue(self, daily, weekly, monthly, sources):
        """Update revenue metrics"""
        data = {
            'daily': daily,
            'weekly': weekly,
            'monthly': monthly,
            'sources': sources
        }
        response = requests.post(
            f'{self.base_url}/revenue/metrics',
            json=data,
            headers=self.headers
        )
        return response.json()

# Usage in your daemon
client = CentralAPIClient()
client.add_task({
    'id': 'task-123',
    'title': 'Review pull request',
    'status': 'pending',
    'priority': 'high'
})
```

## Service Management

**Status:**
```bash
launchctl list | grep central-api
```

**Stop:**
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.central-api.plist
```

**Start:**
```bash
launchctl load ~/Library/LaunchAgents/com.jarvis.central-api.plist
```

**Restart:**
```bash
launchctl unload ~/Library/LaunchAgents/com.jarvis.central-api.plist
launchctl load ~/Library/LaunchAgents/com.jarvis.central-api.plist
```

**View logs:**
```bash
# Application log
tail -f logs/central-api.log

# Error log
tail -f logs/error.log

# Access log
tail -f logs/access.log

# Service stdout/stderr
tail -f logs/stdout.log
tail -f logs/stderr.log
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=api tests/
```

## Caching

The API uses Redis for caching when available, falling back to in-memory cache.

**Cache TTL by endpoint:**
- Tasks: 60 seconds
- Opportunities: 300 seconds (5 min)
- Email summary: 300 seconds
- Revenue metrics: 600 seconds (10 min)
- Fitness data: 600 seconds
- Golf stats: 3600 seconds (1 hour)
- Weather: 600 seconds

**Clear cache:**
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:3003/system/cache/clear
```

## Rate Limiting

Default: **100 requests per minute** per IP address

Health check endpoint is not rate limited.

## Security

- **Local only:** Server binds to `127.0.0.1` (not accessible externally)
- **Token authentication:** All endpoints require valid API token
- **Rate limiting:** Prevents abuse
- **Logging:** All requests logged with IP and timestamp

## Troubleshooting

**API not starting:**
```bash
# Check logs
tail -f logs/stderr.log

# Verify port is available
lsof -i :3003

# Test configuration
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
```

**Authentication failing:**
```bash
# Verify token
grep API_TOKEN .env

# Test with curl
curl -H "Authorization: Bearer $(grep API_TOKEN .env | cut -d= -f2)" \
     http://localhost:3003/system/stats
```

**Redis not working:**
```bash
# Check Redis status
redis-cli ping

# Start Redis (if installed via Homebrew)
brew services start redis

# API will automatically fall back to in-memory cache
```

## Architecture

```
central-api/
├── api/                    # Main application code
│   ├── __init__.py
│   ├── app.py             # Flask app with all endpoints
│   ├── auth.py            # Authentication middleware
│   ├── cache.py           # Caching layer (Redis + in-memory)
│   └── storage.py         # Data storage layer
├── tests/                 # Test suite
│   ├── conftest.py        # Pytest fixtures
│   ├── test_api.py        # API endpoint tests
│   ├── test_storage.py    # Storage layer tests
│   └── test_cache.py      # Cache layer tests
├── config/                # Configuration
│   └── config.yaml
├── data/                  # Persistent data (JSON files)
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── setup.sh              # Setup script
├── start.sh              # Start server manually
├── install-service.sh    # Install launchd service
└── com.jarvis.central-api.plist  # launchd configuration
```

## Migration Guide for Daemons

**Old way (isolated JSON files):**
```python
import json

# Each daemon manages its own files
with open('data/tasks.json', 'w') as f:
    json.dump(tasks, f)
```

**New way (Central API):**
```python
from central_api_client import CentralAPIClient

client = CentralAPIClient()
for task in tasks:
    client.add_task(task)
```

Benefits:
- Single source of truth
- Automatic caching
- Rate limiting
- Centralized logging
- Authentication
- API versioning

## Production Checklist

- [x] Token authentication
- [x] Rate limiting
- [x] Comprehensive logging
- [x] Error handling
- [x] Data persistence
- [x] Caching (Redis + fallback)
- [x] API documentation (Swagger)
- [x] Test suite
- [x] Service management (launchd)
- [x] Security (localhost only)
- [x] Configuration management

## Support

**Logs location:** `~/clawd/central-api/logs/`

**Configuration:** `~/clawd/central-api/config/config.yaml`

**Data storage:** `~/clawd/central-api/data/`

**API documentation:** http://localhost:3003/docs

---

Built for Jarvis AI Assistant System
