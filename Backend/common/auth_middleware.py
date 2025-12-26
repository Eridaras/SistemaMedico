"""
Authentication middleware for protecting routes
"""
from functools import wraps
from flask import request, jsonify
import jwt
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.config import Config

# JWT Configuration from centralized config
JWT_ALGORITHM = Config.JWT_ALGORITHM
JWT_ISSUER = Config.JWT_ISSUER
JWT_AUDIENCE = Config.JWT_AUDIENCE

# Get appropriate key based on algorithm
if JWT_ALGORITHM == 'RS256':
    JWT_KEY = Config.JWT_PUBLIC_KEY
else:
    JWT_KEY = Config.JWT_SECRET_KEY

def token_required(f):
    """Decorator to protect routes that require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({'message': 'Token format invalid'}), 401

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            # Decode token with full validation using public key (RS256) or secret (HS256)
            data = jwt.decode(
                token,
                JWT_KEY,
                algorithms=[JWT_ALGORITHM],
                issuer=JWT_ISSUER,
                audience=JWT_AUDIENCE,
                options={
                    'require': ['exp', 'iat', 'iss', 'aud'],
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_iss': True,
                    'verify_aud': True
                }
            )
            current_user = {
                'user_id': data['user_id'],
                'role_id': data['role_id'],
                'email': data['email']
            }
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidIssuerError:
            return jsonify({'message': 'Token issuer invalid'}), 401
        except jwt.InvalidAudienceError:
            return jsonify({'message': 'Token audience invalid'}), 401
        except jwt.ImmatureSignatureError:
            return jsonify({'message': 'Token not yet valid'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def role_required(allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(f):
        @wraps(f)
        def decorated(current_user, *args, **kwargs):
            if current_user['role_id'] not in allowed_roles:
                return jsonify({'message': 'Insufficient permissions'}), 403
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

