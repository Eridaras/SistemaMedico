"""
Models for Authentication Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db

class UserModel:
    """User database operations"""

    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.role_id, u.full_name, u.email,
                       u.password_hash, u.is_active, u.created_at,
                       r.name as role_name, r.menu_config
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
                WHERE u.email = %s
            """, (email,))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.role_id, u.full_name, u.email,
                       u.is_active, u.created_at,
                       r.name as role_name, r.menu_config
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
                WHERE u.user_id = %s
            """, (user_id,))
            return cursor.fetchone()

    @staticmethod
    def create(role_id, full_name, email, password_hash):
        """Create a new user"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO users (role_id, full_name, email, password_hash)
                VALUES (%s, %s, %s, %s)
                RETURNING user_id, role_id, full_name, email, is_active, created_at
            """, (role_id, full_name, email, password_hash))
            return cursor.fetchone()

    @staticmethod
    def update_password(user_id, password_hash):
        """Update user password"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE users
                SET password_hash = %s
                WHERE user_id = %s
                RETURNING user_id
            """, (password_hash, user_id))
            return cursor.fetchone()

    @staticmethod
    def list_users(limit=20, offset=0):
        """List all users with pagination"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.role_id, u.full_name, u.email,
                       u.is_active, u.created_at,
                       r.name as role_name
                FROM users u
                LEFT JOIN roles r ON u.role_id = r.role_id
                ORDER BY u.created_at DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            return cursor.fetchall()

    @staticmethod
    def count_users():
        """Count total users"""
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM users")
            result = cursor.fetchone()
            return result['count'] if result else 0


class RoleModel:
    """Role database operations"""

    @staticmethod
    def get_by_id(role_id):
        """Get role by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT role_id, name, menu_config, created_at
                FROM roles
                WHERE role_id = %s
            """, (role_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_name(name):
        """Get role by name"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT role_id, name, menu_config, created_at
                FROM roles
                WHERE name = %s
            """, (name,))
            return cursor.fetchone()

    @staticmethod
    def list_roles():
        """List all roles"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT role_id, name, menu_config, created_at
                FROM roles
                ORDER BY name
            """)
            return cursor.fetchall()

    @staticmethod
    def create(name, menu_config):
        """Create a new role"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO roles (name, menu_config)
                VALUES (%s, %s)
                RETURNING role_id, name, menu_config, created_at
            """, (name, menu_config))
            return cursor.fetchone()

    @staticmethod
    def update(role_id, name=None, menu_config=None):
        """Update role"""
        updates = []
        params = []

        if name is not None:
            updates.append("name = %s")
            params.append(name)

        if menu_config is not None:
            updates.append("menu_config = %s")
            params.append(menu_config)

        if not updates:
            return None

        params.append(role_id)
        query = f"""
            UPDATE roles
            SET {', '.join(updates)}
            WHERE role_id = %s
            RETURNING role_id, name, menu_config, created_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
