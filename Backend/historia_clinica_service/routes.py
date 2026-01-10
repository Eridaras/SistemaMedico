"""
Routes for Historia Clinica Service
"""
from flask import Blueprint, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import (success_response, error_response, get_pagination_params,
                         validate_email, validate_cedula, validate_ruc)
from common.database import db
from models import PatientModel, MedicalHistoryModel, ClinicalNoteModel

historia_clinica_bp = Blueprint('historia_clinica', __name__)


# ============= PATIENTS ENDPOINTS =============

@historia_clinica_bp.route('/patients', methods=['GET'])
@token_required
def list_patients(current_user):
    """List all patients"""
    try:
        pagination = get_pagination_params(request)
        search = request.args.get('search')

        patients = PatientModel.list_patients(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            search=search
        )

        total = PatientModel.count_patients(search=search)

        response_data = {
            'patients': patients,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List patients error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/search', methods=['GET'])
@token_required
def search_patient(current_user):
    """Search patient by document number"""
    try:
        doc_number = request.args.get('doc_number')

        if not doc_number:
            return error_response('doc_number parameter is required', 400)

        patient = PatientModel.get_by_doc_number(doc_number)

        if not patient:
            return success_response({'patient': None}, 'Patient not found')

        return success_response({'patient': patient})

    except Exception as e:
        print(f"Search patient error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>', methods=['GET'])
@token_required
def get_patient(current_user, patient_id):
    """Get patient by ID with full history"""
    try:
        patient_data = PatientModel.get_full_history(patient_id)

        if not patient_data:
            return error_response('Patient not found', 404)

        return success_response(patient_data)

    except Exception as e:
        print(f"Get patient error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients', methods=['POST'])
@token_required
def create_patient(current_user):
    """Create new patient"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['doc_type', 'doc_number', 'first_name', 'last_name']
        for field in required_fields:
            if field not in data or not data[field]:
                return error_response(f'{field} is required', 400)

        # Validate document number based on type
        doc_type = data['doc_type']
        doc_number = data['doc_number']

        if doc_type == 'CEDULA' and not validate_cedula(doc_number):
            return error_response('Invalid cedula format (must be 10 digits)', 400)
        elif doc_type == 'RUC' and not validate_ruc(doc_number):
            return error_response('Invalid RUC format (must be 13 digits)', 400)

        # Validate email if provided
        if data.get('email') and not validate_email(data['email']):
            return error_response('Invalid email format', 400)

        # Check if patient already exists
        existing = PatientModel.get_by_doc_number(doc_number)
        if existing:
            # Si el paciente existe pero está inactivo, retornar código 410 con datos
            if not existing.get('is_active', True):
                return error_response('Patient with this document number exists but is inactive', 410, {
                    'patient_id': existing.get('patient_id'),
                    'full_name': f"{existing.get('first_name', '')} {existing.get('last_name', '')}".strip(),
                    'doc_number': existing.get('doc_number')
                })
            # Si está activo, retornar error 409
            return error_response('Patient with this document number already exists', 409)

        # Create patient
        patient = PatientModel.create(
            doc_type=data['doc_type'],
            doc_number=data['doc_number'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            birth_date=data.get('birth_date'),
            gender=data.get('gender'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_relation=data.get('emergency_contact_relation'),
            emergency_contact_phone=data.get('emergency_contact_phone'),
            occupation=data.get('occupation'),
            medical_record_opening_date=data.get('medical_record_opening_date')
        )

        return success_response({'patient': patient}, 'Patient created successfully', 201)

    except Exception as e:
        print(f"Create patient error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>', methods=['PUT'])
@token_required
def update_patient(current_user, patient_id):
    """Update patient"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # IMPORTANT: Remove doc_number and doc_type from update data
        # These are immutable fields that should never be changed after creation
        immutable_fields = ['doc_number', 'doc_type']
        for field in immutable_fields:
            if field in data:
                del data[field]

        # Validate email if provided
        if data.get('email') and not validate_email(data['email']):
            return error_response('Invalid email format', 400)

        patient = PatientModel.update(patient_id, **data)

        if not patient:
            return error_response('Patient not found', 404)

        return success_response({'patient': patient}, 'Patient updated successfully')

    except Exception as e:
        print(f"Update patient error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
@token_required
def delete_patient(current_user, patient_id):
    """Delete patient"""
    try:
        # Check if patient exists
        patient = PatientModel.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)

        # Delete patient (cascade will handle related records)
        PatientModel.delete(patient_id)

        return success_response(None, 'Patient deleted successfully')

    except Exception as e:
        print(f"Delete patient error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>/reactivate', methods=['POST'])
@token_required
def reactivate_patient(current_user, patient_id):
    """Reactivate an inactive patient"""
    try:
        # Reactivate patient
        patient = PatientModel.reactivate(patient_id)

        if not patient:
            return error_response('Patient not found', 404)

        return success_response({'patient': patient}, 'Patient reactivated successfully')

    except Exception as e:
        print(f"Reactivate patient error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= MEDICAL HISTORY ENDPOINTS =============

@historia_clinica_bp.route('/patients/<int:patient_id>/medical-history', methods=['GET'])
@token_required
def get_medical_history(current_user, patient_id):
    """Get patient medical history"""
    try:
        history = MedicalHistoryModel.get_by_patient_id(patient_id)

        if not history:
            return success_response({'medical_history': None, 'message': 'No medical history found'})

        return success_response({'medical_history': history})

    except Exception as e:
        print(f"Get medical history error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>/medical-history', methods=['POST'])
@token_required
def create_or_update_medical_history(current_user, patient_id):
    """Create or update patient medical history"""
    try:
        data = request.get_json()

        # Verify patient exists
        patient = PatientModel.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)

        # Upsert medical history
        history = MedicalHistoryModel.upsert(
            patient_id=patient_id,
            allergies=data.get('allergies'),
            pathologies=data.get('pathologies'),
            surgeries=data.get('surgeries'),
            family_history=data.get('family_history'),
            blood_type=data.get('blood_type'),
            current_medications=data.get('current_medications'),
            personal_pathological_history=data.get('personal_pathological_history'),
            personal_pathological_nr=data.get('personal_pathological_nr', False),
            family_pathological_history=data.get('family_pathological_history'),
            family_pathological_nr=data.get('family_pathological_nr', False),
            previous_procedures=data.get('previous_procedures')
        )

        return success_response({'medical_history': history}, 'Medical history saved successfully')

    except Exception as e:
        print(f"Create/update medical history error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/patients/<int:patient_id>/medical-history', methods=['PUT'])
@token_required
def update_medical_history(current_user, patient_id):
    """Update patient medical history"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        history = MedicalHistoryModel.update(patient_id, **data)

        if not history:
            return error_response('Medical history not found', 404)

        return success_response({'medical_history': history}, 'Medical history updated successfully')

    except Exception as e:
        print(f"Update medical history error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= CLINICAL RECORDS ENDPOINTS (Motivo de Consulta y Examen Físico) =============

@historia_clinica_bp.route('/clinical-records', methods=['POST'])
@token_required
def create_clinical_record(current_user):
    """Create a clinical record for a patient"""
    try:
        data = request.get_json()

        # Validate required fields
        if 'patient_id' not in data:
            return error_response('patient_id is required', 400)

        # Insert clinical record
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO clinical_records (patient_id, appointment_id, motivo_consulta, enfermedad_actual, examen_fisico)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING record_id, patient_id, appointment_id, motivo_consulta, enfermedad_actual, examen_fisico, created_at
            """, (data['patient_id'], data.get('appointment_id'), data.get('motivo_consulta'),
                  data.get('enfermedad_actual'), data.get('examen_fisico')))
            result = cursor.fetchone()

            if result:
                return success_response({'clinical_record': dict(result)}, 'Clinical record created successfully', 201)

        return error_response('Failed to create clinical record', 500)

    except Exception as e:
        print(f"Create clinical record error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= PATIENT PHOTOS ENDPOINTS =============

@historia_clinica_bp.route('/patients/<int:patient_id>/photos', methods=['POST'])
@token_required
def upload_patient_photos(current_user, patient_id):
    """Upload photos for a patient"""
    try:
        import os
        from werkzeug.utils import secure_filename

        # Verificar que el paciente existe
        patient = PatientModel.get_by_id(patient_id)
        if not patient:
            return error_response('Patient not found', 404)

        # Obtener parámetros
        session_number = request.form.get('session_number', 1)
        appointment_id = request.form.get('appointment_id')

        # Crear directorio de almacenamiento local si no existe
        upload_folder = os.path.join('/home/app/uploads/patient_photos', str(patient_id), f'session_{session_number}')
        os.makedirs(upload_folder, exist_ok=True)

        uploaded_photos = []
        files = request.files.getlist('photos')

        for index, file in enumerate(files[:5], start=1):  # Máximo 5 fotos
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, f'photo_{index}_{filename}')
                file.save(file_path)

                # Guardar registro en base de datos
                with db.get_cursor(commit=True) as cursor:
                    cursor.execute("""
                        INSERT INTO patient_photos (patient_id, appointment_id, session_number, photo_url,
                                                   photo_order, file_size, original_filename)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING photo_id, patient_id, session_number, photo_url, photo_order, created_at
                    """, (patient_id, appointment_id, session_number, file_path, index,
                          os.path.getsize(file_path), filename))
                    result = cursor.fetchone()
                    if result:
                        uploaded_photos.append(dict(result))

        return success_response({
            'uploaded_count': len(uploaded_photos),
            'photos': uploaded_photos
        }, 'Photos uploaded successfully', 201)

    except Exception as e:
        print(f"Upload photos error: {str(e)}")
        return error_response(f'An error occurred: {str(e)}', 500)


# ============= HAIR TREATMENTS ENDPOINTS =============

@historia_clinica_bp.route('/treatments', methods=['GET'])
@token_required
def list_treatments(current_user):
    """List all hair treatments"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT hair_treatment_id, name, description, duration, number_of_sessions,
                       price, is_active, created_at, updated_at
                FROM hair_treatments
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            treatments = [dict(row) for row in results]

        return success_response({'treatments': treatments})

    except Exception as e:
        print(f"List treatments error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/treatments/<int:treatment_id>', methods=['GET'])
@token_required
def get_treatment(current_user, treatment_id):
    """Get treatment by ID"""
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT hair_treatment_id, name, description, duration, number_of_sessions,
                       price, inventory_items, is_active, created_at, updated_at
                FROM hair_treatments
                WHERE hair_treatment_id = %s
            """, (treatment_id,))
            result = cursor.fetchone()

            if not result:
                return error_response('Treatment not found', 404)

            return success_response({'treatment': dict(result)})

    except Exception as e:
        print(f"Get treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/treatments', methods=['POST'])
@token_required
def create_treatment(current_user):
    """Create new hair treatment"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'duration', 'number_of_sessions', 'price']
        for field in required_fields:
            if field not in data or (isinstance(data[field], str) and not data[field]):
                return error_response(f'{field} is required', 400)

        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO hair_treatments (name, description, duration, number_of_sessions, price, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING hair_treatment_id, name, description, duration, number_of_sessions,
                         price, is_active, created_at
            """, (data['name'], data.get('description'), data['duration'],
                  data['number_of_sessions'], data['price'], data.get('is_active', True)))
            result = cursor.fetchone()

            if result:
                return success_response({'treatment': dict(result)}, 'Treatment created successfully', 201)

        return error_response('Failed to create treatment', 500)

    except Exception as e:
        print(f"Create treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/treatments/<int:treatment_id>', methods=['PUT'])
@token_required
def update_treatment(current_user, treatment_id):
    """Update hair treatment"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # Build update query dynamically
        update_fields = []
        values = []

        for field in ['name', 'description', 'duration', 'number_of_sessions', 'price', 'is_active']:
            if field in data:
                update_fields.append(f"{field} = %s")
                values.append(data[field])

        if not update_fields:
            return error_response('No valid fields to update', 400)

        values.append(treatment_id)

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(f"""
                UPDATE hair_treatments
                SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE hair_treatment_id = %s
                RETURNING hair_treatment_id, name, description, duration, number_of_sessions,
                         price, is_active, updated_at
            """, values)
            result = cursor.fetchone()

            if not result:
                return error_response('Treatment not found', 404)

            return success_response({'treatment': dict(result)}, 'Treatment updated successfully')

    except Exception as e:
        print(f"Update treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/treatments/<int:treatment_id>', methods=['DELETE'])
@token_required
def delete_treatment(current_user, treatment_id):
    """Delete hair treatment"""
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM hair_treatments
                WHERE hair_treatment_id = %s
                RETURNING hair_treatment_id
            """, (treatment_id,))
            result = cursor.fetchone()

            if not result:
                return error_response('Treatment not found', 404)

            return success_response({'treatment_id': result['hair_treatment_id']}, 'Treatment deleted successfully')

    except Exception as e:
        print(f"Delete treatment error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= CLINICAL NOTES ENDPOINTS =============

@historia_clinica_bp.route('/patients/<int:patient_id>/notes', methods=['GET'])
@token_required
def get_patient_notes(current_user, patient_id):
    """Get all clinical notes for a patient"""
    try:
        pagination = get_pagination_params(request)

        notes = ClinicalNoteModel.get_by_patient_id(
            patient_id,
            limit=pagination['per_page'],
            offset=pagination['offset']
        )

        return success_response({'notes': notes})

    except Exception as e:
        print(f"Get patient notes error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/notes/<int:note_id>', methods=['GET'])
@token_required
def get_note(current_user, note_id):
    """Get clinical note by ID"""
    try:
        note = ClinicalNoteModel.get_by_id(note_id)

        if not note:
            return error_response('Note not found', 404)

        return success_response({'note': note})

    except Exception as e:
        print(f"Get note error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/appointments/<int:appointment_id>/notes', methods=['GET'])
@token_required
def get_appointment_notes(current_user, appointment_id):
    """Get all notes for an appointment"""
    try:
        notes = ClinicalNoteModel.get_by_appointment_id(appointment_id)
        return success_response({'notes': notes})

    except Exception as e:
        print(f"Get appointment notes error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/appointments/<int:appointment_id>/notes', methods=['POST'])
@token_required
def create_note(current_user, appointment_id):
    """Create clinical note"""
    try:
        data = request.get_json()

        if 'observations' not in data or not data['observations']:
            return error_response('observations is required', 400)

        note = ClinicalNoteModel.create(
            appointment_id=appointment_id,
            observations=data['observations'],
            diagnosis=data.get('diagnosis')
        )

        return success_response({'note': note}, 'Clinical note created successfully', 201)

    except Exception as e:
        print(f"Create note error: {str(e)}")
        return error_response('An error occurred', 500)


@historia_clinica_bp.route('/notes/<int:note_id>', methods=['PUT'])
@token_required
def update_note(current_user, note_id):
    """Update clinical note"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        note = ClinicalNoteModel.update(
            note_id,
            observations=data.get('observations'),
            diagnosis=data.get('diagnosis')
        )

        if not note:
            return error_response('Note not found', 404)

        return success_response({'note': note}, 'Clinical note updated successfully')

    except Exception as e:
        print(f"Update note error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= SEARCH ENDPOINTS =============

@historia_clinica_bp.route('/patients/search', methods=['GET'])
@token_required
def search_patients(current_user):
    """Search patients by document number"""
    try:
        doc_number = request.args.get('doc_number')

        if not doc_number:
            return error_response('doc_number parameter is required', 400)

        patient = PatientModel.get_by_doc_number(doc_number)

        if not patient:
            return error_response('Patient not found', 404)

        return success_response({'patient': patient})

    except Exception as e:
        print(f"Search patient error: {str(e)}")
        return error_response('An error occurred', 500)


# Health check
@historia_clinica_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'historia_clinica'})
