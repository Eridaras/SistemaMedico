"""
Models for Historia Clinica Service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


class PatientModel:
    """Patient database operations"""

    @staticmethod
    def get_by_id(patient_id):
        """Get patient by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT patient_id, doc_type, doc_number, first_name, last_name,
                       email, phone, address, birth_date, gender, created_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_doc_number(doc_number):
        """Get patient by document number"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT patient_id, doc_type, doc_number, first_name, last_name,
                       email, phone, address, birth_date, gender, created_at
                FROM patients
                WHERE doc_number = %s
            """, (doc_number,))
            return cursor.fetchone()

    @staticmethod
    def list_patients(limit=20, offset=0, search=None):
        """List patients with pagination"""
        query = """
            SELECT patient_id, doc_type, doc_number, first_name, last_name,
                   email, phone, address, birth_date, gender, created_at
            FROM patients
        """
        params = []

        if search:
            query += """
                WHERE first_name ILIKE %s OR last_name ILIKE %s
                OR doc_number ILIKE %s OR email ILIKE %s
            """
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        query += " ORDER BY first_name, last_name LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_patients(search=None):
        """Count patients"""
        query = "SELECT COUNT(*) as count FROM patients"
        params = []

        if search:
            query += """
                WHERE first_name ILIKE %s OR last_name ILIKE %s
                OR doc_number ILIKE %s OR email ILIKE %s
            """
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(doc_type, doc_number, first_name, last_name, email, phone, address, birth_date, gender):
        """Create a new patient"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO patients (doc_type, doc_number, first_name, last_name,
                                    email, phone, address, birth_date, gender)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING patient_id, doc_type, doc_number, first_name, last_name,
                         email, phone, address, birth_date, gender, created_at
            """, (doc_type, doc_number, first_name, last_name, email, phone, address, birth_date, gender))
            return cursor.fetchone()

    @staticmethod
    def update(patient_id, **kwargs):
        """Update patient"""
        allowed_fields = ['doc_type', 'doc_number', 'first_name', 'last_name',
                         'email', 'phone', 'address', 'birth_date', 'gender']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(patient_id)
        query = f"""
            UPDATE patients
            SET {', '.join(updates)}
            WHERE patient_id = %s
            RETURNING patient_id, doc_type, doc_number, first_name, last_name,
                     email, phone, address, birth_date, gender, created_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def get_full_history(patient_id):
        """Get patient with all related data"""
        with db.get_cursor() as cursor:
            # Get patient data
            cursor.execute("""
                SELECT patient_id, doc_type, doc_number, first_name, last_name,
                       email, phone, address, birth_date, gender, created_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            patient = cursor.fetchone()

            if not patient:
                return None

            # Get medical history
            cursor.execute("""
                SELECT history_id, allergies, pathologies, surgeries,
                       family_history, blood_type, updated_at
                FROM medical_history
                WHERE patient_id = %s
            """, (patient_id,))
            medical_history = cursor.fetchone()

            # Get appointments
            cursor.execute("""
                SELECT a.appointment_id, a.doctor_id, a.start_time, a.end_time,
                       a.status, a.reason, a.created_at,
                       u.full_name as doctor_name
                FROM appointments a
                LEFT JOIN users u ON a.doctor_id = u.user_id
                WHERE a.patient_id = %s
                ORDER BY a.start_time DESC
                LIMIT 10
            """, (patient_id,))
            appointments = cursor.fetchall()

            return {
                'patient': patient,
                'medical_history': medical_history,
                'recent_appointments': appointments
            }


