"""
Routes for Electronic Invoicing (SRI)
"""
from flask import Blueprint, request
from datetime import datetime, date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.auth_middleware import token_required
from common.utils import success_response, error_response, get_pagination_params
from models import InvoiceModel
from electronic_invoice_models import (
    SRIConfigurationModel, InvoiceItemModel, InvoicePaymentModel,
    InvoiceAdditionalInfoModel, SRIAuthorizationLogModel, ElectronicInvoiceModel
)
from sri_electronic_invoice import (
    SRIElectronicInvoice, SRIWebService, FORMAS_PAGO
)
from xml_storage import xml_storage

electronic_invoice_bp = Blueprint('electronic_invoice', __name__)


# ============= SRI CONFIGURATION ENDPOINTS =============

@electronic_invoice_bp.route('/sri/config', methods=['GET'])
@token_required
def get_sri_config(current_user):
    """Get active SRI configuration"""
    try:
        config = SRIConfigurationModel.get_active_config()

        if not config:
            return error_response('SRI configuration not found', 404)

        # Hide sensitive data
        if config.get('certificado_password'):
            config['certificado_password'] = '********'

        return success_response({'config': config})

    except Exception as e:
        print(f"Get SRI config error: {str(e)}")
        return error_response('An error occurred', 500)


@electronic_invoice_bp.route('/sri/config/<int:config_id>', methods=['PUT'])
@token_required
def update_sri_config(current_user, config_id):
    """Update SRI configuration"""
    try:
        # Check if user has admin role
        if current_user.get('role_name') not in ['ADMIN', 'ADMINISTRADOR']:
            return error_response('Insufficient permissions', 403)

        data = request.get_json()

        if not data:
            return error_response('No data to update', 400)

        config = SRIConfigurationModel.update_config(config_id, **data)

        if not config:
            return error_response('Configuration not found', 404)

        return success_response({'config': config}, 'Configuration updated successfully')

    except Exception as e:
        print(f"Update SRI config error: {str(e)}")
        return error_response('An error occurred', 500)


# ============= ELECTRONIC INVOICE ENDPOINTS =============

