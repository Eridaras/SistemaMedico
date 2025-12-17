"""
HTTP Response Compression Middleware
Sistema Médico Integral - Sprint 4
"""
import os
from flask import Flask

# Importación condicional
try:
    from flask_compress import Compress
    COMPRESS_AVAILABLE = True
except ImportError:
    COMPRESS_AVAILABLE = False
    Compress = None


def init_compression(app: Flask) -> None:
    """
    Initialize response compression for Flask application.
    
    Compress uses gzip, brotli, or deflate to compress HTTP responses,
    reducing bandwidth usage and improving load times.
    
    Args:
        app: Flask application instance
    """
    if not COMPRESS_AVAILABLE:
        app.logger.warning(
            "flask-compress no está instalado. "
            "La compresión de respuestas no estará disponible. "
            "Ejecute: pip install flask-compress"
        )
        return
    
    compression_enabled = os.getenv('COMPRESSION_ENABLED', 'true').lower() == 'true'
    if not compression_enabled:
        app.logger.info("Compresión deshabilitada por configuración")
        return
    
    # Configuración de compresión
    app.config['COMPRESS_MIMETYPES'] = [
        'text/html',
        'text/css',
        'text/xml',
        'text/plain',
        'application/json',
        'application/javascript',
        'application/xml',
        'application/xhtml+xml',
    ]
    
    # Tamaño mínimo para comprimir (bytes)
    app.config['COMPRESS_MIN_SIZE'] = int(os.getenv('COMPRESS_MIN_SIZE', 500))
    
    # Nivel de compresión (1-9, mayor = más compresión pero más CPU)
    app.config['COMPRESS_LEVEL'] = int(os.getenv('COMPRESS_LEVEL', 6))
    
    # Algoritmo preferido
    app.config['COMPRESS_ALGORITHM'] = os.getenv('COMPRESS_ALGORITHM', 'gzip')
    
    # Registrar encoding BR (Brotli) si está disponible
    app.config['COMPRESS_BR_LEVEL'] = 4
    app.config['COMPRESS_BR_MODE'] = 0
    app.config['COMPRESS_BR_WINDOW'] = 22
    app.config['COMPRESS_BR_BLOCK'] = 0
    
    # Inicializar Compress
    Compress(app)
    
    app.logger.info(
        f"Compresión HTTP inicializada. "
        f"Algoritmo: {app.config['COMPRESS_ALGORITHM']}, "
        f"Nivel: {app.config['COMPRESS_LEVEL']}, "
        f"Min size: {app.config['COMPRESS_MIN_SIZE']} bytes"
    )


def get_compression_stats(response_size: int, compressed_size: int) -> dict:
    """
    Calculate compression statistics.
    
    Args:
        response_size: Original response size in bytes
        compressed_size: Compressed response size in bytes
        
    Returns:
        dict: Compression statistics
    """
    if response_size == 0:
        return {
            'original_size': 0,
            'compressed_size': 0,
            'savings': 0,
            'ratio': 1.0
        }
    
    savings = response_size - compressed_size
    ratio = compressed_size / response_size
    
    return {
        'original_size': response_size,
        'compressed_size': compressed_size,
        'savings': savings,
        'savings_percent': round((1 - ratio) * 100, 2),
        'ratio': round(ratio, 4)
    }
