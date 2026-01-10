"""
Models for Historia Clinica Service
"""
import sys
import os
from datetime import date, datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


def format_date_for_api(date_obj):
    """Convert date/datetime object to ISO format string (YYYY-MM-DD)"""
    if date_obj is None:
        return None
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d')
    if isinstance(date_obj, date):
        return date_obj.strftime('%Y-%m-%d')
    return str(date_obj)


class PatientModel:
    """Patient database operations"""

    @staticmethod
    def get_by_id(patient_id):
        """Get patient by ID"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT patient_id, full_name, identification, identification_type,
                       email, phone, address, date_of_birth, gender, created_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            result = cursor.fetchone()
            # Transform to expected format
            if result:
                result_dict = dict(result)
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', 'CEDULA')
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                return result_dict
            return None

    @staticmethod
    def get_by_doc_number(doc_number):
        """Get patient by document number (includes inactive patients)"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT patient_id, full_name, identification, identification_type,
                       email, phone, address, date_of_birth, gender, created_at, is_active
                FROM patients
                WHERE identification = %s
            """, (doc_number,))
            result = cursor.fetchone()
            # Transform to expected format
            if result:
                result_dict = dict(result)
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', 'CEDULA')
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                return result_dict
            return None

    @staticmethod
    def list_patients(limit=20, offset=0, search=None):
        """List patients with pagination"""
        query = """
            SELECT patient_id, full_name, identification, identification_type,
                   email, phone, address, date_of_birth, gender, created_at
            FROM patients
            WHERE is_active = TRUE
        """
        params = []

        if search:
            query += """
                AND (full_name ILIKE %s OR identification ILIKE %s OR email ILIKE %s)
            """
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        query += " ORDER BY full_name LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            results = cursor.fetchall()
            # Transform all results to expected format
            transformed = []
            for result in results:
                result_dict = dict(result)
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', 'CEDULA')
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                transformed.append(result_dict)
            return transformed

    @staticmethod
    def count_patients(search=None):
        """Count patients"""
        query = "SELECT COUNT(*) as count FROM patients WHERE is_active = TRUE"
        params = []

        if search:
            query += """
                AND (full_name ILIKE %s OR identification ILIKE %s OR email ILIKE %s)
            """
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def create(doc_type, doc_number, first_name, last_name, email, phone, address, birth_date, gender,
               emergency_contact_name=None, emergency_contact_relation=None, emergency_contact_phone=None,
               occupation=None, medical_record_opening_date=None):
        """Create a new patient with emergency contact info and occupation"""
        # Combine first_name and last_name into full_name
        full_name = f"{first_name} {last_name}".strip()

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO patients (full_name, identification, identification_type, email, phone,
                                     address, date_of_birth, gender, is_active,
                                     emergency_contact_name, emergency_contact_relation, emergency_contact_phone,
                                     occupation, medical_record_opening_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, TRUE, %s, %s, %s, %s, %s)
                RETURNING patient_id, full_name, identification, identification_type,
                         email, phone, address, date_of_birth, gender, created_at,
                         emergency_contact_name, emergency_contact_relation, emergency_contact_phone,
                         occupation, medical_record_opening_date
            """, (full_name, doc_number, doc_type, email, phone, address, birth_date, gender,
                  emergency_contact_name, emergency_contact_relation, emergency_contact_phone,
                  occupation, medical_record_opening_date))
            result = cursor.fetchone()

            # Transform back to expected format for API compatibility
            if result:
                result_dict = dict(result)
                # Split full_name back to first_name and last_name
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', doc_type)
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                return result_dict
            return None

    @staticmethod
    def update(patient_id, **kwargs):
        """Update patient"""
        # Map old field names to new schema
        field_mapping = {
            'doc_number': 'identification',
            'doc_type': 'identification_type',
            'email': 'email',
            'phone': 'phone',
            'address': 'address',
            'birth_date': 'date_of_birth',
            'gender': 'gender'
        }

        updates = []
        params = []

        # Handle name fields - combine into full_name if either is provided
        if 'first_name' in kwargs or 'last_name' in kwargs:
            # Get current patient to preserve existing name parts
            with db.get_cursor() as cursor:
                cursor.execute("SELECT full_name FROM patients WHERE patient_id = %s", (patient_id,))
                current = cursor.fetchone()
                if current:
                    current_name_parts = current['full_name'].split(' ', 1)
                    first_name = kwargs.get('first_name', current_name_parts[0])
                    last_name = kwargs.get('last_name', current_name_parts[1] if len(current_name_parts) > 1 else '')
                    full_name = f"{first_name} {last_name}".strip()
                    updates.append("full_name = %s")
                    params.append(full_name)

        # Handle other fields
        for old_field, new_field in field_mapping.items():
            if old_field in kwargs and kwargs[old_field] is not None:
                updates.append(f"{new_field} = %s")
                params.append(kwargs[old_field])

        if not updates:
            return None

        params.append(patient_id)
        query = f"""
            UPDATE patients
            SET {', '.join(updates)}
            WHERE patient_id = %s
            RETURNING patient_id, full_name, identification, identification_type,
                     email, phone, address, date_of_birth, gender, created_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()

            # Transform back to expected format for API compatibility
            if result:
                result_dict = dict(result)
                # Split full_name back to first_name and last_name
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', 'CEDULA')
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                return result_dict
            return None

    @staticmethod
    def delete(patient_id):
        """Delete patient (soft delete by setting is_active to FALSE)"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE patients
                SET is_active = FALSE
                WHERE patient_id = %s
                RETURNING patient_id
            """, (patient_id,))
            result = cursor.fetchone()
            return result is not None

    @staticmethod
    def reactivate(patient_id):
        """Reactivate an inactive patient"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE patients
                SET is_active = TRUE
                WHERE patient_id = %s
                RETURNING patient_id, full_name, identification, identification_type,
                         email, phone, address, date_of_birth, gender, created_at, is_active
            """, (patient_id,))
            result = cursor.fetchone()

            if result:
                result_dict = dict(result)
                name_parts = result_dict['full_name'].split(' ', 1)
                result_dict['first_name'] = name_parts[0]
                result_dict['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
                result_dict['doc_number'] = result_dict['identification']
                result_dict['doc_type'] = result_dict.get('identification_type', 'CEDULA')
                result_dict['birth_date'] = format_date_for_api(result_dict['date_of_birth'])
                return result_dict
            return None

    @staticmethod
    def get_full_history(patient_id):
        """Get patient with all related data"""
        with db.get_cursor() as cursor:
            # Get patient data
            cursor.execute("""
                SELECT patient_id, full_name, identification, identification_type,
                       email, phone, address, date_of_birth, gender, created_at
                FROM patients
                WHERE patient_id = %s
            """, (patient_id,))
            patient_result = cursor.fetchone()

            if not patient_result:
                return None

            # Transform patient data to expected format
            patient = dict(patient_result)
            name_parts = patient['full_name'].split(' ', 1)
            patient['first_name'] = name_parts[0]
            patient['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
            patient['doc_number'] = patient['identification']
            patient['doc_type'] = patient.get('identification_type', 'CEDULA')
            patient['birth_date'] = format_date_for_api(patient['date_of_birth'])

            # Get medical history
            cursor.execute("""
                SELECT history_id, allergies, chronic_diseases,
                       surgeries, medications, family_history, created_at, updated_at
                FROM medical_history
                WHERE patient_id = %s
            """, (patient_id,))
            medical_history_result = cursor.fetchone()

            # Transform medical history to expected format
            medical_history = None
            if medical_history_result:
                medical_history = dict(medical_history_result)
                medical_history['pathologies'] = medical_history.get('chronic_diseases')
                medical_history['blood_type'] = None

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
                SELECT history_id, patient_id, allergies, chronic_diseases,
                       surgeries, medications, family_history, created_at, updated_at
                FROM medical_history
                WHERE patient_id = %s
            """, (patient_id,))
            result = cursor.fetchone()
            # Map to expected field names for API compatibility
            if result:
                result_dict = dict(result)
                result_dict['pathologies'] = result_dict.get('chronic_diseases')
                result_dict['blood_type'] = None  # Not stored in this table
                return result_dict
            return None

    @staticmethod
    def create(patient_id, allergies=None, pathologies=None, surgeries=None, family_history=None,
               blood_type=None, current_medications=None):
        """Create medical history with all medical fields"""
        # Map pathologies to chronic_diseases
        chronic_diseases = pathologies

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO medical_history (patient_id, allergies, chronic_diseases,
                                            surgeries, medications, family_history,
                                            blood_type, current_medications)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id)
                DO UPDATE SET
                    allergies = EXCLUDED.allergies,
                    chronic_diseases = EXCLUDED.chronic_diseases,
                    surgeries = EXCLUDED.surgeries,
                    medications = EXCLUDED.medications,
                    family_history = EXCLUDED.family_history,
                    blood_type = EXCLUDED.blood_type,
                    current_medications = EXCLUDED.current_medications,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING history_id, patient_id, allergies, chronic_diseases,
                         surgeries, medications, family_history, blood_type,
                         current_medications, created_at, updated_at
            """, (patient_id, allergies, chronic_diseases, surgeries, None, family_history,
                  blood_type, current_medications))
            result = cursor.fetchone()
            if result:
                result_dict = dict(result)
                result_dict['pathologies'] = result_dict.get('chronic_diseases')
                return result_dict
            return None

    @staticmethod
    def update(patient_id, **kwargs):
        """Update medical history"""
        # Map old field names to new schema
        field_mapping = {
            'allergies': 'allergies',
            'pathologies': 'chronic_diseases',
            'surgeries': 'surgeries',
            'medications': 'medications',
            'family_history': 'family_history'
        }

        updates = []
        params = []

        for old_field, new_field in field_mapping.items():
            if old_field in kwargs and kwargs[old_field] is not None:
                updates.append(f"{new_field} = %s")
                params.append(kwargs[old_field])

        if not updates:
            return None

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(patient_id)

        query = f"""
            UPDATE medical_history
            SET {', '.join(updates)}
            WHERE patient_id = %s
            RETURNING history_id, patient_id, allergies, chronic_diseases,
                     surgeries, medications, family_history, created_at, updated_at
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            if result:
                result_dict = dict(result)
                result_dict['pathologies'] = result_dict.get('chronic_diseases')
                result_dict['blood_type'] = kwargs.get('blood_type')
                return result_dict
            return None

    @staticmethod
    def upsert(patient_id, allergies=None, pathologies=None, surgeries=None, family_history=None,
               blood_type=None, current_medications=None, personal_pathological_history=None,
               personal_pathological_nr=False, family_pathological_history=None,
               family_pathological_nr=False, previous_procedures=None):
        """Create or update medical history with new capilar clinic fields"""
        chronic_diseases = pathologies

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO medical_history (patient_id, allergies, chronic_diseases,
                                            surgeries, medications, family_history,
                                            blood_type, current_medications,
                                            personal_pathological_history, personal_pathological_nr,
                                            family_pathological_history, family_pathological_nr,
                                            previous_procedures)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (patient_id)
                DO UPDATE SET
                    allergies = EXCLUDED.allergies,
                    chronic_diseases = EXCLUDED.chronic_diseases,
                    surgeries = EXCLUDED.surgeries,
                    medications = EXCLUDED.medications,
                    family_history = EXCLUDED.family_history,
                    blood_type = EXCLUDED.blood_type,
                    current_medications = EXCLUDED.current_medications,
                    personal_pathological_history = EXCLUDED.personal_pathological_history,
                    personal_pathological_nr = EXCLUDED.personal_pathological_nr,
                    family_pathological_history = EXCLUDED.family_pathological_history,
                    family_pathological_nr = EXCLUDED.family_pathological_nr,
                    previous_procedures = EXCLUDED.previous_procedures,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING history_id, patient_id, allergies, chronic_diseases,
                         surgeries, medications, family_history, blood_type,
                         current_medications, personal_pathological_history, personal_pathological_nr,
                         family_pathological_history, family_pathological_nr, previous_procedures,
                         created_at, updated_at
            """, (patient_id, allergies, chronic_diseases, surgeries, None, family_history,
                  blood_type, current_medications, personal_pathological_history, personal_pathological_nr,
                  family_pathological_history, family_pathological_nr,
                  previous_procedures if previous_procedures else None))
            result = cursor.fetchone()
            if result:
                result_dict = dict(result)
                result_dict['pathologies'] = result_dict.get('chronic_diseases')
                return result_dict
            return None


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
                       p.full_name as patient_name
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
