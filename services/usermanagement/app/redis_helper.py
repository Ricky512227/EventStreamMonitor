"""

Redis helper for User Management Service

Provides caching and session management utilities

"""

import os

from typing import Optional, Dict, Any, Tuple

from common.pyportal_common.cache_handlers import get_redis_client, RedisClient


class UserManagementRedisHelper:
    """

    Redis helper specific to User Management Service

    """

    def __init__(self, redis_client: Optional[RedisClient] = None):

        """

        Initialize Redis helper

        Args:

            redis_client: Optional Redis client instance
                (uses singleton if not provided)

        """

        self.redis_client = redis_client or get_redis_client(

            db=int(os.getenv('REDIS_DB', 0))

        )

    # ==================== User Cache ====================

    def cache_user(
        self, user_id: int, user_data: Dict[str, Any], ttl: int = 3600
    ) -> bool:

        """

        Cache user data

        Args:

            user_id: User ID

            user_data: User data dictionary

            ttl: Cache TTL in seconds (default: 1 hour)

        Returns:

            True if successful

        """

        cache_key = f"user:{user_id}"

        return self.redis_client.cache_set(cache_key, user_data, ttl)

    def get_cached_user(self, user_id: int) -> Optional[Dict[str, Any]]:

        """

        Get cached user data

        Args:

            user_id: User ID

        Returns:

            User data dictionary, or None if not cached

        """

        cache_key = f"user:{user_id}"

        return self.redis_client.cache_get(cache_key)

    def invalidate_user_cache(self, user_id: int) -> bool:

        """

        Invalidate user cache

        Args:

            user_id: User ID

        Returns:

            True if successful

        """

        cache_key = f"user:{user_id}"

        return self.redis_client.cache_delete(cache_key)

    # ==================== User Lookup Cache ====================

    def cache_user_lookup(
        self, username: str, user_id: int, ttl: int = 3600
    ) -> bool:

        """

        Cache username to user_id mapping

        Args:

            username: Username

            user_id: User ID

            ttl: Cache TTL in seconds

        """

        cache_key = f"user:lookup:username:{username}"

        return self.redis_client.set(cache_key, str(user_id), ttl)

    def get_cached_user_id(self, username: str) -> Optional[int]:

        """

        Get cached user ID by username

        Args:

            username: Username

        Returns:

            User ID, or None if not cached

        """

        cache_key = f"user:lookup:username:{username}"

        user_id_str = self.redis_client.get(cache_key)

        if user_id_str:

            try:

                return int(user_id_str)

            except (ValueError, TypeError):

                return None

        return None

    def cache_email_lookup(
        self, email: str, user_id: int, ttl: int = 3600
    ) -> bool:

        """Cache email to user_id mapping"""

        cache_key = f"user:lookup:email:{email}"

        return self.redis_client.set(cache_key, str(user_id), ttl)

    def get_cached_user_id_by_email(self, email: str) -> Optional[int]:

        """Get cached user ID by email"""

        cache_key = f"user:lookup:email:{email}"

        user_id_str = self.redis_client.get(cache_key)

        if user_id_str:

            try:

                return int(user_id_str)

            except (ValueError, TypeError):

                return None

        return None

    # ==================== Session Management ====================

    def create_session(
        self,
        session_id: str,
        user_id: int,
        user_data: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:

        """

        Create user session

        Args:

            session_id: Session identifier

            user_id: User ID

            user_data: User data to store in session

            ttl: Session TTL in seconds (default: 1 hour)

        Returns:

            True if successful

        """

        session_data = {

            'user_id': user_id,

            'user_data': user_data,

            'created_at': str(os.getenv('TIMESTAMP', ''))

        }

        return self.redis_client.set_session(session_id, session_data, ttl)

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:

        """Get session data"""

        return self.redis_client.get_session(session_id)

    def delete_session(self, session_id: str) -> bool:

        """Delete session"""

        return self.redis_client.delete_session(session_id)

    def refresh_session(self, session_id: str, ttl: int = 3600) -> bool:

        """Refresh session TTL"""

        return self.redis_client.refresh_session(session_id, ttl)

    # ==================== Rate Limiting ====================

    def check_rate_limit(
        self,
        key: str,
        limit: int = 10,
        window: int = 60
    ) -> Tuple[bool, int]:

        """

        Check rate limit for a key

        Args:

            key: Rate limit key (e.g., "rate_limit:user:123")

            limit: Maximum number of requests

            window: Time window in seconds

        Returns:

            (is_allowed, remaining_requests)

        """

        rate_key = f"rate_limit:{key}"

        current = self.redis_client.get(rate_key)

        if current is None:

            # First request in window

            self.redis_client.set(rate_key, "1", window)

            return True, limit - 1

        else:

            try:

                count = int(current)

                if count < limit:

                    # Increment counter

                    self.redis_client.client.incr(rate_key)

                    return True, limit - count - 1

                else:

                    return False, 0

            except (ValueError, TypeError):

                return True, limit

    # ==================== Idempotency ====================

    def cache_idempotency_response(

        self,

        idempotency_key: str,

        response_data: Dict[str, Any],

        ttl: int = 86400

    ) -> bool:

        """

        Cache idempotency key response

        Args:

            idempotency_key: Idempotency key from X-Idempotency-Key header

            response_data: Response data to cache (status, body, headers)

            ttl: Cache TTL in seconds (default: 24 hours)

        Returns:

            True if successful

        """

        cache_key = f"idempotency:{idempotency_key}"

        return self.redis_client.cache_set(cache_key, response_data, ttl)

    def get_idempotency_response(

        self,

        idempotency_key: str

    ) -> Optional[Dict[str, Any]]:

        """

        Get cached idempotency response

        Args:

            idempotency_key: Idempotency key from X-Idempotency-Key header

        Returns:

            Cached response data (status, body, headers), or None if not found

        """

        cache_key = f"idempotency:{idempotency_key}"

        return self.redis_client.cache_get(cache_key)
