# Redis Setup and Usage

## Quick Start

### 1. Start Redis

Redis is already configured in `docker-compose.yml`. Just start it:

```bash
docker-compose up -d redis
```

Or start all services:

```bash
docker-compose up -d
```

### 2. Verify Redis is Running

```bash
# Check Redis status
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG
```

### 3. Use Redis in Your Services

```python
# In your service code
from app.redis_helper import UserManagementRedisHelper

# Initialize helper
redis_helper = UserManagementRedisHelper()

# Cache user data
redis_helper.cache_user(user_id=123, user_data={'name': 'John'}, ttl=3600)

# Get cached user
user = redis_helper.get_cached_user(123)
```

## What Was Added

### 1. Redis Service
- Added to `docker-compose.yml`
- Uses `redis:7.2-alpine` image
- Port 6379 exposed
- AOF persistence enabled

### 2. Redis Client Library
- Location: `common/pyportal_common/cache_handlers/redis_client.py`
- Provides: Basic operations, JSON ops, session management, caching

### 3. Service-Specific Helpers
- `services/usermanagement/app/redis_helper.py` - User Management Redis helper
- `services/taskprocessing/app/redis_helper.py` - Task Processing Redis helper

### 4. Dependencies
- Added `redis` to `requirements.txt`
- Added `Flask-Session` for Flask session management (optional)

## Redis Database Allocation

| Service | Redis DB | Purpose |
|---------|----------|---------|
| User Management | 0 | User cache, sessions, rate limiting |
| Task Processing | 1 | Task cache, task data |
| Notification | 2 | Notification cache |

## Common Use Cases

### Caching User Data

```python
from app.redis_helper import UserManagementRedisHelper

redis_helper = UserManagementRedisHelper()

# Cache user after database fetch
user = get_user_from_db(user_id)
redis_helper.cache_user(user_id, user, ttl=3600)

# Get user (checks cache first)
def get_user(user_id):
 cached = redis_helper.get_cached_user(user_id)
 if cached:
 return cached
 user = get_user_from_db(user_id)
 redis_helper.cache_user(user_id, user)
 return user
```

### Session Management

```python
import uuid
from app.redis_helper import UserManagementRedisHelper

redis_helper = UserManagementRedisHelper()

# Create session
session_id = str(uuid.uuid4())
redis_helper.create_session(
 session_id=session_id,
 user_id=123,
 user_data={'username': 'john'},
 ttl=3600
)

# Get session
session = redis_helper.get_session(session_id)
if session:
 user_id = session['user_id']
```

### Rate Limiting

```python
from app.redis_helper import UserManagementRedisHelper

redis_helper = UserManagementRedisHelper()

# Check rate limit
is_allowed, remaining = redis_helper.check_rate_limit(
 key=f"api:user:{user_id}",
 limit=10, # 10 requests
 window=60 # per minute
)

if not is_allowed:
 return {"error": "Rate limit exceeded"}, 429
```

## Environment Variables

Each service needs Redis configuration:

```bash
REDIS_HOST=redis # Redis hostname
REDIS_PORT=6379 # Redis port
REDIS_DB=0 # Redis database number (service-specific)
REDIS_PASSWORD= # Redis password (optional)
```

## Monitoring

### Check Redis Status

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check info
INFO

# Monitor commands
MONITOR

# Check memory
INFO memory

# List keys (be careful!)
KEYS *
```

### View Service-Specific Keys

```bash
# User Management keys (DB 0)
docker-compose exec redis redis-cli -n 0
KEYS user:*

# Booking keys (DB 1)
docker-compose exec redis redis-cli -n 1
KEYS booking:*  # Legacy key pattern (task processing uses this pattern)
```

## Next Steps

1. Redis is configured and ready
2. Integrate caching into your API endpoints
3. Implement session management
4. Add rate limiting where needed
5. Monitor Redis memory usage

For detailed documentation, see `docs/redis_integration.md`.

