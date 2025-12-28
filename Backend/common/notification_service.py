"""
Notification Service
Handles low stock alerts and appointment reminders
"""
from datetime import datetime, date, timedelta
from common.database import db


class NotificationService:
    """Service for managing notifications"""

    @staticmethod
    def get_low_stock_products(minimum_threshold=None):
        """
        Get products with low stock

        Args:
            minimum_threshold: Optional threshold override

        Returns:
            list: Products with current_stock <= minimum_stock
        """
        with db.get_cursor() as cursor:
            query = """
                SELECT
                    product_id,
                    sku,
                    name,
                    current_stock,
                    minimum_stock,
                    (minimum_stock - current_stock) as units_needed,
                    category,
                    type
                FROM products
                WHERE current_stock <= minimum_stock
                ORDER BY (minimum_stock - current_stock) DESC
            """

            cursor.execute(query)
            return cursor.fetchall()

    @staticmethod
    def get_today_appointments_for_doctor(doctor_id):
        """
        Get all appointments for a doctor today

        Args:
            doctor_id: Doctor's user ID

        Returns:
            dict: Summary with count, appointments list, and time ranges
        """
        today = date.today()
        date_from = today.strftime('%Y-%m-%d 00:00:00')
        date_to = today.strftime('%Y-%m-%d 23:59:59')

        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    a.start_time,
                    a.end_time,
                    a.status,
                    a.reason,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.phone as patient_phone,
                    p.email as patient_email,
                    p.doc_number
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                AND a.start_time >= %s::timestamp
                AND a.start_time <= %s::timestamp
                AND a.status IN ('PENDING', 'CONFIRMED')
                ORDER BY a.start_time ASC
            """, (doctor_id, date_from, date_to))

            appointments = cursor.fetchall()

        return {
            'count': len(appointments),
            'appointments': appointments,
            'date': today.isoformat()
        }

    @staticmethod
    def get_upcoming_appointments_for_doctor(doctor_id, days=7):
        """
        Get upcoming appointments for a doctor in the next N days

        Args:
            doctor_id: Doctor's user ID
            days: Number of days to look ahead

        Returns:
            list: Appointments list
        """
        date_from = datetime.now().strftime('%Y-%m-%d 00:00:00')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d 23:59:59')

        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    a.start_time,
                    a.end_time,
                    a.status,
                    a.reason,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.phone as patient_phone,
                    p.email as patient_email
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                AND a.start_time >= %s::timestamp
                AND a.start_time <= %s::timestamp
                AND a.status IN ('PENDING', 'CONFIRMED')
                ORDER BY a.start_time ASC
            """, (doctor_id, date_from, date_to))

            return cursor.fetchall()

    @staticmethod
    def create_notification(user_id, notification_type, title, message, metadata=None):
        """
        Create a notification log entry

        Args:
            user_id: User to notify
            notification_type: Type of notification ('low_stock', 'appointment_reminder', 'daily_summary')
            title: Notification title
            message: Notification message
            metadata: Additional data (dict)

        Returns:
            int: Notification log ID
        """
        import json

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO notification_logs (user_id, notification_type, title, message, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING log_id
            """, (user_id, notification_type, title, message, json.dumps(metadata) if metadata else None))

            result = cursor.fetchone()
            return result['log_id'] if result else None

    @staticmethod
    def get_user_notifications(user_id, limit=50, unread_only=False):
        """
        Get notifications for a user

        Args:
            user_id: User ID
            limit: Maximum notifications to return
            unread_only: If True, only return unread notifications

        Returns:
            list: Notifications
        """
        query = """
            SELECT
                log_id,
                notification_type,
                title,
                message,
                sent_at,
                read_at,
                metadata
            FROM notification_logs
            WHERE user_id = %s
        """

        params = [user_id]

        if unread_only:
            query += " AND read_at IS NULL"

        query += " ORDER BY sent_at DESC LIMIT %s"
        params.append(limit)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def mark_notification_as_read(log_id):
        """
        Mark a notification as read

        Args:
            log_id: Notification log ID

        Returns:
            bool: True if updated
        """
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE notification_logs
                SET read_at = CURRENT_TIMESTAMP
                WHERE log_id = %s AND read_at IS NULL
                RETURNING log_id
            """, (log_id,))

            return cursor.fetchone() is not None

    @staticmethod
    def get_notification_preferences(user_id):
        """
        Get notification preferences for a user

        Args:
            user_id: User ID

        Returns:
            dict: Preferences or None
        """
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    low_stock_notifications,
                    appointment_reminders,
                    daily_summary_enabled,
                    summary_time
                FROM notification_preferences
                WHERE user_id = %s
            """, (user_id,))

            return cursor.fetchone()

    @staticmethod
    def update_notification_preferences(user_id, **kwargs):
        """
        Update notification preferences for a user

        Args:
            user_id: User ID
            **kwargs: Fields to update (low_stock_notifications, appointment_reminders, etc.)

        Returns:
            dict: Updated preferences
        """
        allowed_fields = ['low_stock_notifications', 'appointment_reminders',
                         'daily_summary_enabled', 'summary_time']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(user_id)

        with db.get_cursor(commit=True) as cursor:
            # Insert or update
            cursor.execute(f"""
                INSERT INTO notification_preferences (user_id, {', '.join(allowed_fields[:len(updates)])})
                VALUES (%s, {', '.join(['%s'] * len(updates))})
                ON CONFLICT (user_id) DO UPDATE
                SET {', '.join(updates)}
                RETURNING *
            """, [user_id] + params[:-1])

            return cursor.fetchone()

    @staticmethod
    def generate_daily_summary_for_doctor(doctor_id):
        """
        Generate a daily summary for a doctor

        Args:
            doctor_id: Doctor's user ID

        Returns:
            dict: Summary data
        """
        # Get today's appointments
        appointments_data = NotificationService.get_today_appointments_for_doctor(doctor_id)

        # Get low stock products (for admins/doctors with inventory access)
        low_stock = NotificationService.get_low_stock_products()

        # Build summary message
        summary_parts = []

        if appointments_data['count'] > 0:
            summary_parts.append(f"📅 Tiene {appointments_data['count']} cita(s) programada(s) hoy:")
            for appt in appointments_data['appointments']:
                start_time = appt['start_time'].strftime('%H:%M')
                summary_parts.append(f"  • {start_time} - {appt['patient_name']}")
                if appt['reason']:
                    summary_parts.append(f"    Motivo: {appt['reason']}")
        else:
            summary_parts.append("📅 No tiene citas programadas para hoy")

        if low_stock:
            summary_parts.append(f"\n⚠️ Hay {len(low_stock)} producto(s) con stock bajo:")
            for product in low_stock[:5]:  # Show top 5
                summary_parts.append(f"  • {product['name']}: {product['current_stock']} unidades (mínimo: {product['minimum_stock']})")

        message = "\n".join(summary_parts)

        return {
            'appointments_count': appointments_data['count'],
            'appointments': appointments_data['appointments'],
            'low_stock_count': len(low_stock),
            'low_stock_items': low_stock[:10],  # Limit to top 10
            'summary_message': message
        }

    @staticmethod
    def send_low_stock_alerts():
        """
        Send low stock alerts to admins and doctors with notification preferences enabled

        Returns:
            int: Number of notifications sent
        """
        # Get low stock products
        low_stock_products = NotificationService.get_low_stock_products()

        if not low_stock_products:
            return 0

        # Get users with low_stock_notifications enabled
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.email, u.full_name
                FROM users u
                JOIN notification_preferences np ON u.user_id = np.user_id
                WHERE np.low_stock_notifications = TRUE
                AND u.role IN ('admin', 'doctor')
            """)

            users = cursor.fetchall()

        notifications_sent = 0

        for user in users:
            # Build notification message
            products_list = "\n".join([
                f"• {p['name']}: {p['current_stock']} unidades (necesita {p['units_needed']} más)"
                for p in low_stock_products[:10]
            ])

            message = f"Hay {len(low_stock_products)} producto(s) con stock bajo:\n\n{products_list}"

            # Create notification
            NotificationService.create_notification(
                user_id=user['user_id'],
                notification_type='low_stock',
                title=f'⚠️ Alerta de Stock Bajo ({len(low_stock_products)} productos)',
                message=message,
                metadata={'product_count': len(low_stock_products)}
            )

            notifications_sent += 1

        return notifications_sent

    @staticmethod
    def send_daily_summaries():
        """
        Send daily summaries to all doctors with daily_summary_enabled=True

        Returns:
            int: Number of summaries sent
        """
        # Get doctors with daily summaries enabled
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT u.user_id, u.email, u.full_name
                FROM users u
                JOIN notification_preferences np ON u.user_id = np.user_id
                WHERE np.daily_summary_enabled = TRUE
                AND u.role = 'doctor'
            """)

            doctors = cursor.fetchall()

        summaries_sent = 0

        for doctor in doctors:
            # Generate summary
            summary = NotificationService.generate_daily_summary_for_doctor(doctor['user_id'])

            # Create notification
            NotificationService.create_notification(
                user_id=doctor['user_id'],
                notification_type='daily_summary',
                title=f'📋 Resumen del Día - {date.today().strftime("%d/%m/%Y")}',
                message=summary['summary_message'],
                metadata={
                    'appointments_count': summary['appointments_count'],
                    'low_stock_count': summary['low_stock_count']
                }
            )

            summaries_sent += 1

        return summaries_sent