@electronic_invoice_bp.route('/electronic-invoices', methods=['POST'])
@token_required
def create_electronic_invoice(current_user):
    """
    Create and generate electronic invoice (SRI compliant)

    Request body:
    {
        "patient_id": 1,
        "items": [
            {
                "codigo": "CONS001",
                "descripcion": "Consulta medica general",
                "cantidad": 1,
                "precio_unitario": 50.00,
                "descuento": 0,
                "codigo_iva": "3",  // 0=0%, 3=15%
                "tarifa_iva": 15
            }
        ],
        "formas_pago": [
            {
                "codigo": "01",  // See FORMAS_PAGO constant
                "total": 57.50
            }
        ],
        "info_adicional": [
            {
                "nombre": "Email",
                "valor": "paciente@email.com"
            }
        ]
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'patient_id' not in data or 'items' not in data:
            return error_response('patient_id and items are required', 400)

        if not data['items']:
            return error_response('At least one item is required', 400)

        # Get SRI configuration
        sri_config = SRIConfigurationModel.get_active_config()
        if not sri_config:
            return error_response('SRI configuration not found. Please configure first.', 400)

        # Calculate totals
        subtotal_iva_0 = 0
        subtotal_iva_15 = 0
        iva_15 = 0
        total_descuento = 0

        processed_items = []

        for item in data['items']:
            cantidad = float(item['cantidad'])
            precio_unitario = float(item['precio_unitario'])
            descuento = float(item.get('descuento', 0))
            tarifa_iva = float(item.get('tarifa_iva', 15))

            precio_total_sin_impuesto = (cantidad * precio_unitario) - descuento
            valor_iva = precio_total_sin_impuesto * (tarifa_iva / 100)

            total_descuento += descuento

            # Categorize by IVA rate
            if tarifa_iva == 0:
                subtotal_iva_0 += precio_total_sin_impuesto
            else:
                subtotal_iva_15 += precio_total_sin_impuesto
                iva_15 += valor_iva

            processed_items.append({
                'codigo': item['codigo'],
                'codigo_auxiliar': item.get('codigo_auxiliar'),
                'descripcion': item['descripcion'],
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'descuento': descuento,
                'precio_total_sin_impuesto': precio_total_sin_impuesto,
                'codigo_iva': item.get('codigo_iva', '3'),
                'tarifa_iva': tarifa_iva,
                'valor_iva': valor_iva
            })

        subtotal_sin_impuestos = subtotal_iva_0 + subtotal_iva_15
        importe_total = subtotal_sin_impuestos + iva_15

        # Get next sequential number
        secuencial = SRIConfigurationModel.get_next_secuencial()

        # Generate invoice number
        invoice_number = f"{sri_config['codigo_establecimiento']}-{sri_config['punto_emision']}-{secuencial:09d}"

        # Create invoice in database
        issue_date = data.get('issue_date', date.today())
        invoice = InvoiceModel.create(
            patient_id=data['patient_id'],
            appointment_id=data.get('appointment_id'),
            invoice_number=invoice_number,
            issue_date=issue_date,
            subtotal=subtotal_sin_impuestos,
            iva_rate=15.0,
            iva_amount=iva_15,
            total_amount=importe_total,
            status='DRAFT'
        )

        invoice_id = invoice['invoice_id']

        # Save invoice items
        items_data = [
            (invoice_id, item['codigo'], item['codigo_auxiliar'], item['descripcion'],
             item['cantidad'], item['precio_unitario'], item['descuento'],
             item['precio_total_sin_impuesto'], item['codigo_iva'],
             item['tarifa_iva'], item['valor_iva'])
            for item in processed_items
        ]
        InvoiceItemModel.create_many(items_data)

        # Save payment methods
        if data.get('formas_pago'):
            payments_data = [
                (invoice_id, fp['codigo'], fp['total'], fp.get('plazo'), fp.get('unidad_tiempo'))
                for fp in data['formas_pago']
            ]
            InvoicePaymentModel.create_many(payments_data)

        # Save additional information
        if data.get('info_adicional'):
            info_data = [
                (invoice_id, info['nombre'], info['valor'])
                for info in data['info_adicional']
            ]
            InvoiceAdditionalInfoModel.create_many(info_data)

        # Generate XML
        sri_generator = SRIElectronicInvoice(
            ruc_emisor=sri_config['ruc'],
            razon_social=sri_config['razon_social'],
            nombre_comercial=sri_config['nombre_comercial'],
            direccion_matriz=sri_config['direccion_matriz'],
            codigo_establecimiento=sri_config['codigo_establecimiento'],
            punto_emision=sri_config['punto_emision'],
            ambiente=sri_config['ambiente'],
            tipo_emision=sri_config['tipo_emision']
        )

        # Get complete invoice data
        complete_invoice = ElectronicInvoiceModel.get_complete_invoice(invoice_id)

        # Prepare XML data
        xml_data = {
            'secuencial': str(secuencial),
            'fecha_emision': issue_date.strftime('%d/%m/%Y') if isinstance(issue_date, date) else issue_date,
            'cliente': {
                'tipo_doc': complete_invoice['invoice']['doc_type'] if complete_invoice['invoice']['doc_type'] == 'RUC' else '05',
                'nombre': f"{complete_invoice['invoice']['first_name']} {complete_invoice['invoice']['last_name']}",
                'identificacion': complete_invoice['invoice']['doc_number'],
                'direccion': complete_invoice['invoice'].get('address'),
                'email': complete_invoice['invoice'].get('email'),
                'telefono': complete_invoice['invoice'].get('phone')
            },
            'items': processed_items,
            'totales': {
                'subtotal_sin_impuestos': subtotal_sin_impuestos,
                'descuento_total': total_descuento,
                'subtotal_iva_0': subtotal_iva_0,
                'subtotal_iva_15': subtotal_iva_15,
                'iva_15': iva_15,
                'importe_total': importe_total
            },
            'formas_pago': data.get('formas_pago', []),
            'info_adicional': data.get('info_adicional', [])
        }

        result = sri_generator.generate_xml(xml_data)

        # Save XML to file system
        xml_filepath = xml_storage.save_xml(
            invoice_number=invoice_number,
            xml_content=result['xml'],
            estado='PENDIENTE',
            date=issue_date if isinstance(issue_date, date) else datetime.strptime(issue_date, '%Y-%m-%d').date()
        )

        # Create backup
        xml_storage.backup_xml(invoice_number, result['xml'])

        # Update invoice with electronic data
        ElectronicInvoiceModel.update_electronic_data(
            invoice_id=invoice_id,
            clave_acceso=result['clave_acceso'],
            xml_content=result['xml'],
            estado_sri='PENDIENTE'
        )

        # Log generation
        SRIAuthorizationLogModel.create(
            invoice_id=invoice_id,
            clave_acceso=result['clave_acceso'],
            estado='GENERADO',
            mensaje='XML generado exitosamente'
        )

        return success_response({
            'invoice': complete_invoice['invoice'],
            'items': complete_invoice['items'],
            'clave_acceso': result['clave_acceso'],
            'xml': result['xml'],
            'message': 'Electronic invoice created successfully. Use /authorize endpoint to send to SRI.'
        }, 'Electronic invoice created successfully', 201)

    except Exception as e:
        print(f"Create electronic invoice error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'An error occurred: {str(e)}', 500)


@electronic_invoice_bp.route('/electronic-invoices/<int:invoice_id>/authorize', methods=['POST'])
@token_required
def authorize_electronic_invoice(current_user, invoice_id):
    """
    Send electronic invoice to SRI for authorization
    """
    try:
        # Get complete invoice
        complete_invoice = ElectronicInvoiceModel.get_complete_invoice(invoice_id)

        if not complete_invoice:
            return error_response('Invoice not found', 404)

        invoice = complete_invoice['invoice']

        if not invoice.get('xml_content'):
            return error_response('Invoice does not have XML. Generate electronic invoice first.', 400)

        if invoice.get('estado_sri') == 'AUTORIZADA':
            return error_response('Invoice is already authorized', 400)

        # Get SRI configuration
        sri_config = SRIConfigurationModel.get_active_config()

        # Initialize SRI web service
        sri_ws = SRIWebService(ambiente=sri_config['ambiente'])

        # Send to SRI
        reception_response = sri_ws.enviar_comprobante(invoice['xml_content'])

        # Update status
        if reception_response['estado'] == 'RECIBIDA':
            ElectronicInvoiceModel.update_sri_status(
                invoice_id=invoice_id,
                estado_sri='RECIBIDA',
                mensaje_sri=reception_response.get('mensaje')
            )

            # Log reception
            SRIAuthorizationLogModel.create(
                invoice_id=invoice_id,
                clave_acceso=invoice['clave_acceso'],
                estado='RECIBIDA',
                mensaje=reception_response.get('mensaje'),
                xml_request=invoice['xml_content']
            )

            # Check authorization
            auth_response = sri_ws.consultar_autorizacion(invoice['clave_acceso'])

            if auth_response['estado'] == 'AUTORIZADO':
                # Update invoice with authorization
                ElectronicInvoiceModel.update_electronic_data(
                    invoice_id=invoice_id,
                    clave_acceso=invoice['clave_acceso'],
                    numero_autorizacion=auth_response['numero_autorizacion'],
                    fecha_autorizacion=datetime.now(),
                    xml_content=invoice['xml_content'],
                    estado_sri='AUTORIZADA',
                    mensaje_sri='Factura autorizada por SRI'
                )

                # Update invoice status to ISSUED
                InvoiceModel.update_status(invoice_id, 'ISSUED')

                # Save authorized XML to file system
                xml_storage.save_xml(
                    invoice_number=invoice['invoice_number'],
                    xml_content=invoice['xml_content'],
                    estado='AUTORIZADO',
                    date=invoice['issue_date']
                )

                # Log authorization
                SRIAuthorizationLogModel.create(
                    invoice_id=invoice_id,
                    clave_acceso=invoice['clave_acceso'],
                    estado='AUTORIZADA',
                    numero_autorizacion=auth_response['numero_autorizacion'],
                    fecha_autorizacion=datetime.now(),
                    mensaje='Factura autorizada exitosamente'
                )

                return success_response({
                    'invoice_id': invoice_id,
                    'clave_acceso': invoice['clave_acceso'],
                    'numero_autorizacion': auth_response['numero_autorizacion'],
                    'estado': 'AUTORIZADA',
                    'mensaje': 'Invoice authorized successfully by SRI'
                }, 'Invoice authorized successfully')
            else:
                # Not authorized
                ElectronicInvoiceModel.update_sri_status(
                    invoice_id=invoice_id,
                    estado_sri='NO_AUTORIZADA',
                    mensaje_sri=auth_response.get('mensaje', 'No autorizada por SRI')
                )

                return error_response(f"Invoice not authorized: {auth_response.get('mensaje')}", 400)
        else:
            # Reception failed
            ElectronicInvoiceModel.update_sri_status(
                invoice_id=invoice_id,
                estado_sri='ERROR',
                mensaje_sri=reception_response.get('mensaje', 'Error al enviar a SRI')
            )

            return error_response(f"SRI reception failed: {reception_response.get('mensaje')}", 400)

    except Exception as e:
        print(f"Authorize electronic invoice error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(f'An error occurred: {str(e)}', 500)


@electronic_invoice_bp.route('/electronic-invoices', methods=['GET'])
@token_required
def list_electronic_invoices(current_user):
    """List electronic invoices"""
    try:
        pagination = get_pagination_params(request)
        estado_sri = request.args.get('estado_sri')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')

        invoices = ElectronicInvoiceModel.list_electronic_invoices(
            limit=pagination['per_page'],
            offset=pagination['offset'],
            estado_sri=estado_sri,
            date_from=date_from,
            date_to=date_to
        )

        total = ElectronicInvoiceModel.count_electronic_invoices(
            estado_sri=estado_sri,
            date_from=date_from,
            date_to=date_to
        )

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
        print(f"List electronic invoices error: {str(e)}")
        return error_response('An error occurred', 500)


@electronic_invoice_bp.route('/electronic-invoices/<int:invoice_id>', methods=['GET'])
@token_required
def get_electronic_invoice(current_user, invoice_id):
    """Get complete electronic invoice data"""
    try:
        complete_invoice = ElectronicInvoiceModel.get_complete_invoice(invoice_id)

        if not complete_invoice:
            return error_response('Invoice not found', 404)

        # Get authorization log
        auth_log = SRIAuthorizationLogModel.get_by_invoice(invoice_id)

        return success_response({
            'invoice': complete_invoice['invoice'],
            'items': complete_invoice['items'],
            'payments': complete_invoice['payments'],
            'additional_info': complete_invoice['additional_info'],
            'authorization_log': auth_log
        })

    except Exception as e:
        print(f"Get electronic invoice error: {str(e)}")
        return error_response('An error occurred', 500)


@electronic_invoice_bp.route('/electronic-invoices/<int:invoice_id>/xml', methods=['GET'])
@token_required
def get_invoice_xml(current_user, invoice_id):
    """Get invoice XML"""
    try:
        complete_invoice = ElectronicInvoiceModel.get_complete_invoice(invoice_id)

        if not complete_invoice:
            return error_response('Invoice not found', 404)

        if not complete_invoice['invoice'].get('xml_content'):
            return error_response('XML not available for this invoice', 404)

        return success_response({
            'xml': complete_invoice['invoice']['xml_content'],
            'clave_acceso': complete_invoice['invoice']['clave_acceso']
        })

    except Exception as e:
        print(f"Get invoice XML error: {str(e)}")
        return error_response('An error occurred', 500)


@electronic_invoice_bp.route('/electronic-invoices/statistics', methods=['GET'])
@token_required
def get_electronic_invoice_statistics(current_user):
    """Get electronic invoicing statistics"""
    try:
        stats = ElectronicInvoiceModel.get_statistics()
        return success_response({'statistics': stats})

    except Exception as e:
        print(f"Get statistics error: {str(e)}")
        return error_response('An error occurred', 500)


@electronic_invoice_bp.route('/sri/payment-methods', methods=['GET'])
@token_required
def get_payment_methods(current_user):
    """Get SRI payment method codes"""
    try:
        payment_methods = [
            {'codigo': code, 'descripcion': desc}
            for code, desc in FORMAS_PAGO.items()
        ]
        return success_response({'payment_methods': payment_methods})

    except Exception as e:
        print(f"Get payment methods error: {str(e)}")
        return error_response('An error occurred', 500)


# Health check
@electronic_invoice_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({'status': 'healthy', 'service': 'electronic_invoice'})
