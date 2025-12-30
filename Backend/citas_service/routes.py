"""
Routes for Citas Service
"""
from flask import Blueprint, request
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response, get_pagination_params
from models import AppointmentModel, AppointmentTreatmentModel, AppointmentExtraModel

citas_bp = Blueprint('citas', __name__)


# ============= APPOINTMENTS ENDPOINTS =============

@citas_bp.route('/appointments', methods=['GET'])
@token_required
def list_appointments(current_user):
    """List all appointments"""
    try:
        pagination = get_pagination_params(request)
        patient_id = request.args.get('patient_id', type=int)
        doctor_id = request.args.get('doctor_id', type=int)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        appointments = AppointmentModel.list_appointments(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            patient_id=patient_id,
            doctor_id=doctor_id,
            status=status,
            date_from=date_from,
            date_to=date_to
        )

        total = AppointmentModel.count_appointments(
            patient_id=patient_id,
            doctor_id=doctor_id,
            status=status,
            date_from=date_from,
            date_to=date_to
        )

        response_data = {
            'appointments': appointments,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List appointments error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/<int:appointment_id>', methods=['GET'])
@token_required
def get_appointment(current_user, appointment_id):
    """Get appointment by ID with all details"""
    try:
        appointment = AppointmentModel.get_by_id(appointment_id)

        if not appointment:
            return error_response('Appointment not found', 404)

        # Get treatments and extras
        treatments = AppointmentTreatmentModel.get_by_appointment_id(appointment_id)
        extras = AppointmentExtraModel.get_by_appointment_id(appointment_id)

        # Calculate totals
        treatments_total = AppointmentTreatmentModel.calculate_total(appointment_id)
        extras_total = AppointmentExtraModel.calculate_total(appointment_id)
        total = treatments_total + extras_total

        appointment['treatments'] = treatments
        appointment['extras'] = extras
        appointment['treatments_total'] = treatments_total
        appointment['extras_total'] = extras_total
        appointment['total'] = total

        return success_response({'appointment': appointment})

    except Exception as e:
        print(f"Get appointment error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments', methods=['POST'])
@token_required
def create_appointment(current_user):
    """Create new appointment"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['patient_id', 'doctor_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        # Parse datetime
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except ValueError:
            return error_response('Invalid datetime format', 400)

        # Validate time range
        if start_time >= end_time:
            return error_response('end_time must be after start_time', 400)

        # Check doctor availability
        is_available = AppointmentModel.check_availability(
            data['doctor_id'],
            start_time,
            end_time
        )

        if not is_available:
            return error_response('Doctor is not available at this time', 409)

        # Create appointment
        appointment = AppointmentModel.create(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            start_time=start_time,
            end_time=end_time,
            reason=data.get('reason'),
            status=data.get('status', 'PENDING')
        )

        # Sync to Google Calendar if enabled (background task, don't block response)
        try:
            from common.google_calendar import CalendarSyncManager
            CalendarSyncManager.sync_appointment_create(
                appointment['appointment_id'],
                data['doctor_id']
            )
        except Exception as e:
            print(f"Google Calendar sync warning: {str(e)}")
            # Don't fail the request if calendar sync fails

        return success_response({'appointment': appointment}, 'Appointment created successfully', 201)

    except Exception as e:
        print(f"Create appointment error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/<int:appointment_id>', methods=['PUT'])
@token_required
def update_appointment(current_user, appointment_id):
    """Update appointment"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # If updating time, check availability
        if 'start_time' in data or 'end_time' in data or 'doctor_id' in data:
            current_appointment = AppointmentModel.get_by_id(appointment_id)
            if not current_appointment:
                return error_response('Appointment not found', 404)

            # Parse new times
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            doctor_id = data.get('doctor_id', current_appointment['doctor_id'])

            if start_time:
                start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start_time = current_appointment['start_time']

            if end_time:
                end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            else:
                end_time = current_appointment['end_time']

            # Check availability
            is_available = AppointmentModel.check_availability(
                doctor_id,
                start_time,
                end_time,
                exclude_appointment_id=appointment_id
            )

            if not is_available:
                return error_response('Doctor is not available at this time', 409)

        appointment = AppointmentModel.update(appointment_id, **data)

        if not appointment:
            return error_response('Appointment not found', 404)

        return success_response({'appointment': appointment}, 'Appointment updated successfully')

    except Exception as e:
        print(f"Update appointment error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/<int:appointment_id>/status', methods=['PATCH'])
@token_required
def update_appointment_status(current_user, appointment_id):
    """Update appointment status"""
    try:
        data = request.get_json()

        if 'status' not in data:
            return error_response('status is required', 400)

        valid_statuses = ['PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED']
        if data['status'] not in valid_statuses:
            return error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)

        result = AppointmentModel.update_status(appointment_id, data['status'])

        if not result:
            return error_response('Appointment not found', 404)

        return success_response({'appointment': result}, 'Appointment status updated successfully')

    except Exception as e:
        print(f"Update appointment status error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/check-availability', methods=['POST'])
@token_required
def check_availability(current_user):
    """Check doctor availability"""
    try:
        data = request.get_json()

        required_fields = ['doctor_id', 'start_time', 'end_time']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))

        is_available = AppointmentModel.check_availability(
            data['doctor_id'],
            start_time,
            end_time,
            exclude_appointment_id=data.get('exclude_appointment_id')
        )

        return success_response({'available': is_available})

    except Exception as e:
        print(f"Check availability error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/doctors/<int:doctor_id>/schedule', methods=['GET'])
@token_required
def get_doctor_schedule(current_user, doctor_id):
    """Get doctor schedule for a specific date"""
    try:
        date = request.args.get('date')

        if not date:
            return error_response('date parameter is required', 400)

        schedule = AppointmentModel.get_doctor_schedule(doctor_id, date)

        return success_response({'schedule': schedule, 'date': date, 'doctor_id': doctor_id})

    except Exception as e:
        print(f"Get doctor schedule error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= APPOINTMENT TREATMENTS ENDPOINTS =============

@citas_bp.route('/appointments/<int:appointment_id>/treatments', methods=['GET'])
@token_required
def get_appointment_treatments(current_user, appointment_id):
    """Get all treatments for an appointment"""
    try:
        treatments = AppointmentTreatmentModel.get_by_appointment_id(appointment_id)
        total = AppointmentTreatmentModel.calculate_total(appointment_id)

        return success_response({'treatments': treatments, 'total': total})

    except Exception as e:
        print(f"Get appointment treatments error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/<int:appointment_id>/treatments', methods=['POST'])
@token_required
def add_treatment(current_user, appointment_id):
    """Add treatment to appointment"""
    try:
        data = request.get_json()

        required_fields = ['treatment_id', 'price_at_moment']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        treatment = AppointmentTreatmentModel.add_treatment(
            appointment_id,
            data['treatment_id'],
            data['price_at_moment'],
            data.get('quantity', 1)
        )

        return success_response({'treatment': treatment}, 'Treatment added successfully', 201)

    except Exception as e:
        print(f"Add treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/treatments/<int:detail_id>', methods=['PUT'])
@token_required
def update_treatment(current_user, detail_id):
    """Update treatment in appointment"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        treatment = AppointmentTreatmentModel.update_treatment(
            detail_id,
            price_at_moment=data.get('price_at_moment'),
            quantity=data.get('quantity')
        )

        if not treatment:
            return error_response('Treatment not found', 404)

        return success_response({'treatment': treatment}, 'Treatment updated successfully')

    except Exception as e:
        print(f"Update treatment error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/treatments/<int:detail_id>', methods=['DELETE'])
@token_required
def remove_treatment(current_user, detail_id):
    """Remove treatment from appointment"""
    try:
        result = AppointmentTreatmentModel.remove_treatment(detail_id)

        if not result:
            return error_response('Treatment not found', 404)

        return success_response(message='Treatment removed successfully')

    except Exception as e:
        print(f"Remove treatment error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= APPOINTMENT EXTRAS ENDPOINTS =============

@citas_bp.route('/appointments/<int:appointment_id>/extras', methods=['GET'])
@token_required
def get_appointment_extras(current_user, appointment_id):
    """Get all extra products for an appointment"""
    try:
        extras = AppointmentExtraModel.get_by_appointment_id(appointment_id)
        total = AppointmentExtraModel.calculate_total(appointment_id)

        return success_response({'extras': extras, 'total': total})

    except Exception as e:
        print(f"Get appointment extras error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/<int:appointment_id>/extras', methods=['POST'])
@token_required
def add_extra(current_user, appointment_id):
    """Add extra product to appointment"""
    try:
        data = request.get_json()

        required_fields = ['product_id', 'quantity']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        extra = AppointmentExtraModel.add_extra(
            appointment_id,
            data['product_id'],
            data['quantity'],
            data.get('price_charged', 0)
        )

        return success_response({'extra': extra}, 'Extra product added successfully', 201)

    except Exception as e:
        print(f"Add extra error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/extras/<int:extra_id>', methods=['PUT'])
@token_required
def update_extra(current_user, extra_id):
    """Update extra product in appointment"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        extra = AppointmentExtraModel.update_extra(
            extra_id,
            quantity=data.get('quantity'),
            price_charged=data.get('price_charged')
        )

        if not extra:
            return error_response('Extra not found', 404)

        return success_response({'extra': extra}, 'Extra updated successfully')

    except Exception as e:
        print(f"Update extra error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/extras/<int:extra_id>', methods=['DELETE'])
@token_required
def remove_extra(current_user, extra_id):
    """Remove extra product from appointment"""
    try:
        result = AppointmentExtraModel.remove_extra(extra_id)

        if not result:
            return error_response('Extra not found', 404)

        return success_response(message='Extra removed successfully')

    except Exception as e:
        print(f"Remove extra error: {str(e)}")
        return error_response('An error occurred', 500)


@citas_bp.route('/appointments/today', methods=['GET'])
@token_required
def get_today_appointments(current_user):
    """Get appointments for today"""
    try:
        from datetime import date
        today = date.today()

        date_from = today.strftime('%Y-%m-%d')
        date_to = today.strftime('%Y-%m-%d')

        appointments = AppointmentModel.list_appointments(
            date_from=date_from,
            date_to=date_to
        )

        return success_response({
            'appointments': appointments,
            'count': len(appointments),
            'date': today.isoformat()
        })

    except Exception as e:
        print(f"Get today appointments error: {str(e)}")
        return error_response('An error occurred', 500)


# Health check
@citas_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'citas'})
