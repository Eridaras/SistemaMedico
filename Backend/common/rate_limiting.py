"""
Rate Limiting Configuration
Sistema Médico Integral - Sprint 3
"""
import os
from typing import Any, Optional
from flask import Flask, request, jsonify

# Importación condicional
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    LIMITER_AVAILABLE = True
except ImportError:
    LIMITER_AVAILABLE = False
    Limiter = None
    get_remote_address = None


# Instancia global del limiter
_limiter_instance: Optional[Any] = None


def get_client_ip() -> str:
    """
    Get the real client IP address, handling proxies.
    
    Returns:
        str: Client IP address
    """
    # Check for forwarded headers (behind proxy/load balancer)
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # Take the first IP in the chain (original client)
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    return request.remote_addr or '127.0.0.1'


def init_rate_limiter(app: Flask) -> Optional[Any]:
    """
    Initialize rate limiter for Flask application.
    
    Args:
        app: Flask application instance
        
    Returns:
        Limiter instance or None if disabled
    """
    global _limiter_instance
    
    if not LIMITER_AVAILABLE:
        app.logger.warning(
            "flask-limiter no está instalado. "
            "Rate limiting no estará disponible. "
            "Ejecute: pip install flask-limiter"
        )
        return None
    
    rate_limit_enabled = os.getenv('RATE_LIMIT_ENABLED', 'true').lower() == 'true'
    if not rate_limit_enabled:
        app.logger.info("Rate limiting deshabilitado por configuración")
        return None
    
    # Configuración de storage
    storage_uri = os.getenv('RATE_LIMIT_STORAGE', 'memory://')
    redis_url = os.getenv('REDIS_URL')
    
    if redis_url:
        storage_uri = redis_url
    
    # Límites por defecto
    default_limits = [
        os.getenv('RATE_LIMIT_DEFAULT', '100 per minute'),
    ]
    
    # Crear limiter
    _limiter_instance = Limiter(
        app=app,
        key_func=get_client_ip,
        default_limits=default_limits,
        storage_uri=storage_uri,
        strategy='fixed-window',
        headers_enabled=True,  # Agregar headers X-RateLimit-*
    )
    
    # Manejador de errores personalizado
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'success': False,
            'error': 'rate_limit_exceeded',
            'message': 'Has excedido el límite de solicitudes. Intenta de nuevo más tarde.',
            'retry_after': e.description
        }), 429
    
    app.logger.info(
        f"Rate limiting inicializado. "
        f"Storage: {storage_uri.split('://')[0]}, "
        f"Default: {default_limits[0]}"
    )
    
    return _limiter_instance


def get_limiter() -> Optional[Any]:
    """
    Get the global rate limiter instance.
    
    Returns:
        Limiter instance or None
    """
    return _limiter_instance


class RateLimits:
    """
    Predefined rate limits for different endpoint types.
    
    Usage:
        @limiter.limit(RateLimits.AUTH)
        def login():
            pass
    """
    
    # Autenticación (prevenir fuerza bruta)
    AUTH = os.getenv('RATE_LIMIT_AUTH', '5 per minute')
    
    # Registro de usuarios
    REGISTER = os.getenv('RATE_LIMIT_REGISTER', '3 per minute')
    
    # Operaciones de lectura
    READ = os.getenv('RATE_LIMIT_READ', '100 per minute')
    
    # Operaciones de escritura
    WRITE = os.getenv('RATE_LIMIT_WRITE', '30 per minute')
    
    # Búsquedas
    SEARCH = os.getenv('RATE_LIMIT_SEARCH', '20 per minute')
    
    # Reportes (operaciones costosas)
    REPORTS = os.getenv('RATE_LIMIT_REPORTS', '10 per minute')
    
    # APIs públicas
    PUBLIC = os.getenv('RATE_LIMIT_PUBLIC', '60 per minute')
    
    # APIs administrativas
    ADMIN = os.getenv('RATE_LIMIT_ADMIN', '200 per minute')


def exempt_from_rate_limit(f):
    """
    Decorator to exempt a route from rate limiting.
    
    Usage:
        @app.route('/health')
        @exempt_from_rate_limit
        def health_check():
            return {'status': 'ok'}
    """
    limiter = get_limiter()
    if limiter is not None:
        return limiter.exempt(f)
    return f


def limit_by_user(limit_string: str):
    """
    Decorator to apply rate limit based on authenticated user.
    
    Args:
        limit_string: Rate limit string (e.g., '100 per minute')
        
    Usage:
        @app.route('/api/data')
        @limit_by_user('50 per minute')
        def get_data():
            pass
    """
    def decorator(f):
        limiter = get_limiter()
        if limiter is not None:
            def get_user_key():
                # Intentar obtener user_id del JWT
                from flask import g
                user_id = getattr(g, 'current_user', {}).get('user_id')
                if user_id:
                    return f"user:{user_id}"
                return get_client_ip()
            
            return limiter.limit(limit_string, key_func=get_user_key)(f)
        return f
    return decorator


# Ejemplo de uso:
# from common.rate_limiting import init_rate_limiter, RateLimits, exempt_from_rate_limit
#
# # En app.py
# limiter = init_rate_limiter(app)
#
# # En routes.py
# @app.route('/api/auth/login')
# @limiter.limit(RateLimits.AUTH)
# def login():
#     pass
#
# @app.route('/health')
# @exempt_from_rate_limit
# def health():
#     return {'status': 'ok'}
