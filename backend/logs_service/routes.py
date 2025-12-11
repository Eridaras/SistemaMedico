"""
Routes for Logs Service
"""
from flask import Blueprint, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response, get_pagination_params
from logs_service.models import LogModel

logs_bp = Blueprint('logs', __name__)


@logs_bp.route('/logs', methods=['POST'])
def create_log():
    """Create a new log entry (can be called without authentication for system logs)"""
    try:
        data = request.get_json()

        # Validate required fields
        service_name = data.get('service_name', '').strip()
        action = data.get('action', '').strip()

        if not service_name or not action:
            return error_response('service_name and action are required', 400)

        # Optional fields
        user_id = data.get('user_id')
        details = data.get('details')
        level = data.get('level', 'INFO')
        ip_address = data.get('ip_address') or request.remote_addr

        # Validate level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level not in valid_levels:
            return error_response(f'Invalid level. Must be one of: {", ".join(valid_levels)}', 400)

        # Create log
        log = LogModel.create(
            service_name=service_name,
            action=action,
            user_id=user_id,
            details=details,
            level=level,
            ip_address=ip_address
        )

        return success_response({'log': log}, 'Log created successfully', 201)

    except Exception as e:
        print(f"Create log error: {str(e)}")
        return error_response('An error occurred while creating log', 500)


@logs_bp.route('/logs', methods=['GET'])
@token_required
def list_logs(current_user):
    """List logs with filters"""
    try:
        # Get pagination parameters
        pagination = get_pagination_params(request)

        # Get filter parameters
        service_name = request.args.get('service_name')
        level = request.args.get('level')
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Get logs
        logs = LogModel.list_logs(
            service_name=service_name,
            level=level,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=pagination['per_page'],
            offset=pagination['offset']
        )

        # Get total count
        total = LogModel.count_logs(
            service_name=service_name,
            level=level,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )

        response_data = {
            'logs': logs,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List logs error: {str(e)}")
        return error_response('An error occurred', 500)


@logs_bp.route('/logs/<int:log_id>', methods=['GET'])
@token_required
def get_log(current_user, log_id):
    """Get a specific log entry"""
    try:
        log = LogModel.get_by_id(log_id)

        if not log:
            return error_response('Log not found', 404)

        return success_response({'log': log})

    except Exception as e:
        print(f"Get log error: {str(e)}")
        return error_response('An error occurred', 500)


@logs_bp.route('/logs/stats', methods=['GET'])
@token_required
def get_stats(current_user):
    """Get log statistics"""
    try:
        stats = LogModel.get_stats()
        return success_response({'stats': stats})

    except Exception as e:
        print(f"Get stats error: {str(e)}")
        return error_response('An error occurred', 500)


@logs_bp.route('/logs/cleanup', methods=['POST'])
@token_required
def cleanup_logs(current_user):
    """Delete old logs (admin only)"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 90)

        if days < 30:
            return error_response('Cannot delete logs newer than 30 days', 400)

        deleted_count = LogModel.delete_old_logs(days)

        return success_response(
            {'deleted_count': deleted_count},
            f'Deleted {deleted_count} logs older than {days} days'
        )

    except Exception as e:
        print(f"Cleanup logs error: {str(e)}")
        return error_response('An error occurred', 500)


@logs_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'logs'})
