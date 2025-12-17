"""
Security headers middleware using Flask-Talisman
Sprint 2 - Sistema Médico Integral
"""
import os
from flask import Flask

# Importación condicional para permitir funcionamiento sin talisman
try:
    from flask_talisman import Talisman
    TALISMAN_AVAILABLE = True
except ImportError:
    TALISMAN_AVAILABLE = False
    Talisman = None


def configure_security_headers(app: Flask) -> None:
    """
    Configure security headers for Flask application using Talisman.
    
    Headers configurados:
    - Content-Security-Policy (CSP)
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security (HSTS)
    - Referrer-Policy
    
    Args:
        app: Flask application instance
    """
    if not TALISMAN_AVAILABLE:
        app.logger.warning(
            "flask-talisman no está instalado. "
            "Las cabeceras de seguridad no serán configuradas. "
            "Ejecute: pip install flask-talisman"
        )
        return
    
    # Determinar ambiente
    is_development = os.getenv('FLASK_ENV', 'development') == 'development'
    force_https = os.getenv('FORCE_HTTPS', 'true').lower() == 'true'
    
    # Content Security Policy
    # Ajustar según necesidades del frontend
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Necesario para Swagger UI
            "'unsafe-eval'",    # Necesario para algunas librerías
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Necesario para estilos inline
        ],
        'img-src': [
            "'self'",
            "data:",            # Para imágenes base64
            "https:",           # Para imágenes externas
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
        ],
        'connect-src': [
            "'self'",
            "https://api.example.com",  # Ajustar según APIs externas
        ],
        'frame-ancestors': "'none'",
        'form-action': "'self'",
        'base-uri': "'self'",
    }
    
    # Configuración de Talisman
    talisman_config = {
        # HTTPS
        'force_https': force_https and not is_development,
        'force_https_permanent': False,
        
        # HSTS (Strict Transport Security)
        'strict_transport_security': not is_development,
        'strict_transport_security_max_age': 31536000,  # 1 año
        'strict_transport_security_include_subdomains': True,
        'strict_transport_security_preload': False,  # Activar solo después de verificar
        
        # CSP
        'content_security_policy': csp if not is_development else None,
        'content_security_policy_report_only': is_development,
        'content_security_policy_report_uri': None,
        
        # Otras cabeceras de seguridad
        'referrer_policy': 'strict-origin-when-cross-origin',
        'session_cookie_secure': not is_development,
        'session_cookie_http_only': True,
        'session_cookie_samesite': 'Lax',
        
        # Frame options
        'frame_options': 'DENY',
        'frame_options_allow_from': None,
        
        # Permisos
        'permissions_policy': {
            'geolocation': '()',
            'microphone': '()',
            'camera': '()',
        },
    }
    
    # Aplicar Talisman
    Talisman(app, **talisman_config)
    
    app.logger.info(
        f"Cabeceras de seguridad configuradas. "
        f"Ambiente: {'desarrollo' if is_development else 'producción'}. "
        f"Force HTTPS: {talisman_config['force_https']}"
    )


def get_security_headers_report(app: Flask) -> dict:
    """
    Generate a report of current security headers configuration.
    
    Returns:
        dict: Report with security headers status
    """
    is_development = os.getenv('FLASK_ENV', 'development') == 'development'
    
    return {
        'talisman_available': TALISMAN_AVAILABLE,
        'environment': 'development' if is_development else 'production',
        'headers': {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Strict-Transport-Security': 'Enabled' if not is_development else 'Disabled (dev)',
            'Content-Security-Policy': 'Enabled' if not is_development else 'Report-Only (dev)',
        },
        'recommendations': [
            'Habilitar HSTS preload después de verificar compatibilidad',
            'Revisar CSP para ajustar a necesidades específicas del frontend',
            'Configurar Content-Security-Policy-Report-Uri para monitoreo',
        ]
    }
