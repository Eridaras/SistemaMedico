"""
Security utilities and middleware for all services
"""
from functools import wraps
from flask import request, jsonify
import time
import hashlib
import re
from datetime import datetime, timedelta

# In-memory rate limiting storage (use Redis in production)
rate_limit_storage = {}

def clean_rate_limit_storage():
    """Clean old entries from rate limiting storage"""
    current_time = time.time()
    keys_to_delete = []

    for key, data in rate_limit_storage.items():
        if current_time - data['window_start'] > 60:  # 1 minute window
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del rate_limit_storage[key]

def rate_limit(max_requests=100, window=60):
    """
    Rate limiting decorator

    Args:
        max_requests: Maximum number of requests allowed
        window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            identifier = request.remote_addr
            if request.headers.get('Authorization'):
                # Use token hash for authenticated requests
                token = request.headers.get('Authorization')
                identifier = hashlib.md5(token.encode()).hexdigest()

            current_time = time.time()
            key = f"{f.__name__}:{identifier}"

            # Clean old entries periodically
            if len(rate_limit_storage) > 1000:
                clean_rate_limit_storage()

            # Check rate limit
            if key in rate_limit_storage:
                data = rate_limit_storage[key]

                # Reset window if expired
                if current_time - data['window_start'] > window:
                    rate_limit_storage[key] = {
                        'count': 1,
                        'window_start': current_time
                    }
                else:
                    # Check if limit exceeded
                    if data['count'] >= max_requests:
                        retry_after = int(window - (current_time - data['window_start']))
                        return jsonify({
                            'success': False,
                            'message': 'Rate limit exceeded. Try again later.',
                            'retry_after': retry_after
                        }), 429

                    # Increment counter
                    data['count'] += 1
            else:
                # First request
                rate_limit_storage[key] = {
                    'count': 1,
                    'window_start': current_time
                }

            return f(*args, **kwargs)

        return decorated_function
    return decorator


def sanitize_string(value, max_length=255):
    """
    Sanitize string input to prevent XSS and injection attacks

    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    """
    if not value:
        return value

    # Convert to string
    value = str(value)

    # Truncate to max length
    value = value[:max_length]

    # Remove potentially dangerous characters
    # Keep only alphanumeric, spaces, and safe punctuation
    value = re.sub(r'[^\w\s\-@.,:;áéíóúñÁÉÍÓÚÑ]', '', value)

    # Remove leading/trailing whitespace
    value = value.strip()

    return value


def sanitize_email(email):
    """Validate and sanitize email"""
    if not email:
        return None

    email = str(email).strip().lower()

    # Basic email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return None

    # Truncate to reasonable length
    return email[:255]


def sanitize_sql_identifier(identifier):
    """
    Sanitize SQL identifiers (table/column names)
    Only allow alphanumeric and underscore
    """
    if not identifier:
        return identifier

    # Only allow letters, numbers, and underscores
    return re.sub(r'[^\w]', '', str(identifier))


def validate_uuid(uuid_string):
    """Validate UUID format"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, str(uuid_string).lower()))


def validate_date(date_string):
    """Validate ISO date format (YYYY-MM-DD)"""
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, str(date_string)):
        return False

    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_datetime(datetime_string):
    """Validate ISO datetime format"""
    try:
        datetime.fromisoformat(datetime_string.replace('Z', '+00:00'))
        return True
    except (ValueError, AttributeError):
        return False


def validate_phone(phone):
    """Validate phone number (Ecuador format)"""
    if not phone:
        return False

    # Remove spaces and dashes
    phone = re.sub(r'[\s\-]', '', str(phone))

    # Ecuador phone: 10 digits starting with 0
    pattern = r'^0[0-9]{9}$'
    return bool(re.match(pattern, phone))


def validate_cedula(cedula):
    """
    Validate Ecuadorian cedula (10 digits with check digit)
    """
    if not cedula or len(cedula) != 10:
        return False

    if not cedula.isdigit():
        return False

    # Province code (first 2 digits) must be valid
    province = int(cedula[:2])
    if province < 1 or province > 24:
        return False

    # Calculate check digit
    coefficients = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0

    for i in range(9):
        value = int(cedula[i]) * coefficients[i]
        if value > 9:
            value -= 9
        total += value

    check_digit = (10 - (total % 10)) % 10

    return check_digit == int(cedula[9])


