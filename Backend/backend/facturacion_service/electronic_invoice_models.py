"""
Models for Electronic Invoicing
SRI (Servicio de Rentas Internas) Integration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db
from datetime import datetime


class SRIConfigurationModel:
    """SRI Configuration database operations"""

    @staticmethod
    def get_active_config():
        """Get active SRI configuration"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM sri_configuration
                WHERE active = TRUE
                LIMIT 1
            """)
            return cursor.fetchone()

    @staticmethod
    def update_config(config_id, **kwargs):
        """Update SRI configuration"""
        allowed_fields = [
            'ruc', 'razon_social', 'nombre_comercial', 'direccion_matriz',
            'codigo_establecimiento', 'punto_emision', 'ambiente', 'tipo_emision',
            'obligado_contabilidad', 'contribuyente_especial', 'email_emisor',
            'telefono_emisor', 'logo_path', 'certificado_digital_path',
            'certificado_password'
        ]

        updates = []
        params = []

        for field in allowed_fields:
            if field in kwargs and kwargs[field] is not None:
                updates.append(f"{field} = %s")
                params.append(kwargs[field])

        if not updates:
            return None

        params.append(config_id)
        query = f"""
            UPDATE sri_configuration
            SET {', '.join(updates)}
            WHERE config_id = %s
            RETURNING *
        """

        with db.get_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def get_next_secuencial():
        """Get and increment sequential number"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE sri_configuration
                SET secuencial_actual = secuencial_actual + 1
                WHERE active = TRUE
                RETURNING secuencial_actual
            """)
            result = cursor.fetchone()
            return result['secuencial_actual'] if result else 1


class InvoiceItemModel:
    """Invoice line items database operations"""

    @staticmethod
    def create(invoice_id, codigo_principal, descripcion, cantidad, precio_unitario,
               descuento, precio_total_sin_impuesto, codigo_iva, tarifa_iva, valor_iva,
               codigo_auxiliar=None):
        """Create invoice item"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, codigo_principal, codigo_auxiliar, descripcion,
                    cantidad, precio_unitario, descuento, precio_total_sin_impuesto,
                    codigo_iva, tarifa_iva, valor_iva
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (invoice_id, codigo_principal, codigo_auxiliar, descripcion,
                  cantidad, precio_unitario, descuento, precio_total_sin_impuesto,
                  codigo_iva, tarifa_iva, valor_iva))
            return cursor.fetchone()

    @staticmethod
    def create_many(items):
        """Create multiple invoice items"""
        with db.get_cursor(commit=True) as cursor:
            cursor.executemany("""
                INSERT INTO invoice_items (
                    invoice_id, codigo_principal, codigo_auxiliar, descripcion,
                    cantidad, precio_unitario, descuento, precio_total_sin_impuesto,
                    codigo_iva, tarifa_iva, valor_iva
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, items)
            return cursor.rowcount

    @staticmethod
    def get_by_invoice(invoice_id):
        """Get all items for an invoice"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM invoice_items
                WHERE invoice_id = %s
                ORDER BY item_id
            """, (invoice_id,))
            return cursor.fetchall()

    @staticmethod
    def delete_by_invoice(invoice_id):
        """Delete all items for an invoice"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM invoice_items
                WHERE invoice_id = %s
            """, (invoice_id,))
            return cursor.rowcount


class InvoicePaymentModel:
    """Invoice payment methods database operations"""

    @staticmethod
    def create(invoice_id, forma_pago, total, plazo=None, unidad_tiempo=None):
        """Create payment method"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO invoice_payments (invoice_id, forma_pago, total, plazo, unidad_tiempo)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
            """, (invoice_id, forma_pago, total, plazo, unidad_tiempo))
            return cursor.fetchone()

    @staticmethod
    def create_many(payments):
        """Create multiple payment methods"""
        with db.get_cursor(commit=True) as cursor:
            cursor.executemany("""
                INSERT INTO invoice_payments (invoice_id, forma_pago, total, plazo, unidad_tiempo)
                VALUES (%s, %s, %s, %s, %s)
            """, payments)
            return cursor.rowcount

    @staticmethod
    def get_by_invoice(invoice_id):
        """Get all payment methods for an invoice"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM invoice_payments
                WHERE invoice_id = %s
            """, (invoice_id,))
            return cursor.fetchall()

    @staticmethod
    def delete_by_invoice(invoice_id):
        """Delete all payment methods for an invoice"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM invoice_payments
                WHERE invoice_id = %s
            """, (invoice_id,))
            return cursor.rowcount


class InvoiceAdditionalInfoModel:
    """Invoice additional information database operations"""

    @staticmethod
    def create(invoice_id, nombre, valor):
        """Create additional information field"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO invoice_additional_info (invoice_id, nombre, valor)
                VALUES (%s, %s, %s)
                RETURNING *
            """, (invoice_id, nombre, valor))
            return cursor.fetchone()

    @staticmethod
    def create_many(info_items):
        """Create multiple additional information fields"""
        with db.get_cursor(commit=True) as cursor:
            cursor.executemany("""
                INSERT INTO invoice_additional_info (invoice_id, nombre, valor)
                VALUES (%s, %s, %s)
            """, info_items)
            return cursor.rowcount

    @staticmethod
    def get_by_invoice(invoice_id):
        """Get all additional information for an invoice"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM invoice_additional_info
                WHERE invoice_id = %s
            """, (invoice_id,))
            return cursor.fetchall()

    @staticmethod
    def delete_by_invoice(invoice_id):
        """Delete all additional information for an invoice"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                DELETE FROM invoice_additional_info
                WHERE invoice_id = %s
            """, (invoice_id,))
            return cursor.rowcount


class SRIAuthorizationLogModel:
    """SRI authorization log database operations"""

    @staticmethod
    def create(invoice_id, clave_acceso, estado, numero_autorizacion=None,
               fecha_autorizacion=None, mensaje=None, xml_request=None, xml_response=None):
        """Create authorization log entry"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO sri_authorization_log (
                    invoice_id, clave_acceso, estado, numero_autorizacion,
                    fecha_autorizacion, mensaje, xml_request, xml_response
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (invoice_id, clave_acceso, estado, numero_autorizacion,
                  fecha_autorizacion, mensaje, xml_request, xml_response))
            return cursor.fetchone()

    @staticmethod
    def get_by_invoice(invoice_id):
        """Get all authorization attempts for an invoice"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM sri_authorization_log
                WHERE invoice_id = %s
                ORDER BY created_at DESC
            """, (invoice_id,))
            return cursor.fetchall()

    @staticmethod
    def get_by_clave_acceso(clave_acceso):
        """Get authorization log by access key"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM sri_authorization_log
                WHERE clave_acceso = %s
                ORDER BY created_at DESC
                LIMIT 1
            """, (clave_acceso,))
            return cursor.fetchone()


