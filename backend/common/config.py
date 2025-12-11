"""
Configuration management for different environments
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    # Application
    APP_NAME = "Sistema de Gestión Clínica"
    VERSION = "1.1.0"

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', 20))
    DB_CONNECT_TIMEOUT = int(os.getenv('DB_CONNECT_TIMEOUT', 10))

    # Security
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', 24))
    JWT_ALGORITHM = 'HS256'

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True') == 'True'
    RATE_LIMIT_DEFAULT = int(os.getenv('RATE_LIMIT_DEFAULT', 100))  # requests per minute
    RATE_LIMIT_AUTH = int(os.getenv('RATE_LIMIT_AUTH', 5))  # login attempts per minute

    # Caching
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True') == 'True'
    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', 300))  # 5 minutes

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Service Ports
    AUTH_SERVICE_PORT = int(os.getenv('AUTH_SERVICE_PORT', 5001))
    INVENTARIO_SERVICE_PORT = int(os.getenv('INVENTARIO_SERVICE_PORT', 5002))
    HISTORIA_CLINICA_SERVICE_PORT = int(os.getenv('HISTORIA_CLINICA_SERVICE_PORT', 5003))
    FACTURACION_SERVICE_PORT = int(os.getenv('FACTURACION_SERVICE_PORT', 5004))
    CITAS_SERVICE_PORT = int(os.getenv('CITAS_SERVICE_PORT', 5005))
    LOGS_SERVICE_PORT = int(os.getenv('LOGS_SERVICE_PORT', 5006))

    # Service URLs
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5001/api/auth')
    INVENTARIO_SERVICE_URL = os.getenv('INVENTARIO_SERVICE_URL', 'http://localhost:5002/api/inventario')
    HISTORIA_CLINICA_SERVICE_URL = os.getenv('HISTORIA_CLINICA_SERVICE_URL', 'http://localhost:5003/api/historia-clinica')
    FACTURACION_SERVICE_URL = os.getenv('FACTURACION_SERVICE_URL', 'http://localhost:5004/api/facturacion')
    CITAS_SERVICE_URL = os.getenv('CITAS_SERVICE_URL', 'http://localhost:5005/api/citas')
    LOGS_SERVICE_URL = os.getenv('LOGS_SERVICE_URL', 'http://localhost:5006/api/logs')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_TO_CONSOLE = os.getenv('LOG_TO_CONSOLE', 'True') == 'True'
    LOG_TO_FILE = os.getenv('LOG_TO_FILE', 'False') == 'True'
    LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', 90))

    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', 20))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', 100))

    # File Upload (for future use)
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}


class DevelopmentConfig(Config):
    """Development environment configuration"""

    DEBUG = True
    TESTING = False
    FLASK_ENV = 'development'
    FLASK_DEBUG = True

    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    LOG_TO_CONSOLE = True

    # Relaxed rate limiting for development
    RATE_LIMIT_DEFAULT = 1000
    RATE_LIMIT_AUTH = 100

    # Shorter cache TTL for development
    CACHE_DEFAULT_TTL = 60


class ProductionConfig(Config):
    """Production environment configuration"""

    DEBUG = False
    TESTING = False
    FLASK_ENV = 'production'
    FLASK_DEBUG = False

    # Stricter settings for production
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', 5))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', 50))

    # Production rate limiting
    RATE_LIMIT_DEFAULT = 60
    RATE_LIMIT_AUTH = 5

    # Logging to file in production
    LOG_TO_FILE = True
    LOG_TO_CONSOLE = False

    # Ensure security settings are strict
    JWT_EXPIRATION_HOURS = 12  # Shorter token lifetime in production


class TestingConfig(Config):
    """Testing environment configuration"""

    DEBUG = True
    TESTING = True
    FLASK_ENV = 'testing'

    # Use test database
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', Config.DATABASE_URL)

    # Disable rate limiting for tests
    RATE_LIMIT_ENABLED = False

    # Disable caching for tests
    CACHE_ENABLED = False


class StagingConfig(Config):
    """Staging environment configuration"""

    DEBUG = False
    TESTING = False
    FLASK_ENV = 'staging'

    # Similar to production but with some relaxed settings
    RATE_LIMIT_DEFAULT = 100
    LOG_LEVEL = 'DEBUG'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration for specified environment

    Args:
        env: Environment name (development, production, testing, staging)

    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')

    return config.get(env, config['default'])


# Current configuration
current_config = get_config()
