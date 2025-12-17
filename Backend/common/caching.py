"""
Redis Caching Configuration
Sistema Médico Integral - Sprint 3
"""
import os
from typing import Any, Callable, Optional
from functools import wraps
import json
import hashlib

# Importación condicional para permitir funcionamiento sin redis
try:
    from flask_caching import Cache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    Cache = None


# Configuración global de caché
_cache_instance: Optional[Any] = None


def get_cache_config() -> dict:
    """
    Get cache configuration based on environment.
    
    Returns:
        dict: Cache configuration for Flask-Caching
    """
    cache_type = os.getenv('CACHE_TYPE', 'simple')
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    if cache_type == 'redis':
        return {
            'CACHE_TYPE': 'RedisCache',
            'CACHE_REDIS_URL': redis_url,
            'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TTL', 300)),
            'CACHE_KEY_PREFIX': 'medical_system:',
        }
    elif cache_type == 'memcached':
        return {
            'CACHE_TYPE': 'MemcachedCache',
            'CACHE_MEMCACHED_SERVERS': os.getenv('MEMCACHED_SERVERS', 'localhost:11211').split(','),
            'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TTL', 300)),
            'CACHE_KEY_PREFIX': 'medical_system:',
        }
    elif cache_type == 'filesystem':
        return {
            'CACHE_TYPE': 'FileSystemCache',
            'CACHE_DIR': os.getenv('CACHE_DIR', '/tmp/flask_cache'),
            'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TTL', 300)),
            'CACHE_THRESHOLD': 1000,
        }
    else:
        # Simple cache (in-memory, no persistence)
        return {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TTL', 300)),
            'CACHE_THRESHOLD': 500,
        }


def init_cache(app) -> Optional[Any]:
    """
    Initialize cache for Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        Cache instance or None if caching is disabled
    """
    global _cache_instance
    
    if not CACHE_AVAILABLE:
        app.logger.warning(
            "flask-caching no está instalado. "
            "El caché no estará disponible. "
            "Ejecute: pip install flask-caching redis"
        )
        return None
    
    cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    if not cache_enabled:
        app.logger.info("Caché deshabilitado por configuración")
        return None
    
    config = get_cache_config()
    app.config.from_mapping(config)
    
    _cache_instance = Cache(app)
    
    app.logger.info(
        f"Caché inicializado. Tipo: {config['CACHE_TYPE']}, "
        f"TTL: {config.get('CACHE_DEFAULT_TIMEOUT', 300)}s"
    )
    
    return _cache_instance


def get_cache() -> Optional[Any]:
    """
    Get the global cache instance.
    
    Returns:
        Cache instance or None
    """
    return _cache_instance


def make_cache_key(*args, **kwargs) -> str:
    """
    Generate a unique cache key based on function arguments.
    
    Returns:
        str: MD5 hash of the arguments
    """
    key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached_response(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator for caching API responses.
    
    Works even if cache is not available (falls through to original function).
    
    Args:
        timeout: Cache TTL in seconds
        key_prefix: Prefix for cache key
        
    Returns:
        Decorator function
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache = get_cache()
            
            if cache is None:
                # Cache not available, execute function directly
                return f(*args, **kwargs)
            
            # Generate cache key
            cache_key = f"{key_prefix}:{f.__name__}:{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        
        return decorated_function
    return decorator


def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching a pattern.
    
    Note: Only works with Redis cache type.
    
    Args:
        pattern: Pattern to match (e.g., 'medical_system:patients:*')
        
    Returns:
        int: Number of keys deleted
    """
    cache = get_cache()
    
    if cache is None:
        return 0
    
    # Only works with Redis
    if hasattr(cache, 'cache') and hasattr(cache.cache, '_read_client'):
        redis_client = cache.cache._read_client
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
    
    return 0


# Predefined cache decorators for common use cases
class CachePresets:
    """Predefined caching configurations for common patterns."""
    
    # Catálogos (raramente cambian)
    CATALOGS = {'timeout': 3600, 'key_prefix': 'catalogs'}  # 1 hora
    
    # Listados con paginación
    LISTS = {'timeout': 300, 'key_prefix': 'lists'}  # 5 minutos
    
    # Datos de usuario
    USER_DATA = {'timeout': 600, 'key_prefix': 'user'}  # 10 minutos
    
    # Reportes
    REPORTS = {'timeout': 1800, 'key_prefix': 'reports'}  # 30 minutos
    
    # Datos volátiles (inventario, citas del día)
    VOLATILE = {'timeout': 60, 'key_prefix': 'volatile'}  # 1 minuto


# Ejemplo de uso:
# from common.caching import cached_response, CachePresets
#
# @app.route('/api/catalogs/treatments')
# @cached_response(**CachePresets.CATALOGS)
# def get_treatments():
#     return jsonify(TreatmentModel.list_all())