class ElectronicInvoiceModel:
    """Complete electronic invoice operations"""

    @staticmethod
    def update_electronic_data(invoice_id, clave_acceso, numero_autorizacion=None,
                                fecha_autorizacion=None, xml_content=None,
                                estado_sri=None, mensaje_sri=None):
        """Update invoice with electronic data"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE invoices
                SET clave_acceso = %s,
                    numero_autorizacion = %s,
                    fecha_autorizacion = %s,
                    xml_content = %s,
                    estado_sri = %s,
                    mensaje_sri = %s
                WHERE invoice_id = %s
                RETURNING *
            """, (clave_acceso, numero_autorizacion, fecha_autorizacion,
                  xml_content, estado_sri, mensaje_sri, invoice_id))
            return cursor.fetchone()

    @staticmethod
    def update_sri_status(invoice_id, estado_sri, mensaje_sri=None):
        """Update SRI status"""
        with db.get_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE invoices
                SET estado_sri = %s,
                    mensaje_sri = %s
                WHERE invoice_id = %s
                RETURNING invoice_id, estado_sri, mensaje_sri
            """, (estado_sri, mensaje_sri, invoice_id))
            return cursor.fetchone()

    @staticmethod
    def get_complete_invoice(invoice_id):
        """Get complete invoice data with all related information"""
        with db.get_cursor() as cursor:
            # Get invoice data
            cursor.execute("""
                SELECT i.*, p.first_name, p.last_name, p.doc_type, p.doc_number,
                       p.email, p.phone, p.address
                FROM invoices i
                LEFT JOIN patients p ON i.patient_id = p.patient_id
                WHERE i.invoice_id = %s
            """, (invoice_id,))
            invoice = cursor.fetchone()

            if not invoice:
                return None

            # Get items
            items = InvoiceItemModel.get_by_invoice(invoice_id)

            # Get payment methods
            payments = InvoicePaymentModel.get_by_invoice(invoice_id)

            # Get additional info
            additional_info = InvoiceAdditionalInfoModel.get_by_invoice(invoice_id)

            return {
                'invoice': invoice,
                'items': items,
                'payments': payments,
                'additional_info': additional_info
            }

    @staticmethod
    def list_electronic_invoices(limit=20, offset=0, estado_sri=None, date_from=None, date_to=None):
        """List electronic invoices"""
        query = """
            SELECT * FROM v_electronic_invoices
            WHERE 1=1
        """
        params = []

        if estado_sri:
            query += " AND estado_sri = %s"
            params.append(estado_sri)

        if date_from:
            query += " AND issue_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND issue_date <= %s"
            params.append(date_to)

        query += " ORDER BY issue_date DESC, invoice_id DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    @staticmethod
    def count_electronic_invoices(estado_sri=None, date_from=None, date_to=None):
        """Count electronic invoices"""
        query = "SELECT COUNT(*) as count FROM v_electronic_invoices WHERE 1=1"
        params = []

        if estado_sri:
            query += " AND estado_sri = %s"
            params.append(estado_sri)

        if date_from:
            query += " AND issue_date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND issue_date <= %s"
            params.append(date_to)

        with db.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def get_statistics():
        """Get electronic invoicing statistics"""
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_facturas,
                    COUNT(CASE WHEN estado_sri = 'AUTORIZADA' THEN 1 END) as autorizadas,
                    COUNT(CASE WHEN estado_sri = 'PENDIENTE' THEN 1 END) as pendientes,
                    COUNT(CASE WHEN estado_sri = 'NO_AUTORIZADA' THEN 1 END) as rechazadas,
                    COUNT(CASE WHEN estado_sri = 'ERROR' THEN 1 END) as errores,
                    COALESCE(SUM(CASE WHEN estado_sri = 'AUTORIZADA' THEN total_amount ELSE 0 END), 0) as monto_autorizado
                FROM invoices
                WHERE clave_acceso IS NOT NULL
            """)
            return cursor.fetchone()
