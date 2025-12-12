"""
Models for Citas Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


class AppointmentModel:
    """Appointment database operations"""

    @staticmethod
    def get_by_id(appointment_id):
        """Get appointment by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.appointment_id, a.patient_id, a.doctor_id, a.start_time, a.end_time,
                       a.status, a.reason, a.created_at,
                       p.first_name || ' ' || p.last_name as patient_name,
                       p.doc_number, p.phone, p.email,
                       u.full_name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN users u ON a.doctor_id = u.user_id
                WHERE a.appointment_id = %s
            """, (appointment_id,))
            return cursor.fetchone()

    @staticmethod
    def list_appointments(limit=20, offset=0, patient_id=None, doctor_id=None,
                         status=None, date_from=None, date_to=None):
        """List appointments with filters"""
        query = """
            SELECT a.appointment_id, a.patient_id, a.doctor_id, a.start_time, a.end_time,
                   a.status, a.reason, a.created_at,
                   p.first_name || ' ' || p.last_name as patient_name,
                   u.full_name as doctor_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.patient_id
            LEFT JOIN users u ON a.doctor_id = u.user_id
            WHERE 1=1
        """
        params = []

        if patient_id:
            query += " AND a.patient_id = %s"
            params.append(patient_id)

        if doctor_id:
            query += " AND a.doctor_id = %s"
            params.append(doctor_id)

        if status:
            query += " AND a.status = %s"
            params.append(status)

        if date_from:
            query += " AND a.start_time >= %s"
            params.append(date_from)

        if date_to:
            query += " AND a.start_time <= %s"
            params.append(date_to)

        query += " ORDER BY a.start_time DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_appointments(patient_id=None, doctor_id=None, status=None, date_from=None, date_to=None):
        """Count appointments"""
        query = "SELECT COUNT(*) as count FROM appointments WHERE 1=1"
        params = []

        if patient_id:
            query += " AND patient_id = %s"
            params.append(patient_id)

        if doctor_id:
            query += " AND doctor_id = %s"
            params.append(doctor_id)

        if status:
            query += " AND status = %s"
            params.append(status)

        if date_from:
            query += " AND start_time >= %s"
            params.append(date_from)

        if date_to:
            query += " AND start_time <= %s"
            params.append(date_to)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(patient_id, doctor_id, start_time, end_time, reason, status='PENDING'):
        """Create a new appointment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, start_time, end_time, reason, status)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING appointment_id, patient_id, doctor_id, start_time, end_time,
                         reason, status, created_at
            """, (patient_id, doctor_id, start_time, end_time, reason, status))
            return cursor.fetchone()

    @staticmethod
    def update(appointment_id, **kwargs):
        """Update appointment"""
        allowed_fields = ['patient_id', 'doctor_id', 'start_time', 'end_time', 'reason', 'status']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(appointment_id)
        query = f"""
            UPDATE appointments
            SET {', '.join(updates)}
            WHERE appointment_id = %s
            RETURNING appointment_id, patient_id, doctor_id, start_time, end_time,
                     reason, status, created_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def update_status(appointment_id, status):
        """Update appointment status"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE appointments
                SET status = %s
                WHERE appointment_id = %s
                RETURNING appointment_id, status
            """, (status, appointment_id))
            return cursor.fetchone()

    @staticmethod
    def check_availability(doctor_id, start_time, end_time, exclude_appointment_id=None):
        """Check if doctor is available for the given time slot"""
        query = """
            SELECT COUNT(*) as count
            FROM appointments
            WHERE doctor_id = %s
            AND status NOT IN ('CANCELLED')
            AND (
                (start_time <= %s AND end_time > %s) OR
                (start_time < %s AND end_time >= %s) OR
                (start_time >= %s AND end_time <= %s)
            )
        """
        params = [doctor_id, start_time, start_time, end_time, end_time, start_time, end_time]

        if exclude_appointment_id:
            query += " AND appointment_id != %s"
            params.append(exclude_appointment_id)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] == 0 if result else False

    @staticmethod
    def get_doctor_schedule(doctor_id, date):
        """Get all appointments for a doctor on a specific date"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT a.appointment_id, a.start_time, a.end_time, a.status, a.reason,
                       p.first_name || ' ' || p.last_name as patient_name,
                       p.phone
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                WHERE a.doctor_id = %s
                AND DATE(a.start_time) = %s
                AND a.status NOT IN ('CANCELLED')
                ORDER BY a.start_time
            """, (doctor_id, date))
            return cursor.fetchall()


