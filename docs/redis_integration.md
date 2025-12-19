# Redis Integration Guide

## Overview

Redis has been integrated into the microservices architecture for:
- **Caching**: Improve performance by caching frequently accessed data
- **Session Management**: Store user sessions across services
- **Rate Limiting**: Implement rate limiting for API endpoints

## Architecture

### Redis Setup

Redis is running as a separate service in Docker Compose:
- **Container**: `redis`
- **Image**: `redis:7.2-alpine`
- **Port**: `6379`
- **Persistence**: AOF (Append Only File) enabled
- **Volume**: `redis-data` for data persistence

### Database Allocation

Each service uses a separate Redis database to avoid key conflicts:

| Service | Redis DB | Usage |
|---------|----------|-------|
| User Management | 0 | User cache, sessions, rate limiting |
| Task Processing | 1 | Task cache, task data (legacy: BookingRedisHelper) |
| Notification | 2 | Notification cache, delivery status |

## Usage Examples

### User Management Service

```python
from app.redis_helper import UserManagementRedisHelper

# Initialize helper
redis_helper = UserManagementRedisHelper()

# Cache user data
user_data = {
    'id': 123,
    'username': 'john_doe',
    'email': 'john@example.com',
    'firstName': 'John',
    'lastName': 'Doe'
}
redis_helper.cache_user(user_id=123, user_data=user_data, ttl=3600)

# Get cached user
cached_user = redis_helper.get_cached_user(123)
if cached_user:
    print(f"Cached user: {cached_user}")
else:
    # Fetch from database
    user = fetch_user_from_db(123)
    redis_helper.cache_user(123, user, ttl=3600)

# Session management
session_id = "sess_abc123"
redis_helper.create_session(
    session_id=session_id,
    user_id=123,
    user_data=user_data,
    ttl=3600
)

# Get session
session = redis_helper.get_session(session_id)

# Rate limiting
is_allowed, remaining = redis_helper.check_rate_limit(
    key=f"user:{user_id}",
    limit=10,
    window=60
)
```

### Task Processing Service

```python
from app.redis_helper import BookingRedisHelper  # Legacy class name, used for task processing

# Initialize helper
redis_helper = BookingRedisHelper()

# Cache task data
task_data = {
    'taskId': 456,
    'userId': 123,
    'status': 'processing',
    'details': {...}
}
redis_helper.cache_booking(456, task_data, ttl=3600)  # Legacy method name

# Get cached task
cached_task = redis_helper.get_cached_booking(456)  # Legacy method name

# Cache task-related data
redis_helper.cache_flight_availability(
    flight_id=789,
    available_seats=10,
    ttl=300  # 5 minutes
)

# Get cached availability
available = redis_helper.get_cached_flight_availability(789)
```

## Direct Redis Client Usage

For advanced use cases, use the Redis client directly:

```python
from common.pyportal_common.cache_handlers import get_redis_client

# Get Redis client
redis_client = get_redis_client(db=0)

# Basic operations
redis_client.set("key", "value", ttl=60)
value = redis_client.get("key")

# JSON operations
data = {"name": "John", "age": 30}
redis_client.set_json("user:123", data, ttl=3600)
retrieved = redis_client.get_json("user:123")

# Hash operations
redis_client.hset("user:123:profile", "email", "john@example.com")
email = redis_client.hget("user:123:profile", "email")
profile = redis_client.hgetall("user:123:profile")
```

## Configuration

### Environment Variables

Set in `docker-compose.yml` or service `.env` files:

```bash
REDIS_HOST=redis           # Redis host (default: redis)
REDIS_PORT=6379           # Redis port (default: 6379)
REDIS_DB=0                # Redis database number
REDIS_PASSWORD=           # Redis password (optional)
```

### Service Configuration

Each service uses its own Redis database:

- **User Management**: `REDIS_DB=0`
- **Task Processing**: `REDIS_DB=1`
- **Notification**: `REDIS_DB=2`

## Caching Strategies

### 1. Cache-Aside Pattern

```python
def get_user(user_id: int):
    # Try cache first
    cached_user = redis_helper.get_cached_user(user_id)
    if cached_user:
        return cached_user
    
    # Fetch from database
    user = db.get_user(user_id)
    
    # Store in cache
    if user:
        redis_helper.cache_user(user_id, user, ttl=3600)
    
    return user
```

### 2. Write-Through Pattern

```python
def create_user(user_data: dict):
    # Save to database
    user = db.create_user(user_data)
    
    # Update cache immediately
    redis_helper.cache_user(user['id'], user, ttl=3600)
    
    return user
```

