"""
Redis helper for Task Processing Service
Provides caching and session management utilities
"""
import os
from typing import Optional, Dict, Any
from common.pyportal_common.cache_handlers import get_redis_client, RedisClient


class TaskRedisHelper:
    """
    Redis helper specific to Task Processing Service
    """
    
    def __init__(self, redis_client: Optional[RedisClient] = None):
        """
        Initialize Redis helper
        
        Args:
            redis_client: Optional Redis client instance (uses singleton if not provided)
        """
        self.redis_client = redis_client or get_redis_client(
            db=int(os.getenv('REDIS_DB', 1))
        )
    
    # ==================== Task Cache ====================
    
    def cache_task(self, task_id: int, task_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache task data
        
        Args:
            task_id: Task ID
            task_data: Task data dictionary
            ttl: Cache TTL in seconds (default: 1 hour)
        
        Returns:
            True if successful
        """
        cache_key = f"task:{task_id}"
        return self.redis_client.cache_set(cache_key, task_data, ttl)
    
    def get_cached_task(self, task_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached task data
        
        Args:
            task_id: Task ID
        
        Returns:
            Task data dictionary, or None if not cached
        """
        cache_key = f"task:{task_id}"
        return self.redis_client.cache_get(cache_key)
    
    def invalidate_task_cache(self, task_id: int) -> bool:
        """Invalidate task cache"""
        cache_key = f"task:{task_id}"
        return self.redis_client.cache_delete(cache_key)
    
    # ==================== User Tasks Cache ====================
    
    def cache_user_tasks(self, user_id: int, tasks: list, ttl: int = 1800) -> bool:
        """
        Cache user's tasks list
        
        Args:
            user_id: User ID
            tasks: List of tasks
            ttl: Cache TTL in seconds (default: 30 minutes)
        """
        cache_key = f"user:tasks:{user_id}"
        return self.redis_client.cache_set(cache_key, {'tasks': tasks}, ttl)
    
    def get_cached_user_tasks(self, user_id: int) -> Optional[list]:
        """Get cached user tasks"""
        cache_key = f"user:tasks:{user_id}"
        data = self.redis_client.cache_get(cache_key)
        if data and isinstance(data, dict):
            return data.get('tasks')
        return None
    
    def invalidate_user_tasks_cache(self, user_id: int) -> bool:
        """Invalidate user tasks cache"""
        cache_key = f"user:tasks:{user_id}"
        return self.redis_client.cache_delete(cache_key)

