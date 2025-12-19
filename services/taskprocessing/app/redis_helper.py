"""
Redis helper for Booking Service
Provides caching and session management utilities
"""
import os
from typing import Optional, Dict, Any
from common.pyportal_common.cache_handlers import get_redis_client, RedisClient


class BookingRedisHelper:
    """
    Redis helper specific to Booking Service
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
    
    # ==================== Booking Cache ====================
    
    def cache_booking(self, booking_id: int, booking_data: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Cache booking data
        
        Args:
            booking_id: Booking ID
            booking_data: Booking data dictionary
            ttl: Cache TTL in seconds (default: 1 hour)
        
        Returns:
            True if successful
        """
        cache_key = f"booking:{booking_id}"
        return self.redis_client.cache_set(cache_key, booking_data, ttl)
    
    def get_cached_booking(self, booking_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached booking data
        
        Args:
            booking_id: Booking ID
        
        Returns:
            Booking data dictionary, or None if not cached
        """
        cache_key = f"booking:{booking_id}"
        return self.redis_client.cache_get(cache_key)
    
    def invalidate_booking_cache(self, booking_id: int) -> bool:
        """Invalidate booking cache"""
        cache_key = f"booking:{booking_id}"
        return self.redis_client.cache_delete(cache_key)
    
    # ==================== User Bookings Cache ====================
    
    def cache_user_bookings(self, user_id: int, bookings: list, ttl: int = 1800) -> bool:
        """
        Cache user's bookings list
        
        Args:
            user_id: User ID
            bookings: List of bookings
            ttl: Cache TTL in seconds (default: 30 minutes)
        """
        cache_key = f"user:bookings:{user_id}"
        return self.redis_client.cache_set(cache_key, {'bookings': bookings}, ttl)
    
    def get_cached_user_bookings(self, user_id: int) -> Optional[list]:
        """Get cached user bookings"""
        cache_key = f"user:bookings:{user_id}"
        data = self.redis_client.cache_get(cache_key)
        if data and isinstance(data, dict):
            return data.get('bookings')
        return None
    
    def invalidate_user_bookings_cache(self, user_id: int) -> bool:
        """Invalidate user bookings cache"""
        cache_key = f"user:bookings:{user_id}"
        return self.redis_client.cache_delete(cache_key)
    
    # ==================== Flight Availability Cache ====================
    
    def cache_flight_availability(self, flight_id: int, available_seats: int, ttl: int = 300) -> bool:
        """
        Cache flight availability
        
        Args:
            flight_id: Flight ID
            available_seats: Number of available seats
            ttl: Cache TTL in seconds (default: 5 minutes)
        """
        cache_key = f"flight:availability:{flight_id}"
        return self.redis_client.set(cache_key, str(available_seats), ttl)
    
    def get_cached_flight_availability(self, flight_id: int) -> Optional[int]:
        """Get cached flight availability"""
        cache_key = f"flight:availability:{flight_id}"
        seats_str = self.redis_client.get(cache_key)
        if seats_str:
            try:
                return int(seats_str)
            except (ValueError, TypeError):
                return None
        return None
    
    def invalidate_flight_availability_cache(self, flight_id: int) -> bool:
        """Invalidate flight availability cache"""
        cache_key = f"flight:availability:{flight_id}"
        return self.redis_client.cache_delete(cache_key)

