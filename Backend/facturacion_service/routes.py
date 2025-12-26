"""
Routes for Facturacion Service
"""
from flask import Blueprint, request
from datetime import date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response, get_pagination_params, calculate_iva
from facturacion_service.models import InvoiceModel, OperationalExpenseModel, FinancialReportModel

facturacion_bp = Blueprint('facturacion', __name__)


# ============= INVOICES ENDPOINTS =============

@facturacion_bp.route('/invoices', methods=['GET'])
@token_required
def list_invoices(current_user):
    """List all invoices"""
    try:
        pagination = get_pagination_params(request)
        status = request.args.get('status')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        invoices = InvoiceModel.list_invoices(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            status=status,
            date_from=date_from,
            date_to=date_to
        )

        total = InvoiceModel.count_invoices(status=status, date_from=date_from, date_to=date_to)

        response_data = {
            'invoices': invoices,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List invoices error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/invoices/<int:invoice_id>', methods=['GET'])
@token_required
def get_invoice(current_user, invoice_id):
    """Get invoice by ID"""
    try:
        invoice = InvoiceModel.get_by_id(invoice_id)

        if not invoice:
            return error_response('Invoice not found', 404)

        return success_response({'invoice': invoice})

    except Exception as e:
        print(f"Get invoice error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/invoices', methods=['POST'])
@token_required
def create_invoice(current_user):
    """Create new invoice"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['patient_id', 'subtotal']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        # Calculate IVA
        subtotal = float(data['subtotal'])
        iva_rate = float(data.get('iva_rate', 15.0))
        iva_amount = calculate_iva(subtotal, iva_rate)
        total_amount = subtotal + iva_amount

        # Get next invoice number if not provided
        invoice_number = data.get('invoice_number')
        if not invoice_number and data.get('status') != 'DRAFT':
            invoice_number = InvoiceModel.get_next_invoice_number()

        # Create invoice
        invoice = InvoiceModel.create(
            patient_id=data['patient_id'],
            appointment_id=data.get('appointment_id'),
            invoice_number=invoice_number,
            issue_date=data.get('issue_date', date.today()),
            subtotal=subtotal,
            iva_rate=iva_rate,
            iva_amount=iva_amount,
            total_amount=total_amount,
            status=data.get('status', 'DRAFT')
        )

        return success_response({'invoice': invoice}, 'Invoice created successfully', 201)

    except Exception as e:
        print(f"Create invoice error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/invoices/<int:invoice_id>', methods=['PUT'])
@token_required
def update_invoice(current_user, invoice_id):
    """Update invoice"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        # Recalculate totals if subtotal or iva_rate changed
        if 'subtotal' in data or 'iva_rate' in data:
            # Get current invoice
            current_invoice = InvoiceModel.get_by_id(invoice_id)
            if not current_invoice:
                return error_response('Invoice not found', 404)

            subtotal = float(data.get('subtotal', current_invoice['subtotal']))
            iva_rate = float(data.get('iva_rate', current_invoice['iva_rate']))

            data['iva_amount'] = calculate_iva(subtotal, iva_rate)
            data['total_amount'] = subtotal + data['iva_amount']

        invoice = InvoiceModel.update(invoice_id, **data)

        if not invoice:
            return error_response('Invoice not found', 404)

        return success_response({'invoice': invoice}, 'Invoice updated successfully')

    except Exception as e:
        print(f"Update invoice error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/invoices/<int:invoice_id>/status', methods=['PATCH'])
@token_required
def update_invoice_status(current_user, invoice_id):
    """Update invoice status"""
    try:
        data = request.get_json()

        if 'status' not in data:
            return error_response('status is required', 400)

        valid_statuses = ['DRAFT', 'ISSUED', 'PAID', 'ANNULLED']
        if data['status'] not in valid_statuses:
            return error_response(f'Invalid status. Must be one of: {", ".join(valid_statuses)}', 400)

        # If changing to ISSUED and no invoice number, generate one
        if data['status'] == 'ISSUED':
            invoice = InvoiceModel.get_by_id(invoice_id)
            if not invoice:
                return error_response('Invoice not found', 404)

            if not invoice.get('invoice_number'):
                invoice_number = InvoiceModel.get_next_invoice_number()
                InvoiceModel.update(invoice_id, invoice_number=invoice_number)

        result = InvoiceModel.update_status(invoice_id, data['status'])

        if not result:
            return error_response('Invoice not found', 404)

        return success_response({'invoice': result}, 'Invoice status updated successfully')

    except Exception as e:
        print(f"Update invoice status error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/invoices/totals', methods=['GET'])
@token_required
def get_invoice_totals(current_user):
    """Get invoice totals by period"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        totals = InvoiceModel.get_totals_by_period(date_from, date_to)

        return success_response({'totals': totals})

    except Exception as e:
        print(f"Get invoice totals error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= OPERATIONAL EXPENSES ENDPOINTS =============

@facturacion_bp.route('/expenses', methods=['GET'])
@token_required
def list_expenses(current_user):
    """List all expenses"""
    try:
        pagination = get_pagination_params(request)
        category = request.args.get('category')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        expenses = OperationalExpenseModel.list_expenses(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            category=category,
            date_from=date_from,
            date_to=date_to
        )

        total = OperationalExpenseModel.count_expenses(category=category, date_from=date_from, date_to=date_to)

        response_data = {
            'expenses': expenses,
            'pagination': {
                'page': pagination['page'],
                'per_page': pagination['per_page'],
                'total': total,
                'pages': (total + pagination['per_page'] - 1) // pagination['per_page']
            }
        }

        return success_response(response_data)

    except Exception as e:
        print(f"List expenses error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses/<int:expense_id>', methods=['GET'])
@token_required
def get_expense(current_user, expense_id):
    """Get expense by ID"""
    try:
        expense = OperationalExpenseModel.get_by_id(expense_id)

        if not expense:
            return error_response('Expense not found', 404)

        return success_response({'expense': expense})

    except Exception as e:
        print(f"Get expense error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses', methods=['POST'])
@token_required
def create_expense(current_user):
    """Create new expense"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['description', 'amount']
        for field in required_fields:
            if field not in data:
                return error_response(f'{field} is required', 400)

        expense = OperationalExpenseModel.create(
            description=data['description'],
            amount=data['amount'],
            expense_date=data.get('expense_date', date.today()),
            category=data.get('category'),
            registered_by=current_user['user_id']
        )

        return success_response({'expense': expense}, 'Expense created successfully', 201)

    except Exception as e:
        print(f"Create expense error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses/<int:expense_id>', methods=['PUT'])
@token_required
def update_expense(current_user, expense_id):
    """Update expense"""
    try:
        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        expense = OperationalExpenseModel.update(expense_id, **data)

        if not expense:
            return error_response('Expense not found', 404)

        return success_response({'expense': expense}, 'Expense updated successfully')

    except Exception as e:
        print(f"Update expense error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(current_user, expense_id):
    """Delete expense"""
    try:
        result = OperationalExpenseModel.delete(expense_id)

        if not result:
            return error_response('Expense not found', 404)

        return success_response(message='Expense deleted successfully')

    except Exception as e:
        print(f"Delete expense error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses/categories', methods=['GET'])
@token_required
def get_expense_categories(current_user):
    """Get all expense categories"""
    try:
        categories = OperationalExpenseModel.get_categories()
        return success_response({'categories': categories})

    except Exception as e:
        print(f"Get expense categories error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/expenses/totals', methods=['GET'])
@token_required
def get_expense_totals(current_user):
    """Get expense totals by period"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        totals = OperationalExpenseModel.get_totals_by_period(date_from, date_to)

        return success_response({'totals': totals})

    except Exception as e:
        print(f"Get expense totals error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= FINANCIAL REPORTS ENDPOINTS =============

@facturacion_bp.route('/reports/dashboard', methods=['GET'])
@token_required
def get_dashboard_metrics(current_user):
    """Get financial dashboard metrics"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        metrics = FinancialReportModel.get_dashboard_metrics(date_from, date_to)

        return success_response({'metrics': metrics})

    except Exception as e:
        print(f"Get dashboard metrics error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats(current_user):
    """Get dashboard stats (alias for /reports/dashboard for frontend compatibility)"""
    try:
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        metrics = FinancialReportModel.get_dashboard_metrics(date_from, date_to)

        return success_response(metrics)

    except Exception as e:
        print(f"Get dashboard stats error: {str(e)}")
        return error_response('An error occurred', 500)


@facturacion_bp.route('/dashboard/monthly', methods=['GET'])
@token_required
def get_dashboard_monthly(current_user):
    """Get monthly income/expenses data for charts"""
    try:
        from datetime import datetime, timedelta
        import calendar

        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        if not date_from:
            today = datetime.now()
            first_day = today.replace(day=1)
            date_from = (first_day - timedelta(days=180)).strftime('%Y-%m-%d')

        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')

        monthly_data = FinancialReportModel.get_monthly_summary(date_from, date_to)

        return success_response({
            'monthly': monthly_data,
            'period': {'from': date_from, 'to': date_to}
        })

    except Exception as e:
        print(f"Get dashboard monthly error: {str(e)}")
        return error_response('An error occurred', 500)


# Health check
@facturacion_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'facturacion'})
