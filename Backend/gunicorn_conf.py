"""
Gunicorn Configuration File
Sistema Médico Integral - Sprint 5-6
"""
import os
import multiprocessing

# Binding
bind = "0.0.0.0:5000"

# Workers
# Fórmula recomendada: (2 x CPUs) + 1
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
threads = int(os.getenv('GUNICORN_THREADS', 2))

# Timeout
timeout = int(os.getenv('GUNICORN_TIMEOUT', 120))

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()

# Worker Class
# Usar 'gthread' para Flask estándar (bloqueante pero thread-safe)
# Usar 'uvicorn.workers.UvicornWorker' si se migra a async o se usa FastAPI
worker_class = "gthread"

# Reload en desarrollo
reload = os.getenv('FLASK_ENV') == 'development'

# Métricas (si se usa statsd)
# statsad_host = "localhost:8125"

# Hooks
def on_starting(server):
    print(f"Iniciando servidor Gunicorn con {workers} workers de tipo {worker_class}")
