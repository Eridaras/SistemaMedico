"""
Reminder Manager
Handles scheduling and sending of appointment reminders via email and WhatsApp
"""
from datetime import datetime, timedelta
from common.database import db
from common.email_service import EmailService
from common.whatsapp_service import WhatsAppService
import json


class ReminderManager:
    """Manages appointment reminders"""

    def __init__(self):
        self.email_service = EmailService()
        self.whatsapp_service = WhatsAppService()

    @staticmethod
    def get_user_settings(user_id):
        """
        Get reminder settings for a user

        Args:
            user_id: User ID

        Returns:
            dict: Reminder settings or None
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    setting_id,
                    email_enabled,
                    email_hours_before,
                    whatsapp_enabled,
                    whatsapp_hours_before,
                    auto_send_enabled,
                    send_on_days,
                    quiet_hours_start,
                    quiet_hours_end,
                    smtp_host,
                    smtp_port,
                    smtp_user,
                    from_email,
                    from_name,
                    twilio_account_sid,
                    twilio_whatsapp_number
                FROM reminder_settings
                WHERE user_id = %s
            """, (user_id,))

            return cursor.fetchone()

    @staticmethod
    def upsert_user_settings(user_id, **kwargs):
        """
        Update or insert reminder settings for a user

        Args:
            user_id: User ID
            **kwargs: Settings to update

        Returns:
            dict: Updated settings
        """
        allowed_fields = [
            'email_enabled', 'email_hours_before',
            'whatsapp_enabled', 'whatsapp_hours_before',
            'auto_send_enabled', 'send_on_days',
            'quiet_hours_start', 'quiet_hours_end',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password',
            'from_email', 'from_name',
            'twilio_account_sid', 'twilio_auth_token', 'twilio_whatsapp_number'
        ]

        # Build update/insert query
        fields_to_update = []
        values = []

        for field in allowed_fields:
            if field in kwargs:
                fields_to_update.append(field)
                value = kwargs[field]

                # Convert lists to JSON for JSONB fields
                if field in ['email_hours_before', 'whatsapp_hours_before', 'send_on_days']:
                    value = json.dumps(value) if isinstance(value, (list, dict)) else value

                values.append(value)

        if not fields_to_update:
            return None

        values.append(user_id)

        # Build SQL
        update_set = ', '.join([f"{field} = %s" for field in fields_to_update])
        placeholders = ', '.join(['%s'] * len(fields_to_update))

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(f"""
                INSERT INTO reminder_settings (user_id, {', '.join(fields_to_update)})
                VALUES (%s, {placeholders})
                ON CONFLICT (user_id) DO UPDATE
                SET {update_set}
                RETURNING *
            """, [user_id] + values + values)

            return cursor.fetchone()

    def get_appointments_needing_reminders(self, hours_before):
        """
        Get appointments that need reminders sent

        Args:
            hours_before: Hours before appointment to send reminder

        Returns:
            list: Appointments needing reminders
        """
        # Calculate time window
        now = datetime.now()
        target_time_start = now + timedelta(hours=hours_before - 0.5)  # 30min before target
        target_time_end = now + timedelta(hours=hours_before + 0.5)    # 30min after target

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
                WHERE a.status IN ('PENDING', 'CONFIRMED')
                AND a.start_time BETWEEN %s AND %s
                AND NOT EXISTS (
                    SELECT 1 FROM reminder_logs rl
                    WHERE rl.appointment_id = a.appointment_id
                    AND rl.hours_before = %s
                    AND rl.status = 'sent'
                )
            """, (target_time_start, target_time_end, hours_before))

            return cursor.fetchall()

    def send_email_reminder(self, appointment, hours_before):
        """
        Send email reminder for an appointment

        Args:
            appointment: Appointment data dictionary
            hours_before: Hours before appointment

        Returns:
            bool: True if sent successfully
        """
        if not appointment.get('patient_email'):
            print(f"⚠️ No email for patient {appointment['patient_name']}")
            return False

        # Prepare appointment data for template
        appointment_data = {
            'patient_name': appointment['patient_name'],
            'doctor_name': appointment['doctor_name'],
            'appointment_date': appointment['start_time'],
            'appointment_time': appointment['start_time'].strftime('%H:%M') if isinstance(appointment['start_time'], datetime) else '',
            'reason': appointment.get('reason', 'Consulta médica'),
            'clinic_address': 'Av. Principal 123, Quito, Ecuador',
            'clinic_phone': '02-123-4567'
        }

        # Send email
        success = self.email_service.send_appointment_reminder(
            appointment['patient_email'],
            appointment_data,
            hours_before
        )

        # Log result
        self._log_reminder(
            appointment['appointment_id'],
            appointment['patient_id'],
            'email',
            hours_before,
            'sent' if success else 'failed',
            appointment['patient_email'],
            None,
            None if success else 'Email sending failed'
        )

        return success

    def send_whatsapp_reminder(self, appointment, hours_before):
        """
        Send WhatsApp reminder for an appointment

        Args:
            appointment: Appointment data dictionary
            hours_before: Hours before appointment

        Returns:
            bool: True if sent successfully
        """
        if not appointment.get('patient_phone'):
            print(f"⚠️ No phone for patient {appointment['patient_name']}")
            return False

        # Format phone number for Ecuador (+593)
        phone = appointment['patient_phone']
        if not phone.startswith('+'):
            # Assume Ecuador number, remove leading 0 and add +593
            phone = phone.lstrip('0')
            phone = f"+593{phone}"

        # Prepare appointment data for template
        appointment_data = {
            'patient_name': appointment['patient_name'],
            'doctor_name': appointment['doctor_name'],
            'appointment_date': appointment['start_time'],
            'appointment_time': appointment['start_time'].strftime('%H:%M') if isinstance(appointment['start_time'], datetime) else '',
            'reason': appointment.get('reason', 'Consulta médica'),
            'clinic_address': 'Av. Principal 123, Quito',
            'clinic_phone': '02-123-4567'
        }

        # Send WhatsApp
        success = self.whatsapp_service.send_appointment_reminder(
            phone,
            appointment_data,
            hours_before
        )

        # Log result
        self._log_reminder(
            appointment['appointment_id'],
            appointment['patient_id'],
            'whatsapp',
            hours_before,
            'sent' if success else 'failed',
            None,
            phone,
            None if success else 'WhatsApp sending failed'
        )

        return success

    def _log_reminder(self, appointment_id, patient_id, reminder_type, hours_before,
                     status, recipient_email, recipient_phone, error_message):
        """Log reminder sending attempt"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO reminder_logs (
                    appointment_id, patient_id, reminder_type, hours_before,
                    status, sent_at, error_message, recipient_email, recipient_phone
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                appointment_id, patient_id, reminder_type, hours_before,
                status, datetime.now() if status == 'sent' else None,
                error_message, recipient_email, recipient_phone
            ))

    def process_scheduled_reminders(self):
        """
        Process all scheduled reminders based on user settings

        This should be run periodically (every 30 minutes) via cron job

        Returns:
            dict: Statistics of processed reminders
        """
        stats = {
            'total_processed': 0,
            'email_sent': 0,
            'whatsapp_sent': 0,
            'failed': 0
        }

        # Get all unique hours_before values from all users' settings
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT jsonb_array_elements_text(email_hours_before)::int as hours
                FROM reminder_settings
                WHERE email_enabled = TRUE AND auto_send_enabled = TRUE
                UNION
                SELECT DISTINCT jsonb_array_elements_text(whatsapp_hours_before)::int as hours
                FROM reminder_settings
                WHERE whatsapp_enabled = TRUE AND auto_send_enabled = TRUE
            """)

            hours_list = [row['hours'] for row in cursor.fetchall()]

        # Process each time window
        for hours_before in hours_list:
            appointments = self.get_appointments_needing_reminders(hours_before)

            for appointment in appointments:
                stats['total_processed'] += 1

                # Get doctor's settings
                settings = self.get_user_settings(appointment['doctor_id'])

                if not settings or not settings.get('auto_send_enabled'):
                    continue

                # Send email if enabled
                if settings.get('email_enabled'):
                    email_hours = json.loads(settings['email_hours_before']) if isinstance(settings['email_hours_before'], str) else settings['email_hours_before']
                    if hours_before in email_hours:
                        if self.send_email_reminder(appointment, hours_before):
                            stats['email_sent'] += 1
                        else:
                            stats['failed'] += 1

                # Send WhatsApp if enabled
                if settings.get('whatsapp_enabled'):
                    whatsapp_hours = json.loads(settings['whatsapp_hours_before']) if isinstance(settings['whatsapp_hours_before'], str) else settings['whatsapp_hours_before']
                    if hours_before in whatsapp_hours:
                        if self.send_whatsapp_reminder(appointment, hours_before):
                            stats['whatsapp_sent'] += 1
                        else:
                            stats['failed'] += 1

        print(f"📊 Reminder processing complete: {stats}")
        return stats

    @staticmethod
    def get_reminder_logs(appointment_id=None, limit=100):
        """
        Get reminder logs

        Args:
            appointment_id: Optional filter by appointment
            limit: Maximum logs to return

        Returns:
            list: Reminder logs
        """
        query = """
            SELECT
                rl.*,
                p.first_name || ' ' || p.last_name as patient_name
            FROM reminder_logs rl
            LEFT JOIN patients p ON rl.patient_id = p.patient_id
            WHERE 1=1
        """
        params = []

        if appointment_id:
            query += " AND rl.appointment_id = %s"
            params.append(appointment_id)

        query += " ORDER BY rl.created_at DESC LIMIT %s"
        params.append(limit)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
