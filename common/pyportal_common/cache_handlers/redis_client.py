"""
Redis client wrapper for caching and session management
"""
import os
import json
import redis
from typing import Optional, Any, Dict

class RedisClient:
    """
    Redis client wrapper for caching and session management

    Provides methods for:
    - Key-value caching
    - Session storage
    - TTL (Time To Live) management
    - JSON serialization/deserialization
    """

    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 db: int = 0,
                 password: Optional[str] = None,
                 decode_responses: bool = True,
                 socket_timeout: int = 5,
                 socket_connect_timeout: int = 5):
        """
        Initialize Redis client

        Args:
            host: Redis host (default: from REDIS_HOST env var or 'redis')
            port: Redis port (default: from REDIS_PORT env var or 6379)
            db: Redis database number (default: 0)
            password: Redis password (default: from REDIS_PASSWORD env var)
            decode_responses: Decode responses as strings (default: True)
            socket_timeout: Socket timeout in seconds for Redis operations
                          (GET/SET/etc). These are blocking I/O operations
                          that run on your application threads. Prevents
                          threads from hanging indefinitely if Redis becomes
                          unresponsive during a request. Without this, a slow
                          Redis operation could block your application threads
                          forever, making them unavailable for other requests.
            socket_connect_timeout: Socket connect timeout in seconds for
                                  establishing the initial TCP connection to
                                  Redis. This is a blocking I/O operation that
                                  runs on your application threads. Prevents
                                  threads from hanging when Redis is down or
                                  unreachable. Without this, connection
                                  attempts could wait forever, exhausting
                                  connection pools and blocking application
                                  startup/threads.
        """
        self.host = host or os.getenv('REDIS_HOST', 'redis')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.db = db
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.decode_responses = decode_responses

        # Connection pool for better performance - reuses TCP socket
        # connections to avoid the overhead of establishing new connections.
        # All operations (GET/SET/etc) are blocking I/O operations that run
        # on application threads, so socket timeouts prevent threads from
        # hanging indefinitely.
        self.pool = redis.ConnectionPool(
            host=self.host,
            port=self.port,
            db=self.db,
            password=self.password,
            decode_responses=decode_responses,
            socket_timeout=socket_timeout,
            socket_connect_timeout=socket_connect_timeout,
            max_connections=50
        )

        self.client = redis.Redis(connection_pool=self.pool)

    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.client.ping()
        except Exception:
            return False

    # ==================== Basic Operations ====================

    def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis

        Args:
            key: Redis key

        Returns:
            Value as string, or None if key doesn't exist
        """
        try:
            return self.client.get(key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """
        Set value in Redis

        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds (None for no expiration)

        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl:
                return self.client.setex(key, ttl, value)
            else:
                return self.client.set(key, value)
        except Exception:
            return False

    def delete(self, *keys: str) -> int:
        """
        Delete keys from Redis

        Args:
            *keys: One or more keys to delete

        Returns:
            Number of keys deleted
        """
        try:
            return self.client.delete(*keys)
        except Exception:
            return 0

    def exists(self, key: str) -> bool:
        """Check if key exists in Redis"""
        try:
            return bool(self.client.exists(key))
        except Exception:
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for a key"""
        try:
            return self.client.expire(key, ttl)
        except Exception:
            return False

    # ==================== JSON Operations ====================

    def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get JSON value from Redis

        Args:
            key: Redis key

        Returns:
            Deserialized JSON object, or None if key doesn't exist
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except (json.JSONDecodeError, TypeError, Exception):
            return None

    def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set JSON value in Redis

        Args:
            key: Redis key
            value: Dictionary to serialize and store
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            return self.set(key, json_value, ttl)
        except (TypeError, ValueError, Exception):
            return False

    # ==================== Session Management ====================

    def set_session(self, session_id: str, session_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Store session data

        Args:
            session_id: Unique session identifier
            session_data: Session data dictionary
            ttl: Session TTL in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        return self.set_json(key, session_data, ttl)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data

        Args:
            session_id: Unique session identifier

        Returns:
            Session data dictionary, or None if session doesn't exist
        """
        key = f"session:{session_id}"
        return self.get_json(key)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete session

        Args:
            session_id: Unique session identifier

        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        return bool(self.delete(key))

    def refresh_session(self, session_id: str, ttl: int = 3600) -> bool:
        """
        Refresh session TTL

        Args:
            session_id: Unique session identifier
            ttl: New TTL in seconds

        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        return self.expire(key, ttl)

    # ==================== Cache Operations ====================

    def cache_get(self, cache_key: str) -> Optional[Any]:
        """
        Get cached value

        Args:
            cache_key: Cache key

        Returns:
            Cached value (deserialized if JSON), or None
        """
        return self.get_json(cache_key) or self.get(cache_key)

    def cache_set(self, cache_key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set cached value

        Args:
            cache_key: Cache key
            value: Value to cache (dict/str/other)
            ttl: Cache TTL in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if isinstance(value, dict):
            return self.set_json(cache_key, value, ttl)
        else:
            return self.set(cache_key, str(value), ttl)

    def cache_delete(self, cache_key: str) -> bool:
        """Delete cached value"""
        return bool(self.delete(cache_key))

    def cache_pattern_delete(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern

        Args:
            pattern: Redis key pattern (e.g., "cache:user:*")

        Returns:
            Number of keys deleted
        """
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception:
            return 0

    # ==================== Hash Operations ====================

    def hset(self, name: str, key: str, value: str) -> bool:
        """Set field in hash"""
        try:
            return bool(self.client.hset(name, key, value))
        except Exception:
            return False

    def hget(self, name: str, key: str) -> Optional[str]:
        """Get field from hash"""
        try:
            return self.client.hget(name, key)
        except Exception:
            return None

    def hgetall(self, name: str) -> Dict[str, str]:
        """Get all fields from hash"""
        try:
            return self.client.hgetall(name) or {}
        except Exception:
            return {}

    def hdel(self, name: str, *keys: str) -> int:
        """Delete fields from hash"""
        try:
            return self.client.hdel(name, *keys)
        except Exception:
            return 0

    def close(self):
        """Close Redis connection"""
        try:
            self.client.close()
            self.pool.disconnect()
        except Exception:
            pass

# Global Redis client instance
_redis_client: Optional[RedisClient] = None


def get_redis_client(host: Optional[str] = None,
                     port: Optional[int] = None,
                     db: int = 0,
                     password: Optional[str] = None) -> RedisClient:
    """
    Get or create global Redis client instance (singleton pattern)

    Args:
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Redis password

    Returns:
        RedisClient instance
    """
    global _redis_client

    if _redis_client is None:
        _redis_client = RedisClient(
            host=host,
            port=port,
            db=db,
            password=password
        )

    return _redis_client


def init_redis_client(host: Optional[str] = None,
                     port: Optional[int] = None,
                     db: int = 0,
                     password: Optional[str] = None) -> RedisClient:
    """
    Initialize Redis client (explicit initialization)

    Args:
        host: Redis host
        port: Redis port
        db: Redis database number
        password: Redis password

    Returns:
        RedisClient instance
    """
    return get_redis_client(host=host, port=port, db=db, password=password)
