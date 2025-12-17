"""
Routes for Authentication Service
"""
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required, role_required
from common.utils import validate_email, success_response, error_response
from common.config import Config
from auth_service.models import UserModel, RoleModel

auth_bp = Blueprint('auth', __name__)

# Usar configuración centralizada
JWT_SECRET_KEY = Config.JWT_SECRET_KEY
JWT_EXPIRATION_HOURS = Config.JWT_EXPIRATION_HOURS
JWT_ALGORITHM = Config.JWT_ALGORITHM
JWT_ISSUER = Config.JWT_ISSUER
JWT_AUDIENCE = Config.JWT_AUDIENCE
BCRYPT_LOG_ROUNDS = Config.BCRYPT_LOG_ROUNDS


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    try:
        data = request.get_json()

        # Validate input
        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return error_response('Email and password are required', 400)

        if not validate_email(email):
            return error_response('Invalid email format', 400)

        # Get user from database
        user = UserModel.get_by_email(email)

        if not user:
            return error_response('Invalid credentials', 401)

        # Check if user is active
        if not user['is_active']:
            return error_response('User account is disabled', 403)

        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return error_response('Invalid credentials', 401)

        # Generate JWT token
        token_payload = {
            'user_id': user['user_id'],
            'role_id': user['role_id'],
            'email': user['email'],
            'iss': JWT_ISSUER,
            'aud': JWT_AUDIENCE,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }

        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Prepare response
        response_data = {
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'role_id': user['role_id'],
                'role_name': user['role_name'],
                'menu_config': user['menu_config']
            }
        }

        return success_response(response_data, 'Login successful')

    except Exception as e:
        print(f"Login error: {str(e)}")
        return error_response('An error occurred during login', 500)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user endpoint"""
    try:
        data = request.get_json()

        # Validate input
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        role_id = data.get('role_id', 2)  # Default role (e.g., Recepcion)

        if not email or not password or not full_name:
            return error_response('Email, password and full name are required', 400)

        if not validate_email(email):
            return error_response('Invalid email format', 400)

        if len(password) < 6:
            return error_response('Password must be at least 6 characters', 400)

        # Check if user already exists
        existing_user = UserModel.get_by_email(email)
        if existing_user:
            return error_response('User with this email already exists', 409)

        # Hash password with configurable work factor
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt(rounds=BCRYPT_LOG_ROUNDS)
        ).decode('utf-8')

        # Create user
        user = UserModel.create(role_id, full_name, email, password_hash)

        # Get role info
        role = RoleModel.get_by_id(role_id)

        # Generate JWT token
        token_payload = {
            'user_id': user['user_id'],
            'role_id': user['role_id'],
            'email': user['email'],
            'iss': JWT_ISSUER,
            'aud': JWT_AUDIENCE,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
        }

        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # Prepare response
        response_data = {
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'role_id': user['role_id'],
                'role_name': role['name'] if role else None,
                'is_active': user['is_active']
            }
        }

        return success_response(response_data, 'User registered successfully', 201)

    except Exception as e:
        print(f"Register error: {str(e)}")
        return error_response('An error occurred during registration', 500)


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    try:
        user = UserModel.get_by_id(current_user['user_id'])

        if not user:
            return error_response('User not found', 404)

        response_data = {
            'user_id': user['user_id'],
            'full_name': user['full_name'],
            'email': user['email'],
            'role_id': user['role_id'],
            'role_name': user['role_name'],
            'menu_config': user['menu_config'],
            'is_active': user['is_active']
        }

        return success_response(response_data)

    except Exception as e:
        print(f"Get current user error: {str(e)}")
        return error_response('An error occurred', 500)


@auth_bp.route('/users', methods=['GET'])
@token_required
def list_users(current_user):
    """List all users (admin only)"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        per_page = min(per_page, 100)  # Max 100 per page

        offset = (page - 1) * per_page

        # Get users
        users = UserModel.list_users(limit=per_page, offset=offset)
        total = UserModel.count_users()

        response_data = {
            'users': users,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List users error: {str(e)}")
        return error_response('An error occurred', 500)


@auth_bp.route('/roles', methods=['GET'])
@token_required
def list_roles(current_user):
    """List all roles"""
    try:
        roles = RoleModel.list_roles()
        return success_response({'roles': roles})

    except Exception as e:
        print(f"List roles error: {str(e)}")
        return error_response('An error occurred', 500)


@auth_bp.route('/roles', methods=['POST'])
@token_required
def create_role(current_user):
    """Create a new role (admin only)"""
    try:
        data = request.get_json()

        name = data.get('name', '').strip()
        menu_config = data.get('menu_config', {})

        if not name:
            return error_response('Role name is required', 400)

        # Check if role already exists
        existing_role = RoleModel.get_by_name(name)
        if existing_role:
            return error_response('Role with this name already exists', 409)

        # Create role
        role = RoleModel.create(name, menu_config)

        return success_response({'role': role}, 'Role created successfully', 201)

    except Exception as e:
        print(f"Create role error: {str(e)}")
        return error_response('An error occurred', 500)


@auth_bp.route('/roles/<int:role_id>', methods=['PUT'])
@token_required
def update_role(current_user, role_id):
    """Update a role (admin only)"""
    try:
        data = request.get_json()

        name = data.get('name')
        menu_config = data.get('menu_config')

        if not name and not menu_config:
            return error_response('No data to update', 400)

        # Update role
        role = RoleModel.update(role_id, name, menu_config)

        if not role:
            return error_response('Role not found', 404)

        return success_response({'role': role}, 'Role updated successfully')

    except Exception as e:
        print(f"Update role error: {str(e)}")
        return error_response('An error occurred', 500)


@auth_bp.route('/validate', methods=['GET'])
@token_required
def validate_token(current_user):
    """Validate JWT token"""
    return success_response({'valid': True, 'user': current_user})


# Health check
@auth_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'auth'})
