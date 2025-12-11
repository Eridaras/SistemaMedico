"""
Caching utilities for improved performance
In-memory cache with TTL support
For production, consider using Redis
"""
from functools import wraps
import time
import hashlib
import json
import pickle

class SimpleCache:
    """Simple in-memory cache with TTL"""

    def __init__(self):
        self.cache = {}
        self.timestamps = {}

    def get(self, key):
        """Get value from cache"""
        if key in self.cache:
            # Check if expired
            if key in self.timestamps:
                if time.time() - self.timestamps[key]['created'] > self.timestamps[key]['ttl']:
                    # Expired, remove from cache
                    del self.cache[key]
                    del self.timestamps[key]
                    return None

            return self.cache[key]
        return None

    def set(self, key, value, ttl=300):
        """
        Set value in cache with TTL

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 5 minutes)
        """
        self.cache[key] = value
        self.timestamps[key] = {
            'created': time.time(),
            'ttl': ttl
        }

        # Clean old entries if cache grows too large
        if len(self.cache) > 1000:
            self.cleanup()

    def delete(self, key):
        """Delete specific key from cache"""
        if key in self.cache:
            del self.cache[key]
        if key in self.timestamps:
            del self.timestamps[key]

    def clear(self):
        """Clear all cache"""
        self.cache.clear()
        self.timestamps.clear()

    def cleanup(self):
        """Remove expired entries"""
        current_time = time.time()
        keys_to_delete = []

        for key, timestamp_data in self.timestamps.items():
            if current_time - timestamp_data['created'] > timestamp_data['ttl']:
                keys_to_delete.append(key)

        for key in keys_to_delete:
            if key in self.cache:
                del self.cache[key]
            if key in self.timestamps:
                del self.timestamps[key]

    def get_stats(self):
        """Get cache statistics"""
        total_entries = len(self.cache)
        current_time = time.time()
        expired = 0

        for timestamp_data in self.timestamps.values():
            if current_time - timestamp_data['created'] > timestamp_data['ttl']:
                expired += 1

        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired,
            'expired_entries': expired
        }


# Global cache instance
cache = SimpleCache()


def cached(ttl=300, key_prefix=''):
    """
    Decorator for caching function results

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Generate cache key from function name and arguments
            key_parts = [key_prefix, f.__name__]

            # Add positional arguments
            for arg in args:
                if isinstance(arg, (str, int, float, bool)):
                    key_parts.append(str(arg))

            # Add keyword arguments
            for k, v in sorted(kwargs.items()):
                if isinstance(v, (str, int, float, bool)):
                    key_parts.append(f"{k}:{v}")

            cache_key = hashlib.md5(':'.join(key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = f(*args, **kwargs)

            # Store in cache
            cache.set(cache_key, result, ttl)

            return result

        return decorated_function
    return decorator


def cache_response(ttl=300):
    """
    Decorator for caching Flask route responses
    Use for GET endpoints only
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request

            # Only cache GET requests
            if request.method != 'GET':
                return f(*args, **kwargs)

            # Generate cache key from URL and query params
            cache_key_parts = [
                request.path,
                request.query_string.decode('utf-8')
            ]

            # Add user context if authenticated
            if hasattr(request, 'user_id'):
                cache_key_parts.append(f"user:{request.user_id}")

            cache_key = hashlib.md5(':'.join(cache_key_parts).encode()).hexdigest()

            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = f(*args, **kwargs)

            # Only cache successful responses
            if isinstance(result, tuple):
                response, status_code = result
                if status_code == 200:
                    cache.set(cache_key, result, ttl)
            else:
                cache.set(cache_key, result, ttl)

            return result

        return decorated_function
    return decorator


def invalidate_cache(pattern=None):
    """
    Invalidate cache entries

    Args:
        pattern: If provided, only invalidate keys matching pattern
    """
    if pattern is None:
        cache.clear()
    else:
        # Note: This is a simple implementation
        # For production, use Redis with pattern matching
        keys_to_delete = [
            key for key in cache.cache.keys()
            if pattern in key
        ]
        for key in keys_to_delete:
            cache.delete(key)


# Cache for specific data types
class DataCache:
    """Specialized cache for common data queries"""

    @staticmethod
    def get_roles():
        """Cache roles (rarely change)"""
        return cache.get('roles:all')

    @staticmethod
    def set_roles(roles, ttl=3600):
        """Cache roles for 1 hour"""
        cache.set('roles:all', roles, ttl)

    @staticmethod
    def get_user(user_id):
        """Cache user data"""
        return cache.get(f'user:{user_id}')

    @staticmethod
    def set_user(user_id, user_data, ttl=600):
        """Cache user for 10 minutes"""
        cache.set(f'user:{user_id}', user_data, ttl)

    @staticmethod
    def invalidate_user(user_id):
        """Invalidate user cache"""
        cache.delete(f'user:{user_id}')

    @staticmethod
    def get_products():
        """Cache product list"""
        return cache.get('products:all')

    @staticmethod
    def set_products(products, ttl=300):
        """Cache products for 5 minutes"""
        cache.set('products:all', products, ttl)

    @staticmethod
    def invalidate_products():
        """Invalidate products cache"""
        cache.delete('products:all')

    @staticmethod
    def get_treatments():
        """Cache treatment list"""
        return cache.get('treatments:all')

    @staticmethod
    def set_treatments(treatments, ttl=300):
        """Cache treatments for 5 minutes"""
        cache.set('treatments:all', treatments, ttl)

    @staticmethod
    def invalidate_treatments():
        """Invalidate treatments cache"""
        cache.delete('treatments:all')