### 3. Cache Invalidation

```python
def update_user(user_id: int, user_data: dict):
    # Update database
    user = db.update_user(user_id, user_data)
    
    # Invalidate cache
    redis_helper.invalidate_user_cache(user_id)
    
    # Optionally update cache with new data
    redis_helper.cache_user(user_id, user, ttl=3600)
    
    return user
```

## Session Management

### Creating Sessions

```python
import uuid
from app.redis_helper import UserManagementRedisHelper

redis_helper = UserManagementRedisHelper()

# Generate session ID
session_id = str(uuid.uuid4())

# Create session
redis_helper.create_session(
    session_id=session_id,
    user_id=123,
    user_data={'username': 'john_doe', 'role': 'user'},
    ttl=3600  # 1 hour
)

# Return session ID to client (in cookie/token)
```

### Retrieving Sessions

```python
# Get session
session = redis_helper.get_session(session_id)
if session:
    user_id = session['user_id']
    user_data = session['user_data']
else:
    # Session expired or doesn't exist
    return unauthorized_response()
```

### Refreshing Sessions

```python
# Refresh session TTL
redis_helper.refresh_session(session_id, ttl=3600)
```

## Rate Limiting

### Implement Rate Limiting in API Endpoints

```python
from flask import request, jsonify
from app.redis_helper import UserManagementRedisHelper

redis_helper = UserManagementRedisHelper()

@app.route('/api/v1/airliner/registerUser', methods=['POST'])
def register_user():
    # Get client IP or user ID for rate limiting
    client_id = request.remote_addr  # or user_id if authenticated
    
    # Check rate limit
    is_allowed, remaining = redis_helper.check_rate_limit(
        key=f"register:{client_id}",
        limit=5,  # 5 requests
        window=60  # per minute
    )
    
    if not is_allowed:
        return jsonify({
            'error': 'Rate limit exceeded',
            'retry_after': 60
        }), 429
    
    # Add remaining requests to response headers
    response = jsonify({'message': 'User registered'})
    response.headers['X-RateLimit-Remaining'] = str(remaining)
    return response
```

## Key Naming Conventions

Use consistent key naming for easier management:

- **Users**: `user:{user_id}`
- **User Lookup**: `user:lookup:username:{username}`, `user:lookup:email:{email}`
- **Sessions**: `session:{session_id}`
- **Tasks**: `booking:{task_id}` (legacy key pattern, used for task processing)
- **User Tasks**: `user:bookings:{user_id}` (legacy key pattern)
- **Flight Availability**: `flight:availability:{flight_id}`
- **Rate Limits**: `rate_limit:{service}:{identifier}`

## Monitoring and Debugging

### Check Redis Connection

```python
from common.pyportal_common.cache_handlers import get_redis_client

redis_client = get_redis_client()
if redis_client.ping():
    print("Redis connection successful")
else:
    print("Redis connection failed")
```

### View Redis Data

```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# List all keys (be careful in production)
KEYS *

# Get specific key
GET user:123

# Check database
SELECT 0  # Switch to DB 0
KEYS user:*

# Monitor commands
MONITOR
```

## Best Practices

1. **Set Appropriate TTLs**: Don't cache data indefinitely
   - User data: 1 hour
   - Booking data: 1 hour
   - Flight availability: 5 minutes
   - Sessions: 1 hour (refreshable)

2. **Handle Cache Misses**: Always have a database fallback

3. **Invalidate on Updates**: Clear cache when data changes

4. **Use Different DBs**: Separate services use different Redis databases

5. **Monitor Memory**: Redis is in-memory, monitor usage

6. **Enable Persistence**: AOF is enabled for data durability

7. **Connection Pooling**: The client uses connection pooling automatically

## Performance Considerations

- **Connection Pooling**: Already implemented in `RedisClient`
- **Pipelining**: For batch operations, use Redis pipelining
- **Memory Management**: Monitor Redis memory usage
- **TTL Management**: Set appropriate TTLs to prevent memory bloat

## Troubleshooting

### Connection Issues

```python
# Test connection
redis_client = get_redis_client()
try:
    redis_client.ping()
    print("Connected")
except Exception as e:
    print(f"Connection error: {e}")
```

### Check Service Logs

```bash
docker-compose logs redis
docker-compose logs usermanagement-service | grep -i redis
```

### Redis Memory Usage

```bash
docker-compose exec redis redis-cli INFO memory
```