class AppointmentTreatmentModel:
    """Appointment Treatment database operations"""

    @staticmethod
    def get_by_appointment_id(appointment_id):
        """Get all treatments for an appointment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT at.detail_id, at.appointment_id, at.treatment_id, at.price_at_moment, at.quantity,
                       t.name as treatment_name, t.base_price
                FROM appointment_treatments at
                JOIN treatments t ON at.treatment_id = t.treatment_id
                WHERE at.appointment_id = %s
                ORDER BY at.detail_id
            """, (appointment_id,))
            return cursor.fetchall()

    @staticmethod
    def add_treatment(appointment_id, treatment_id, price_at_moment, quantity=1):
        """Add treatment to appointment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO appointment_treatments (appointment_id, treatment_id, price_at_moment, quantity)
                VALUES (%s, %s, %s, %s)
                RETURNING detail_id, appointment_id, treatment_id, price_at_moment, quantity
            """, (appointment_id, treatment_id, price_at_moment, quantity))
            return cursor.fetchone()

    @staticmethod
    def remove_treatment(detail_id):
        """Remove treatment from appointment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM appointment_treatments
                WHERE detail_id = %s
                RETURNING detail_id
            """, (detail_id,))
            return cursor.fetchone()

    @staticmethod
    def update_treatment(detail_id, price_at_moment=None, quantity=None):
        """Update treatment in appointment"""
        updates = []
        params = []

        if price_at_moment is not None:
            updates.append("price_at_moment = %s")
            params.append(price_at_moment)

        if quantity is not None:
            updates.append("quantity = %s")
            params.append(quantity)

        if not updates:
            return None

        params.append(detail_id)
        query = f"""
            UPDATE appointment_treatments
            SET {', '.join(updates)}
            WHERE detail_id = %s
            RETURNING detail_id, appointment_id, treatment_id, price_at_moment, quantity
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def calculate_total(appointment_id):
        """Calculate total cost of treatments for appointment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(price_at_moment * quantity), 0) as total
                FROM appointment_treatments
                WHERE appointment_id = %s
            """, (appointment_id,))
            result = cursor.fetchone()
            return float(result['total']) if result else 0.0


class AppointmentExtraModel:
    """Appointment Extra (additional products) database operations"""

    @staticmethod
    def get_by_appointment_id(appointment_id):
        """Get all extra products for an appointment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT ae.extra_id, ae.appointment_id, ae.product_id, ae.quantity, ae.price_charged,
                       p.name as product_name, p.sale_price
                FROM appointment_extras ae
                JOIN products p ON ae.product_id = p.product_id
                WHERE ae.appointment_id = %s
                ORDER BY ae.extra_id
            """, (appointment_id,))
            return cursor.fetchall()

    @staticmethod
    def add_extra(appointment_id, product_id, quantity, price_charged=0):
        """Add extra product to appointment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO appointment_extras (appointment_id, product_id, quantity, price_charged)
                VALUES (%s, %s, %s, %s)
                RETURNING extra_id, appointment_id, product_id, quantity, price_charged
            """, (appointment_id, product_id, quantity, price_charged))
            return cursor.fetchone()

    @staticmethod
    def remove_extra(extra_id):
        """Remove extra product from appointment"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM appointment_extras
                WHERE extra_id = %s
                RETURNING extra_id
            """, (extra_id,))
            return cursor.fetchone()

    @staticmethod
    def update_extra(extra_id, quantity=None, price_charged=None):
        """Update extra product in appointment"""
        updates = []
        params = []

        if quantity is not None:
            updates.append("quantity = %s")
            params.append(quantity)

        if price_charged is not None:
            updates.append("price_charged = %s")
            params.append(price_charged)

        if not updates:
            return None

        params.append(extra_id)
        query = f"""
            UPDATE appointment_extras
            SET {', '.join(updates)}
            WHERE extra_id = %s
            RETURNING extra_id, appointment_id, product_id, quantity, price_charged
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def calculate_total(appointment_id):
        """Calculate total cost of extras for appointment"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT COALESCE(SUM(price_charged * quantity), 0) as total
                FROM appointment_extras
                WHERE appointment_id = %s
            """, (appointment_id,))
            result = cursor.fetchone()
            return float(result['total']) if result else 0.0
