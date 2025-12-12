-- =====================================================
-- Electronic Invoicing Schema Updates
-- SRI (Servicio de Rentas Internas) Integration
-- =====================================================

-- Add electronic invoicing fields to invoices table
ALTER TABLE invoices
ADD COLUMN IF NOT EXISTS clave_acceso VARCHAR(49),
ADD COLUMN IF NOT EXISTS numero_autorizacion VARCHAR(49),
ADD COLUMN IF NOT EXISTS fecha_autorizacion TIMESTAMP,
ADD COLUMN IF NOT EXISTS xml_content TEXT,
ADD COLUMN IF NOT EXISTS estado_sri VARCHAR(20) DEFAULT 'PENDIENTE',
ADD COLUMN IF NOT EXISTS mensaje_sri TEXT,
ADD COLUMN IF NOT EXISTS ambiente VARCHAR(1) DEFAULT '1',
ADD COLUMN IF NOT EXISTS tipo_emision VARCHAR(1) DEFAULT '1';

-- Add comments to new columns
COMMENT ON COLUMN invoices.clave_acceso IS '49-digit SRI access key';
COMMENT ON COLUMN invoices.numero_autorizacion IS 'SRI authorization number';
COMMENT ON COLUMN invoices.fecha_autorizacion IS 'SRI authorization date and time';
COMMENT ON COLUMN invoices.xml_content IS 'Generated XML for electronic invoice';
COMMENT ON COLUMN invoices.estado_sri IS 'SRI status: PENDIENTE, RECIBIDA, AUTORIZADA, NO_AUTORIZADA, ERROR';
COMMENT ON COLUMN invoices.mensaje_sri IS 'SRI response messages or errors';
COMMENT ON COLUMN invoices.ambiente IS 'SRI environment: 1=Test, 2=Production';
COMMENT ON COLUMN invoices.tipo_emision IS 'Emission type: 1=Normal';

