"""
Common utility functions
"""
from datetime import datetime, timedelta
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_cedula(cedula):
    """Validate Ecuadorian cedula format (10 digits)"""
    if not cedula or len(cedula) != 10:
        return False
    return cedula.isdigit()

def validate_ruc(ruc):
    """Validate Ecuadorian RUC format (13 digits)"""
    if not ruc or len(ruc) != 13:
        return False
    return ruc.isdigit()

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def calculate_iva(subtotal, iva_rate=15.0):
    """Calculate IVA amount"""
    return round(subtotal * (iva_rate / 100), 2)

def get_pagination_params(request):
    """Extract pagination parameters from request"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Limit per_page to avoid abuse
    per_page = min(per_page, 100)

    offset = (page - 1) * per_page

    return {
        'page': page,
        'per_page': per_page,
        'offset': offset
    }

def success_response(data=None, message=None, status_code=200):
    """Standard success response"""
    response = {
        'success': True
    }
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return response, status_code

def error_response(message, status_code=400, errors=None):
    """Standard error response"""
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    return response, status_code
