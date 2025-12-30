# Facturación Service Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-base.txt /app/requirements-base.txt

COPY facturacion_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy common utilities
COPY common/ /app/common/

# Copy service code
COPY facturacion_service/ /app/

# Create non-root user and storage directory
RUN useradd -m -u 1000 appuser && \
    mkdir -p /storage/xml_facturas && \
    chown -R appuser:appuser /app /storage
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
