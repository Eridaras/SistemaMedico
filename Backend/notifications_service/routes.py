"""
Routes for Notifications Service
"""
from flask import Blueprint, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response
from common.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)


# ============= USER NOTIFICATIONS =============

@notifications_bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """Get notifications for current user"""
    try:
        limit = request.args.get('limit', 50, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'

        notifications = NotificationService.get_user_notifications(
            current_user['user_id'],
            limit=limit,
            unread_only=unread_only
        )

        # Count unread
        all_notifications = NotificationService.get_user_notifications(
            current_user['user_id'],
            limit=1000,
            unread_only=True
        )

        return success_response({
            'notifications': notifications,
            'unread_count': len(all_notifications)
        })

    except Exception as e:
        print(f"Get notifications error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/notifications/<int:log_id>/read', methods=['PATCH'])
@token_required
def mark_notification_read(current_user, log_id):
    """Mark a notification as read"""
    try:
        success = NotificationService.mark_notification_as_read(log_id)

        if not success:
            return error_response('Notification not found or already read', 404)

        return success_response(message='Notification marked as read')

    except Exception as e:
        print(f"Mark notification read error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= LOW STOCK ALERTS =============

@notifications_bp.route('/low-stock', methods=['GET'])
@token_required
def get_low_stock_products(current_user):
    """Get products with low stock"""
    try:
        products = NotificationService.get_low_stock_products()

        return success_response({
            'products': products,
            'count': len(products)
        })

    except Exception as e:
        print(f"Get low stock products error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/low-stock/alerts/send', methods=['POST'])
@token_required
def send_low_stock_alerts(current_user):
    """Send low stock alerts to all admins/doctors"""
    try:
        # Only admins can trigger this
        if current_user.get('role') != 'admin':
            return error_response('Unauthorized', 403)

        count = NotificationService.send_low_stock_alerts()

        return success_response({
            'notifications_sent': count
        }, f'{count} low stock alerts sent')

    except Exception as e:
        print(f"Send low stock alerts error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= APPOINTMENT REMINDERS =============

@notifications_bp.route('/appointments/today', methods=['GET'])
@token_required
def get_today_appointments(current_user):
    """Get today's appointments for current user (if doctor)"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)

        # If not specified, use current user (if they're a doctor)
        if not doctor_id:
            if current_user.get('role') != 'doctor':
                return error_response('Only doctors can view appointment reminders', 403)
            doctor_id = current_user['user_id']

        # Admins can view any doctor's appointments
        if current_user.get('role') != 'admin' and doctor_id != current_user['user_id']:
            return error_response('Unauthorized', 403)

        appointments_data = NotificationService.get_today_appointments_for_doctor(doctor_id)

        return success_response(appointments_data)

    except Exception as e:
        print(f"Get today appointments error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/appointments/upcoming', methods=['GET'])
@token_required
def get_upcoming_appointments(current_user):
    """Get upcoming appointments for current user (if doctor)"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)
        days = request.args.get('days', 7, type=int)

        # If not specified, use current user (if they're a doctor)
        if not doctor_id:
            if current_user.get('role') != 'doctor':
                return error_response('Only doctors can view appointment reminders', 403)
            doctor_id = current_user['user_id']

        # Admins can view any doctor's appointments
        if current_user.get('role') != 'admin' and doctor_id != current_user['user_id']:
            return error_response('Unauthorized', 403)

        appointments = NotificationService.get_upcoming_appointments_for_doctor(doctor_id, days)

        return success_response({
            'appointments': appointments,
            'count': len(appointments),
            'days': days
        })

    except Exception as e:
        print(f"Get upcoming appointments error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/daily-summary', methods=['GET'])
@token_required
def get_daily_summary(current_user):
    """Get daily summary for current user (if doctor)"""
    try:
        doctor_id = request.args.get('doctor_id', type=int)

        # If not specified, use current user (if they're a doctor)
        if not doctor_id:
            if current_user.get('role') != 'doctor':
                return error_response('Only doctors can view daily summaries', 403)
            doctor_id = current_user['user_id']

        # Admins can view any doctor's summary
        if current_user.get('role') != 'admin' and doctor_id != current_user['user_id']:
            return error_response('Unauthorized', 403)

        summary = NotificationService.generate_daily_summary_for_doctor(doctor_id)

        return success_response(summary)

    except Exception as e:
        print(f"Get daily summary error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/daily-summary/send', methods=['POST'])
@token_required
def send_daily_summaries(current_user):
    """Send daily summaries to all doctors (admin only)"""
    try:
        # Only admins can trigger this
        if current_user.get('role') != 'admin':
            return error_response('Unauthorized', 403)

        count = NotificationService.send_daily_summaries()

        return success_response({
            'summaries_sent': count
        }, f'{count} daily summaries sent')

    except Exception as e:
        print(f"Send daily summaries error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= NOTIFICATION PREFERENCES =============

@notifications_bp.route('/preferences', methods=['GET'])
@token_required
def get_notification_preferences(current_user):
    """Get notification preferences for current user"""
    try:
        preferences = NotificationService.get_notification_preferences(current_user['user_id'])

        if not preferences:
            # Return default preferences
            return success_response({
                'low_stock_notifications': True,
                'appointment_reminders': True,
                'daily_summary_enabled': True,
                'summary_time': '08:00:00'
            })

        return success_response(preferences)

    except Exception as e:
        print(f"Get notification preferences error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/preferences', methods=['PUT'])
@token_required
def update_notification_preferences(current_user):
    """Update notification preferences for current user"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data provided', 400)

        preferences = NotificationService.update_notification_preferences(
            current_user['user_id'],
            **data
        )

        return success_response(preferences, 'Preferences updated successfully')

    except Exception as e:
        print(f"Update notification preferences error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= REMINDER SETTINGS =============

@notifications_bp.route('/reminder-settings', methods=['GET'])
@token_required
def get_reminder_settings(current_user):
    """Get reminder settings for current user"""
    try:
        from common.reminder_manager import ReminderManager

        settings = ReminderManager.get_user_settings(current_user['user_id'])

        if not settings:
            # Return default settings
            return success_response({
                'email_enabled': True,
                'email_hours_before': [24, 3],
                'whatsapp_enabled': False,
                'whatsapp_hours_before': [24],
                'auto_send_enabled': True,
                'send_on_days': ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'],
                'quiet_hours_start': '22:00:00',
                'quiet_hours_end': '08:00:00'
            })

        return success_response(settings)

    except Exception as e:
        print(f"Get reminder settings error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/reminder-settings', methods=['PUT'])
@token_required
def update_reminder_settings(current_user):
    """Update reminder settings for current user"""
    try:
        from common.reminder_manager import ReminderManager

        data = request.get_json()

        if not data:
            return error_response('No data provided', 400)

        settings = ReminderManager.upsert_user_settings(
            current_user['user_id'],
            **data
        )

        if not settings:
            return error_response('No valid fields to update', 400)

        return success_response(settings, 'Reminder settings updated successfully')

    except Exception as e:
        print(f"Update reminder settings error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/reminder-logs', methods=['GET'])
@token_required
def get_reminder_logs(current_user):
    """Get reminder logs (filtered by user role)"""
    try:
        from common.reminder_manager import ReminderManager

        appointment_id = request.args.get('appointment_id', type=int)
        limit = request.args.get('limit', 100, type=int)

        # Doctors and admins can see logs
        if current_user.get('role') not in ['doctor', 'admin']:
            return error_response('Unauthorized', 403)

        logs = ReminderManager.get_reminder_logs(
            appointment_id=appointment_id,
            limit=limit
        )

        return success_response({
            'logs': logs,
            'count': len(logs)
        })

    except Exception as e:
        print(f"Get reminder logs error: {str(e)}")
        return error_response('An error occurred', 500)


@notifications_bp.route('/reminders/send-now', methods=['POST'])
@token_required
def send_reminders_now(current_user):
    """Manually trigger reminder processing (admin/doctor only)"""
    try:
        from common.reminder_manager import ReminderManager

        # Only admins and doctors can trigger this
        if current_user.get('role') not in ['admin', 'doctor']:
            return error_response('Unauthorized', 403)

        data = request.get_json() or {}
        appointment_id = data.get('appointment_id')
        hours_before = data.get('hours_before', 24)

        reminder_manager = ReminderManager()

        if appointment_id:
            # Send reminders for specific appointment
            from common.database import db
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT
                        a.appointment_id,
                        a.start_time,
                        a.doctor_id,
                        a.reason,
                        p.patient_id,
                        p.first_name || ' ' || p.last_name as patient_name,
                        p.email as patient_email,
                        p.phone as patient_phone,
                        u.full_name as doctor_name
                    FROM appointments a
                    LEFT JOIN patients p ON a.patient_id = p.patient_id
                    LEFT JOIN users u ON a.doctor_id = u.user_id
                    WHERE a.appointment_id = %s
                """, (appointment_id,))

                appointment = cursor.fetchone()

                if not appointment:
                    return error_response('Appointment not found', 404)

                # Check if user has permission
                if current_user.get('role') != 'admin' and appointment['doctor_id'] != current_user['user_id']:
                    return error_response('Unauthorized', 403)

                results = {
                    'email_sent': False,
                    'whatsapp_sent': False
                }

                # Get user settings
                settings = ReminderManager.get_user_settings(current_user['user_id'])

                if settings and settings.get('email_enabled'):
                    results['email_sent'] = reminder_manager.send_email_reminder(appointment, hours_before)

                if settings and settings.get('whatsapp_enabled'):
                    results['whatsapp_sent'] = reminder_manager.send_whatsapp_reminder(appointment, hours_before)

                return success_response(results, 'Reminders sent')
        else:
            # Process all scheduled reminders
            stats = reminder_manager.process_scheduled_reminders()
            return success_response(stats, 'Scheduled reminders processed')

    except Exception as e:
        print(f"Send reminders now error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response('An error occurred', 500)


# Health check
@notifications_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'notifications'})
