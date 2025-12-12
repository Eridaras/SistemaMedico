"""
Centralized error handling for all services
"""
from flask import jsonify
from functools import wraps
import traceback
import sys

class AppError(Exception):
    """Base exception for application errors"""

    def __init__(self, message, status_code=400, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['success'] = False
        rv['message'] = self.message
        return rv


class ValidationError(AppError):
    """Validation error (400)"""

    def __init__(self, message, errors=None):
        super().__init__(message, status_code=400)
        if errors:
            self.payload = {'errors': errors}


class AuthenticationError(AppError):
    """Authentication error (401)"""

    def __init__(self, message='Authentication required'):
        super().__init__(message, status_code=401)


class AuthorizationError(AppError):
    """Authorization error (403)"""

    def __init__(self, message='Insufficient permissions'):
        super().__init__(message, status_code=403)


class NotFoundError(AppError):
    """Resource not found error (404)"""

    def __init__(self, message='Resource not found'):
        super().__init__(message, status_code=404)


class ConflictError(AppError):
    """Conflict error (409)"""

    def __init__(self, message='Resource already exists'):
        super().__init__(message, status_code=409)


class DatabaseError(AppError):
    """Database operation error (500)"""

    def __init__(self, message='Database operation failed'):
        super().__init__(message, status_code=500)


class ServiceUnavailableError(AppError):
    """Service unavailable error (503)"""

    def __init__(self, message='Service temporarily unavailable'):
        super().__init__(message, status_code=503)


def register_error_handlers(app):
    """Register error handlers for Flask app"""

    @app.errorhandler(AppError)
    def handle_app_error(error):
        """Handle custom application errors"""
        response = error.to_dict()

        # Log error
        from common.logger import logs_logger
        if hasattr(app, 'service_name'):
            logger = logs_logger
            logger.error(
                action=f"Application error: {error.message}",
                details=str(error.payload) if error.payload else None
            )

        return jsonify(response), error.status_code

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'error': str(error)
        }), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle unauthorized errors"""
        return jsonify({
            'success': False,
            'message': 'Unauthorized access'
        }), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle forbidden errors"""
        return jsonify({
            'success': False,
            'message': 'Forbidden - insufficient permissions'
        }), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle not found errors"""
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Handle rate limit errors"""
        return jsonify({
            'success': False,
            'message': 'Too many requests - rate limit exceeded'
        }), 429

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors"""
        # Log the error
        print(f"Internal Server Error: {error}", file=sys.stderr)
        traceback.print_exc()

        from common.logger import logs_logger
        if hasattr(app, 'service_name'):
            logger = logs_logger
            logger.critical(
                action=f"Internal server error in {app.service_name}",
                details=traceback.format_exc()
            )

        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

    @app.errorhandler(503)
    def handle_service_unavailable(error):
        """Handle service unavailable errors"""
        return jsonify({
            'success': False,
            'message': 'Service temporarily unavailable'
        }), 503


def handle_exceptions(f):
    """
    Decorator to handle exceptions in route handlers

    Usage:
        @app.route('/example')
        @handle_exceptions
        def example():
            # Your code here
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except AppError:
            # Re-raise app errors to be handled by error handler
            raise
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error in {f.__name__}: {e}", file=sys.stderr)
            traceback.print_exc()

            # Log to logs service
            from common.logger import logs_logger
            logs_logger.error(
                action=f"Unexpected error in {f.__name__}",
                details=f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            )

            # Return generic error response
            return jsonify({
                'success': False,
                'message': 'An unexpected error occurred'
            }), 500

    return decorated_function


def safe_db_operation(operation, error_message='Database operation failed'):
    """
    Safely execute a database operation with error handling

    Args:
        operation: Function to execute
        error_message: Custom error message

    Returns:
        Result of operation

    Raises:
        DatabaseError: If operation fails
    """
    try:
        return operation()
    except Exception as e:
        print(f"Database error: {e}", file=sys.stderr)
        traceback.print_exc()

        from common.logger import logs_logger
        logs_logger.error(
            action="Database operation failed",
            details=f"{error_message}: {str(e)}"
        )

        raise DatabaseError(error_message)


class ErrorResponse:
    """Helper class for creating error responses"""

    @staticmethod
    def validation_error(message, errors=None):
        """Create validation error response"""
        response = {
            'success': False,
            'message': message
        }
        if errors:
            response['errors'] = errors
        return jsonify(response), 400

    @staticmethod
    def unauthorized(message='Unauthorized access'):
        """Create unauthorized error response"""
        return jsonify({
            'success': False,
            'message': message
        }), 401

    @staticmethod
    def forbidden(message='Insufficient permissions'):
        """Create forbidden error response"""
        return jsonify({
            'success': False,
            'message': message
        }), 403

    @staticmethod
    def not_found(message='Resource not found'):
        """Create not found error response"""
        return jsonify({
            'success': False,
            'message': message
        }), 404

    @staticmethod
    def conflict(message='Resource already exists'):
        """Create conflict error response"""
        return jsonify({
            'success': False,
            'message': message
        }), 409

    @staticmethod
    def internal_error(message='Internal server error'):
        """Create internal error response"""
        return jsonify({
            'success': False,
            'message': message
        }), 500

    @staticmethod
    def service_unavailable(message='Service temporarily unavailable'):
        """Create service unavailable response"""
        return jsonify({
            'success': False,
            'message': message
        }), 503
