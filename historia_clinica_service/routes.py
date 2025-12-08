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
from historia_clinica_service.models import PatientModel, MedicalHistoryModel, ClinicalNoteModel

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
            gender=data.get('gender')
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

        # Validate email if provided
        if data.get('email') and not validate_email(data['email']):
            return error_response('Invalid email format', 400)

        # Validate document if being updated
        if 'doc_type' in data and 'doc_number' in data:
            doc_type = data['doc_type']
            doc_number = data['doc_number']

            if doc_type == 'CEDULA' and not validate_cedula(doc_number):
                return error_response('Invalid cedula format (must be 10 digits)', 400)
            elif doc_type == 'RUC' and not validate_ruc(doc_number):
                return error_response('Invalid RUC format (must be 13 digits)', 400)

        patient = PatientModel.update(patient_id, **data)

        if not patient:
            return error_response('Patient not found', 404)

        return success_response({'patient': patient}, 'Patient updated successfully')

    except Exception as e:
        print(f"Update patient error: {str(e)}")
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
            blood_type=data.get('blood_type')
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
