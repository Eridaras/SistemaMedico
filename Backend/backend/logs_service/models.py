"""
Models for Logs Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db

class LogModel:
    """Log database operations"""

    @staticmethod
    def create(service_name, action, user_id=None, details=None, level='INFO', ip_address=None):
        """Create a new log entry"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO system_logs
                (service_name, action, user_id, details, level, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING log_id, service_name, action, user_id, details,
                          level, ip_address, created_at
            """, (service_name, action, user_id, details, level, ip_address))
            return cursor.fetchone()

    @staticmethod
    def get_by_id(log_id):
        """Get log by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT l.log_id, l.service_name, l.action, l.user_id,
                       l.details, l.level, l.ip_address, l.created_at,
                       u.full_name as user_name, u.email as user_email
                FROM system_logs l
                LEFT JOIN users u ON l.user_id = u.user_id
                WHERE l.log_id = %s
            """, (log_id,))
            return cursor.fetchone()

    @staticmethod
    def list_logs(service_name=None, level=None, user_id=None,
                  start_date=None, end_date=None, limit=100, offset=0):
        """List logs with filters"""
        conditions = []
        params = []

        if service_name:
            conditions.append("l.service_name = %s")
            params.append(service_name)

        if level:
            conditions.append("l.level = %s")
            params.append(level)

        if user_id:
            conditions.append("l.user_id = %s")
            params.append(user_id)

        if start_date:
            conditions.append("l.created_at >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("l.created_at <= %s")
            params.append(end_date)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT l.log_id, l.service_name, l.action, l.user_id,
                       l.details, l.level, l.ip_address, l.created_at,
                       u.full_name as user_name, u.email as user_email
                FROM system_logs l
                LEFT JOIN users u ON l.user_id = u.user_id
                {where_clause}
                ORDER BY l.created_at DESC
                LIMIT %s OFFSET %s
            """, params)
            return cursor.fetchall()

    @staticmethod
    def count_logs(service_name=None, level=None, user_id=None,
                   start_date=None, end_date=None):
        """Count logs with filters"""
        conditions = []
        params = []

        if service_name:
            conditions.append("service_name = %s")
            params.append(service_name)

        if level:
            conditions.append("level = %s")
            params.append(level)

        if user_id:
            conditions.append("user_id = %s")
            params.append(user_id)

        if start_date:
            conditions.append("created_at >= %s")
            params.append(start_date)

        if end_date:
            conditions.append("created_at <= %s")
            params.append(end_date)

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        with db.get_cursor() as cursor:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM system_logs
                {where_clause}
            """, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def get_stats():
        """Get log statistics"""
        with db.get_cursor() as cursor:
            # Total logs
            cursor.execute("SELECT COUNT(*) as total FROM system_logs")
            total = cursor.fetchone()['total']

            # Logs by service
            cursor.execute("""
                SELECT service_name, COUNT(*) as count
                FROM system_logs
                GROUP BY service_name
                ORDER BY count DESC
            """)
            by_service = cursor.fetchall()

            # Logs by level
            cursor.execute("""
                SELECT level, COUNT(*) as count
                FROM system_logs
                GROUP BY level
                ORDER BY count DESC
            """)
            by_level = cursor.fetchall()

            # Recent errors
            cursor.execute("""
                SELECT log_id, service_name, action, details, created_at
                FROM system_logs
                WHERE level IN ('ERROR', 'CRITICAL')
                ORDER BY created_at DESC
                LIMIT 10
            """)
            recent_errors = cursor.fetchall()

            return {
                'total': total,
                'by_service': by_service,
                'by_level': by_level,
                'recent_errors': recent_errors
            }

    @staticmethod
    def delete_old_logs(days=90):
        """Delete logs older than specified days"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM system_logs
                WHERE created_at < NOW() - INTERVAL '%s days'
                RETURNING log_id
            """, (days,))
            deleted = cursor.fetchall()
            return len(deleted)