class MedicalHistoryModel:
    """Medical History database operations"""

    @staticmethod
    def get_by_patient_id(patient_id):
        """Get medical history by patient ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT history_id, patient_id, allergies, pathologies, surgeries,
                       family_history, blood_type, updated_at
                FROM medical_history
                WHERE patient_id = %s
            """, (patient_id,))
            return cursor.fetchone()

    @staticmethod
    def create(patient_id, allergies, pathologies, surgeries, family_history, blood_type):
        """Create medical history"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO medical_history (patient_id, allergies, pathologies, surgeries,
                                            family_history, blood_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING history_id, patient_id, allergies, pathologies, surgeries,
                         family_history, blood_type, updated_at
            """, (patient_id, allergies, pathologies, surgeries, family_history, blood_type))
            return cursor.fetchone()

    @staticmethod
    def update(patient_id, **kwargs):
        """Update medical history"""
        allowed_fields = ['allergies', 'pathologies', 'surgeries', 'family_history', 'blood_type']

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(patient_id)

        query = f"""
            UPDATE medical_history
            SET {', '.join(updates)}
            WHERE patient_id = %s
            RETURNING history_id, patient_id, allergies, pathologies, surgeries,
                     family_history, blood_type, updated_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def upsert(patient_id, allergies, pathologies, surgeries, family_history, blood_type):
        """Create or update medical history"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO medical_history (patient_id, allergies, pathologies, surgeries,
                                            family_history, blood_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id)
                DO UPDATE SET
                    allergies = EXCLUDED.allergies,
                    pathologies = EXCLUDED.pathologies,
                    surgeries = EXCLUDED.surgeries,
                    family_history = EXCLUDED.family_history,
                    blood_type = EXCLUDED.blood_type,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING history_id, patient_id, allergies, pathologies, surgeries,
                         family_history, blood_type, updated_at
            """, (patient_id, allergies, pathologies, surgeries, family_history, blood_type))
            return cursor.fetchone()


class ClinicalNoteModel:
    """Clinical Note database operations"""

    @staticmethod
    def get_by_id(note_id):
        """Get clinical note by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT cn.note_id, cn.appointment_id, cn.observations, cn.diagnosis, cn.created_at,
                       a.patient_id, a.doctor_id, a.start_time,
                       u.full_name as doctor_name,
                       p.first_name || ' ' || p.last_name as patient_name
                FROM clinical_notes cn
                JOIN appointments a ON cn.appointment_id = a.appointment_id
                JOIN users u ON a.doctor_id = u.user_id
                JOIN patients p ON a.patient_id = p.patient_id
                WHERE cn.note_id = %s
            """, (note_id,))
            return cursor.fetchone()

    @staticmethod
    def get_by_appointment_id(appointment_id):
        """Get clinical notes by appointment ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT cn.note_id, cn.appointment_id, cn.observations, cn.diagnosis, cn.created_at,
                       u.full_name as doctor_name
                FROM clinical_notes cn
                JOIN appointments a ON cn.appointment_id = a.appointment_id
                JOIN users u ON a.doctor_id = u.user_id
                WHERE cn.appointment_id = %s
                ORDER BY cn.created_at DESC
            """, (appointment_id,))
            return cursor.fetchall()

    @staticmethod
    def get_by_patient_id(patient_id, limit=20, offset=0):
        """Get clinical notes by patient ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT cn.note_id, cn.appointment_id, cn.observations, cn.diagnosis, cn.created_at,
                       a.start_time as appointment_date,
                       u.full_name as doctor_name
                FROM clinical_notes cn
                JOIN appointments a ON cn.appointment_id = a.appointment_id
                JOIN users u ON a.doctor_id = u.user_id
                WHERE a.patient_id = %s
                ORDER BY cn.created_at DESC
                LIMIT %s OFFSET %s
            """, (patient_id, limit, offset))
            return cursor.fetchall()

    @staticmethod
    def create(appointment_id, observations, diagnosis):
        """Create clinical note"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO clinical_notes (appointment_id, observations, diagnosis)
                VALUES (%s, %s, %s)
                RETURNING note_id, appointment_id, observations, diagnosis, created_at
            """, (appointment_id, observations, diagnosis))
            return cursor.fetchone()

    @staticmethod
    def update(note_id, observations=None, diagnosis=None):
        """Update clinical note"""
        updates = []
        params = []

        if observations is not None:
            updates.append("observations = %s")
            params.append(observations)

        if diagnosis is not None:
            updates.append("diagnosis = %s")
            params.append(diagnosis)

        if not updates:
            return None

        params.append(note_id)
        query = f"""
            UPDATE clinical_notes
            SET {', '.join(updates)}
            WHERE note_id = %s
            RETURNING note_id, appointment_id, observations, diagnosis, created_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