-- Create table for invoice line items (detalles)
CREATE TABLE IF NOT EXISTS invoice_items (
    item_id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    codigo_principal VARCHAR(50) NOT NULL,
    codigo_auxiliar VARCHAR(50),
    descripcion TEXT NOT NULL,
    cantidad DECIMAL(10, 2) NOT NULL,
    precio_unitario DECIMAL(12, 6) NOT NULL,
    descuento DECIMAL(10, 2) DEFAULT 0,
    precio_total_sin_impuesto DECIMAL(12, 2) NOT NULL,
    codigo_iva VARCHAR(1) NOT NULL,
    tarifa_iva DECIMAL(5, 2) NOT NULL,
    valor_iva DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for invoice items
CREATE INDEX IF NOT EXISTS idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX IF NOT EXISTS idx_invoice_items_codigo ON invoice_items(codigo_principal);

-- Create table for SRI company configuration
CREATE TABLE IF NOT EXISTS sri_configuration (
    config_id SERIAL PRIMARY KEY,
    ruc VARCHAR(13) NOT NULL UNIQUE,
    razon_social VARCHAR(300) NOT NULL,
    nombre_comercial VARCHAR(300) NOT NULL,
    direccion_matriz TEXT NOT NULL,
    codigo_establecimiento VARCHAR(3) DEFAULT '001',
    punto_emision VARCHAR(3) DEFAULT '001',
    ambiente VARCHAR(1) DEFAULT '1',
    tipo_emision VARCHAR(1) DEFAULT '1',
    obligado_contabilidad VARCHAR(2) DEFAULT 'SI',
    contribuyente_especial VARCHAR(5),
    email_emisor VARCHAR(255),
    telefono_emisor VARCHAR(20),
    logo_path VARCHAR(500),
    certificado_digital_path VARCHAR(500),
    certificado_password VARCHAR(255),
    secuencial_actual INTEGER DEFAULT 1,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for active configuration
CREATE INDEX IF NOT EXISTS idx_sri_config_active ON sri_configuration(active);

-- Insert default configuration (to be updated by clinic)
INSERT INTO sri_configuration (
    ruc,
    razon_social,
    nombre_comercial,
    direccion_matriz,
    ambiente
) VALUES (
    '9999999999001',
    'CLINICA EJEMPLO S.A.',
    'Clinica Ejemplo',
    'Av. Principal 123 y Secundaria, Quito, Ecuador',
    '1'
) ON CONFLICT (ruc) DO NOTHING;

-- Create table for payment methods
CREATE TABLE IF NOT EXISTS invoice_payments (
    payment_id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    forma_pago VARCHAR(2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    plazo INTEGER,
    unidad_tiempo VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for invoice payments
CREATE INDEX IF NOT EXISTS idx_invoice_payments_invoice ON invoice_payments(invoice_id);

-- Create table for additional information
CREATE TABLE IF NOT EXISTS invoice_additional_info (
    info_id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id) ON DELETE CASCADE,
    nombre VARCHAR(100) NOT NULL,
    valor TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for additional info
CREATE INDEX IF NOT EXISTS idx_invoice_additional_info_invoice ON invoice_additional_info(invoice_id);

-- Create table for SRI authorization log
CREATE TABLE IF NOT EXISTS sri_authorization_log (
    log_id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(invoice_id),
    clave_acceso VARCHAR(49) NOT NULL,
    estado VARCHAR(20) NOT NULL,
    numero_autorizacion VARCHAR(49),
    fecha_autorizacion TIMESTAMP,
    mensaje TEXT,
    xml_request TEXT,
    xml_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for authorization log
CREATE INDEX IF NOT EXISTS idx_sri_auth_log_invoice ON sri_authorization_log(invoice_id);
CREATE INDEX IF NOT EXISTS idx_sri_auth_log_clave ON sri_authorization_log(clave_acceso);
CREATE INDEX IF NOT EXISTS idx_sri_auth_log_estado ON sri_authorization_log(estado);

-- Update existing invoices status values
UPDATE invoices SET status = 'DRAFT' WHERE status = 'BORRADOR';
UPDATE invoices SET status = 'ISSUED' WHERE status = 'EMITIDA';
UPDATE invoices SET status = 'PAID' WHERE status = 'PAGADA';
UPDATE invoices SET status = 'ANNULLED' WHERE status = 'ANULADA';

-- Add new status for electronic invoices
-- Status flow: DRAFT -> PROCESSING -> AUTHORIZED -> ISSUED -> PAID
--              DRAFT -> PROCESSING -> REJECTED
--              ISSUED -> ANNULLED

COMMENT ON TABLE invoice_items IS 'Invoice line items for electronic invoices';
COMMENT ON TABLE sri_configuration IS 'SRI configuration for electronic invoicing';
COMMENT ON TABLE invoice_payments IS 'Payment methods for invoices';
COMMENT ON TABLE invoice_additional_info IS 'Additional information for invoices';
COMMENT ON TABLE sri_authorization_log IS 'Log of SRI authorization attempts and responses';

-- Create view for complete invoice data
CREATE OR REPLACE VIEW v_electronic_invoices AS
SELECT
    i.invoice_id,
    i.invoice_number,
    i.issue_date,
    i.patient_id,
    i.subtotal,
    i.iva_rate,
    i.iva_amount,
    i.total_amount,
    i.status,
    i.clave_acceso,
    i.numero_autorizacion,
    i.fecha_autorizacion,
    i.estado_sri,
    i.ambiente,
    p.first_name || ' ' || p.last_name as patient_name,
    p.doc_type as patient_doc_type,
    p.doc_number as patient_doc_number,
    p.email as patient_email,
    p.phone as patient_phone,
    p.address as patient_address,
    sc.ruc as emisor_ruc,
    sc.razon_social as emisor_razon_social,
    sc.nombre_comercial as emisor_nombre_comercial
FROM invoices i
LEFT JOIN patients p ON i.patient_id = p.patient_id
LEFT JOIN sri_configuration sc ON sc.active = TRUE
WHERE i.clave_acceso IS NOT NULL;

COMMENT ON VIEW v_electronic_invoices IS 'Complete view of electronic invoices with patient and issuer data';

-- Trigger to update sri_configuration.updated_at
CREATE OR REPLACE FUNCTION update_sri_config_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_sri_config_timestamp
BEFORE UPDATE ON sri_configuration
FOR EACH ROW
EXECUTE FUNCTION update_sri_config_timestamp();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Electronic invoicing schema created successfully!';
    RAISE NOTICE 'Tables created: invoice_items, sri_configuration, invoice_payments, invoice_additional_info, sri_authorization_log';
    RAISE NOTICE 'View created: v_electronic_invoices';
    RAISE NOTICE 'Please update sri_configuration table with your actual RUC and company information';
END $$;
