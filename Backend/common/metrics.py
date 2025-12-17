"""
Prometheus Metrics Configuration
Sistema Médico Integral - Sprint 5-6
"""
import os
from flask import Flask, request

# Importación condicional
try:
    from prometheus_flask_exporter import PrometheusMetrics
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    PrometheusMetrics = None


def init_metrics(app: Flask) -> None:
    """
    Initialize Prometheus metrics for Flask application.
    
    Exposes /metrics endpoint for Prometheus scraping.
    
    Args:
        app: Flask application instance
    """
    if not METRICS_AVAILABLE:
        app.logger.warning(
            "prometheus-flask-exporter no está instalado. "
            "Las métricas no estarán disponibles. "
            "Ejecute: pip install prometheus-flask-exporter"
        )
        return
    
    metrics_enabled = os.getenv('METRICS_ENABLED', 'true').lower() == 'true'
    if not metrics_enabled:
        app.logger.info("Métricas deshabilitadas por configuración")
        return
    
    # Inicializar métricas
    # group_by='path' agrupa métricas por ruta de URL
    metrics = PrometheusMetrics(app, group_by='path', path='/metrics')
    
    # Info básica de la aplicación
    metrics.info('app_info', 'Application info', version='1.0.0')
    
    # Registrar métricas customizadas por defecto
    metrics.register_default(
        metrics.counter(
            'by_path_counter', 'Request count by request paths',
            labels={'path': lambda: request.path}
        )
    )
    
    app.logger.info("Métricas Prometheus inicializadas en /metrics")
