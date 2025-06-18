from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import threading

class CacheService:
    """
    In-memory cache service with TTL support.
    Thread-safe implementation for caching data with automatic expiration.
    """
    
    def __init__(self):
        """Initialize the cache service with thread-safe storage."""
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    def set(self, key: str, value: Any, ttl_minutes: int = 5) -> None:
        """
        Set a value in the cache with TTL.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
            ttl_minutes (int): Time to live in minutes (default: 5)
        """
        with self._lock:
            expiry_time = datetime.utcnow() + timedelta(minutes=ttl_minutes)
            self._cache[key] = {
                'value': value,
                'expiry': expiry_time
            }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            Optional[Any]: Cached value if exists and not expired, None otherwise
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            cache_item = self._cache[key]
            if datetime.utcnow() > cache_item['expiry']:
                # Remove expired item
                del self._cache[key]
                return None
            
            return cache_item['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            bool: True if key was deleted, False if key didn't exist
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear_expired(self) -> int:
        """
        Clear all expired items from the cache.
        
        Returns:
            int: Number of expired items removed
        """
        with self._lock:
            current_time = datetime.utcnow()
            expired_keys = [
                key for key, item in self._cache.items()
                if current_time > item['expiry']
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)

# Global cache instance
cache_service = CacheService()