def validate_ruc(ruc):
    """Validate Ecuadorian RUC (13 digits)"""
    if not ruc or len(ruc) != 13:
        return False

    if not ruc.isdigit():
        return False

    # RUC types:
    # 1. Natural person: cedula + 001
    # 2. Private company: special validation
    # 3. Public company: special validation

    # For simplicity, validate basic format
    province = int(ruc[:2])
    if province < 1 or province > 24:
        return False

    third_digit = int(ruc[2])

    # Natural person RUC
    if third_digit < 6:
        # Should end with 001
        if not ruc.endswith('001'):
            return False
        # Validate cedula part
        return validate_cedula(ruc[:10])

    # Company RUC (basic validation)
    return True


def prevent_sql_injection(value):
    """
    Check for common SQL injection patterns
    Returns True if suspicious, False if safe
    """
    if not value:
        return False

    value = str(value).lower()

    # Common SQL injection patterns
    dangerous_patterns = [
        r'(\b(select|insert|update|delete|drop|create|alter|exec|execute|union|declare)\b)',
        r'(--|#|/\*|\*/)',
        r"('[^']*'|\"[^\"]*\")",
        r';.*',
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return True

    return False


def validate_pagination(page, per_page, max_per_page=100):
    """Validate pagination parameters"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 20

        # Ensure positive values
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))

        return page, per_page
    except (ValueError, TypeError):
        return 1, 20


class InputValidator:
    """Centralized input validation"""

    @staticmethod
    def validate_user_input(data):
        """Validate user creation/update input"""
        errors = []

        if 'email' in data:
            email = sanitize_email(data['email'])
            if not email:
                errors.append('Invalid email format')
            data['email'] = email

        if 'full_name' in data:
            name = sanitize_string(data['full_name'], 100)
            if not name or len(name) < 3:
                errors.append('Full name must be at least 3 characters')
            data['full_name'] = name

        if 'password' in data:
            password = data['password']
            if len(password) < 8:
                errors.append('Password must be at least 8 characters')
            if not re.search(r'[A-Z]', password):
                errors.append('Password must contain at least one uppercase letter')
            if not re.search(r'[a-z]', password):
                errors.append('Password must contain at least one lowercase letter')
            if not re.search(r'[0-9]', password):
                errors.append('Password must contain at least one number')

        return errors, data

    @staticmethod
    def validate_patient_input(data):
        """Validate patient creation/update input"""
        errors = []

        if 'doc_number' in data:
            doc_type = data.get('doc_type', 'CEDULA')
            doc_number = str(data['doc_number']).strip()

            if doc_type == 'CEDULA':
                if not validate_cedula(doc_number):
                    errors.append('Invalid cedula number')
            elif doc_type == 'RUC':
                if not validate_ruc(doc_number):
                    errors.append('Invalid RUC number')

            data['doc_number'] = doc_number

        if 'email' in data and data['email']:
            email = sanitize_email(data['email'])
            if email is None:
                errors.append('Invalid email format')
            data['email'] = email

        if 'phone' in data and data['phone']:
            if not validate_phone(data['phone']):
                errors.append('Invalid phone number format')

        for field in ['first_name', 'last_name']:
            if field in data:
                value = sanitize_string(data[field], 100)
                if not value or len(value) < 2:
                    errors.append(f'{field} must be at least 2 characters')
                data[field] = value

        return errors, data


def secure_headers():
    """Add security headers to response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            response = f(*args, **kwargs)

            # Add security headers
            if hasattr(response, 'headers'):
                response.headers['X-Content-Type-Options'] = 'nosniff'
                response.headers['X-Frame-Options'] = 'DENY'
                response.headers['X-XSS-Protection'] = '1; mode=block'
                response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
                response.headers['Content-Security-Policy'] = "default-src 'self'"

            return response

        return decorated_function
    return decorator
