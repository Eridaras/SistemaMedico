-- ============================================================
-- ESQUEMA OPTIMIZADO BD - SISTEMA MÉDICO ECUADOR
-- Diseñado para alta escalabilidad y millones de registros
-- ============================================================

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas rápidas de texto

-- ============================================================
-- ROLES Y USUARIOS
-- ============================================================

CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_roles_name ON roles(name);

CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    full_name VARCHAR(200) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Índices para búsquedas rápidas
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_active ON users(role_id, is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- ============================================================
-- PACIENTES (Optimizado para millones de registros)
-- ============================================================

CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,

    -- Identificación (Ecuador)
    identification VARCHAR(13) UNIQUE NOT NULL, -- Cédula o pasaporte
    identification_type VARCHAR(20) DEFAULT 'cedula', -- cedula, pasaporte, ruc

    -- Datos personales
    full_name VARCHAR(200) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    blood_type VARCHAR(5),

    -- Contacto
    phone VARCHAR(15),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    province VARCHAR(100),

    -- Contacto de emergencia
    emergency_contact_name VARCHAR(200),
    emergency_contact_phone VARCHAR(15),
    emergency_contact_relationship VARCHAR(50),

    -- Seguro médico
    insurance_provider VARCHAR(200),
    insurance_number VARCHAR(100),

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id)
);

-- Índices críticos para rendimiento
CREATE UNIQUE INDEX idx_patients_identification ON patients(identification);
CREATE INDEX idx_patients_full_name_trgm ON patients USING gin(full_name gin_trgm_ops); -- Búsqueda fuzzy
CREATE INDEX idx_patients_phone ON patients(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_patients_email ON patients(email) WHERE email IS NOT NULL;
CREATE INDEX idx_patients_active ON patients(is_active) WHERE is_active = true;
CREATE INDEX idx_patients_created_at ON patients(created_at DESC);
CREATE INDEX idx_patients_dob ON patients(date_of_birth);

-- ============================================================
-- HISTORIA CLÍNICA (Particionada por año para escalabilidad)
-- ============================================================

CREATE TABLE IF NOT EXISTS medical_records (
    record_id BIGSERIAL,
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id INTEGER NOT NULL REFERENCES users(user_id),

    -- Información médica
    diagnosis TEXT,
    symptoms TEXT,
    treatment_plan TEXT,
    observations TEXT,

    -- Signos vitales
    blood_pressure VARCHAR(20),
    heart_rate INTEGER,
    temperature DECIMAL(4,2),
    weight DECIMAL(5,2),
    height DECIMAL(5,2),

    -- Metadata
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (record_id, record_date)
) PARTITION BY RANGE (record_date);

-- Crear particiones por año (últimos 5 años + futuro)
CREATE TABLE medical_records_2023 PARTITION OF medical_records
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE medical_records_2024 PARTITION OF medical_records
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE medical_records_2025 PARTITION OF medical_records
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE medical_records_2026 PARTITION OF medical_records
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');

CREATE TABLE medical_records_future PARTITION OF medical_records
    FOR VALUES FROM ('2027-01-01') TO ('2099-12-31');

-- Índices en cada partición se crean automáticamente
CREATE INDEX idx_medical_records_patient ON medical_records(patient_id, record_date DESC);
CREATE INDEX idx_medical_records_doctor ON medical_records(doctor_id);
CREATE INDEX idx_medical_records_date ON medical_records(record_date DESC);

-- Antecedentes médicos (tabla separada para evitar duplicación)
CREATE TABLE IF NOT EXISTS medical_history (
    history_id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id),

    -- Antecedentes
    allergies TEXT,
    chronic_diseases TEXT,
    surgeries TEXT,
    medications TEXT,
    family_history TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_medical_history_patient ON medical_history(patient_id);

-- ============================================================
-- INVENTARIO (Optimizado para alta frecuencia de lectura)
-- ============================================================

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,

    -- Identificación
    sku VARCHAR(50) UNIQUE,
    barcode VARCHAR(100),

    -- Información básica
    name VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50), -- medicamento, insumo, equipo
    category VARCHAR(100),

    -- Precios
    unit_price DECIMAL(10,2) NOT NULL,
    cost_price DECIMAL(10,2), -- Para cálculo de rentabilidad

    -- Stock (desnormalizado para performance)
    current_stock INTEGER DEFAULT 0,
    minimum_stock INTEGER DEFAULT 0,
    maximum_stock INTEGER,
    reorder_point INTEGER,

    -- Atributos fiscales Ecuador
    iva_percentage DECIMAL(5,2) DEFAULT 15.00,
    requires_prescription BOOLEAN DEFAULT false,

    -- Lote y vencimiento
    batch_number VARCHAR(100),
    expiration_date DATE,

    -- Ubicación en bodega
    location VARCHAR(100),
    shelf VARCHAR(50),

    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para búsquedas y reportes
CREATE UNIQUE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
CREATE INDEX idx_products_barcode ON products(barcode) WHERE barcode IS NOT NULL;
CREATE INDEX idx_products_type_category ON products(type, category);
CREATE INDEX idx_products_active_stock ON products(is_active, current_stock) WHERE is_active = true;
CREATE INDEX idx_products_low_stock ON products(current_stock) WHERE current_stock <= minimum_stock;
CREATE INDEX idx_products_expiration ON products(expiration_date) WHERE expiration_date IS NOT NULL;

-- Historial de movimientos de inventario (particionado por mes)
CREATE TABLE IF NOT EXISTS stock_movements (
    movement_id BIGSERIAL,
    product_id INTEGER NOT NULL REFERENCES products(product_id),

    -- Tipo de movimiento
    movement_type VARCHAR(20) NOT NULL, -- in, out, adjustment, expired
    quantity INTEGER NOT NULL,

    -- Referencia (factura, compra, ajuste)
    reference_type VARCHAR(50), -- invoice, purchase, adjustment
    reference_id INTEGER,

    -- Usuario responsable
    user_id INTEGER REFERENCES users(user_id),

    -- Notas
    notes TEXT,

    -- Metadata
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (movement_id, movement_date)
) PARTITION BY RANGE (movement_date);

-- Particiones mensuales (últimos 12 meses)
CREATE TABLE stock_movements_2025_01 PARTITION OF stock_movements
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE stock_movements_2025_02 PARTITION OF stock_movements
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE stock_movements_2025_03 PARTITION OF stock_movements
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE stock_movements_future PARTITION OF stock_movements
    FOR VALUES FROM ('2025-04-01') TO ('2099-12-31');

CREATE INDEX idx_stock_movements_product ON stock_movements(product_id, movement_date DESC);
CREATE INDEX idx_stock_movements_type ON stock_movements(movement_type);
CREATE INDEX idx_stock_movements_date ON stock_movements(movement_date DESC);

-- ============================================================
-- TRATAMIENTOS Y RECETAS
-- ============================================================

CREATE TABLE IF NOT EXISTS treatments (
    treatment_id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) DEFAULT 0,
    iva_percentage DECIMAL(5,2) DEFAULT 0,
    duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_treatments_name ON treatments(name);
CREATE INDEX idx_treatments_active ON treatments(is_active) WHERE is_active = true;

-- Receta médica (productos por tratamiento)
CREATE TABLE IF NOT EXISTS treatment_recipes (
    recipe_id SERIAL PRIMARY KEY,
    treatment_id INTEGER NOT NULL REFERENCES treatments(treatment_id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL DEFAULT 1,
    instructions TEXT,
    UNIQUE(treatment_id, product_id)
);

CREATE INDEX idx_treatment_recipes_treatment ON treatment_recipes(treatment_id);
CREATE INDEX idx_treatment_recipes_product ON treatment_recipes(product_id);

-- ============================================================
-- CITAS (Particionado por mes para alto volumen)
-- ============================================================

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id BIGSERIAL,

    -- Relaciones
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id),
    doctor_id INTEGER NOT NULL REFERENCES users(user_id),
    treatment_id INTEGER REFERENCES treatments(treatment_id),

    -- Fechas y horarios
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,

    -- Estado y motivo
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, CONFIRMED, COMPLETED, CANCELLED, NO_SHOW
    reason TEXT,
    notes TEXT,

    -- Recordatorios
    reminder_sent BOOLEAN DEFAULT false,
    reminder_sent_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id),

    -- Constraints
    CHECK (end_time > start_time),
    CHECK (status IN ('PENDING', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')),

    PRIMARY KEY (appointment_id, start_time)
) PARTITION BY RANGE (start_time);

-- Particiones mensuales (últimos 6 meses + próximos 12 meses)
CREATE TABLE appointments_2025_01 PARTITION OF appointments
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE appointments_2025_02 PARTITION OF appointments
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE appointments_2025_03 PARTITION OF appointments
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE appointments_future PARTITION OF appointments
    FOR VALUES FROM ('2025-04-01') TO ('2099-12-31');

-- Índices críticos para agendar citas
CREATE INDEX idx_appointments_patient ON appointments(patient_id, start_time DESC);
CREATE INDEX idx_appointments_doctor_date ON appointments(doctor_id, start_time);
CREATE INDEX idx_appointments_status ON appointments(status, start_time);
CREATE INDEX idx_appointments_date_range ON appointments(start_time, end_time);
CREATE INDEX idx_appointments_reminders ON appointments(start_time, reminder_sent) WHERE reminder_sent = false;

-- Nota: Unique constraint en tabla particionada requiere incluir partition key
-- Constraint de no solapamiento se puede manejar a nivel de aplicación o con triggers
-- CREATE UNIQUE INDEX idx_appointments_doctor_no_overlap
--     ON appointments(doctor_id, start_time, end_time);

-- Servicios adicionales en cita
-- Nota: appointment_id no tiene FK constraint porque appointments es particionada
CREATE TABLE IF NOT EXISTS appointment_extras (
    extra_id SERIAL PRIMARY KEY,
    appointment_id BIGINT NOT NULL,
    description VARCHAR(200) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_appointment_extras_appointment ON appointment_extras(appointment_id);

-- ============================================================
-- FACTURACIÓN (Particionado por mes para reporting rápido)
-- ============================================================

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id BIGSERIAL,

    -- Relaciones
    patient_id INTEGER NOT NULL REFERENCES patients(patient_id),

    -- Montos
    subtotal DECIMAL(10,2) NOT NULL,
    iva_percentage DECIMAL(5,2) DEFAULT 15.00,
    iva DECIMAL(10,2) NOT NULL,
    discount DECIMAL(10,2) DEFAULT 0,
    total DECIMAL(10,2) NOT NULL,

    -- Pago
    payment_method VARCHAR(50), -- Efectivo, Tarjeta, Transferencia, Cheque
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, cancelled, refunded

    -- Datos fiscales Ecuador
    authorization_number VARCHAR(100),
    electronic_invoice BOOLEAN DEFAULT false,

    -- Metadata
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id),

    CHECK (status IN ('pending', 'paid', 'cancelled', 'refunded')),

    PRIMARY KEY (invoice_id, invoice_date)
) PARTITION BY RANGE (invoice_date);

-- Particiones mensuales
CREATE TABLE invoices_2025_01 PARTITION OF invoices
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE invoices_2025_02 PARTITION OF invoices
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE TABLE invoices_2025_03 PARTITION OF invoices
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE invoices_future PARTITION OF invoices
    FOR VALUES FROM ('2025-04-01') TO ('2099-12-31');

-- Índices para reportes financieros
CREATE INDEX idx_invoices_patient ON invoices(patient_id, invoice_date DESC);
CREATE INDEX idx_invoices_date ON invoices(invoice_date DESC);
CREATE INDEX idx_invoices_status ON invoices(status, invoice_date DESC);
CREATE INDEX idx_invoices_payment_method ON invoices(payment_method);
CREATE INDEX idx_invoices_pending ON invoices(invoice_date) WHERE status = 'pending';

-- Items de factura
-- Nota: invoice_id no tiene FK constraint porque invoices es particionada
CREATE TABLE IF NOT EXISTS invoice_items (
    item_id BIGSERIAL PRIMARY KEY,
    invoice_id BIGINT NOT NULL,
    product_id INTEGER REFERENCES products(product_id),

    -- Detalles del item
    description VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0,
    subtotal DECIMAL(10,2) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_invoice_items_invoice ON invoice_items(invoice_id);
CREATE INDEX idx_invoice_items_product ON invoice_items(product_id);

-- ============================================================
-- GASTOS OPERACIONALES
-- ============================================================

CREATE TABLE IF NOT EXISTS expenses (
    expense_id SERIAL PRIMARY KEY,

    -- Categorización
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),

    -- Descripción y monto
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,

    -- Proveedor
    supplier_name VARCHAR(200),
    supplier_ruc VARCHAR(13),

    -- Comprobante
    receipt_number VARCHAR(100),

    -- Fechas
    expense_date DATE NOT NULL,
    due_date DATE,
    paid_date DATE,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES users(user_id)
);

CREATE INDEX idx_expenses_date ON expenses(expense_date DESC);
CREATE INDEX idx_expenses_category ON expenses(category, expense_date DESC);
CREATE INDEX idx_expenses_supplier ON expenses(supplier_name);

-- ============================================================
-- AUDITORÍA Y LOGS
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id BIGSERIAL,

    -- Usuario y acción
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(100) NOT NULL, -- CREATE, UPDATE, DELETE, LOGIN, LOGOUT

    -- Tabla y registro afectado
    table_name VARCHAR(100),
    record_id INTEGER,

    -- Detalles
    old_values JSONB,
    new_values JSONB,

    -- Metadata
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (log_id, created_at)
) PARTITION BY RANGE (created_at);

-- Particiones trimestrales para logs
CREATE TABLE audit_logs_2025_q1 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');

CREATE TABLE audit_logs_2025_q2 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');

CREATE TABLE audit_logs_future PARTITION OF audit_logs
    FOR VALUES FROM ('2025-07-01') TO ('2099-12-31');

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_audit_logs_table ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action, created_at DESC);

-- ============================================================
-- TRIGGERS PARA ACTUALIZACIÓN AUTOMÁTICA
-- ============================================================

-- Función para updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a todas las tablas con updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_treatments_updated_at BEFORE UPDATE ON treatments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VISTAS MATERIALIZADAS PARA REPORTES RÁPIDOS
-- ============================================================

-- Vista para estadísticas diarias (refresco cada hora)
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_stats AS
SELECT
    DATE(i.invoice_date) as date,
    COUNT(DISTINCT i.invoice_id) as total_invoices,
    COUNT(DISTINCT i.patient_id) as total_patients,
    SUM(i.total) as revenue,
    SUM(i.total) FILTER (WHERE i.payment_method = 'Efectivo') as cash_revenue,
    SUM(i.total) FILTER (WHERE i.payment_method = 'Tarjeta') as card_revenue,
    COUNT(a.appointment_id) as total_appointments,
    COUNT(a.appointment_id) FILTER (WHERE a.status = 'COMPLETED') as completed_appointments
FROM invoices i
LEFT JOIN appointments a ON DATE(a.start_time) = DATE(i.invoice_date)
GROUP BY DATE(i.invoice_date);

CREATE UNIQUE INDEX idx_daily_stats_date ON daily_stats(date);

-- ============================================================
-- FUNCIONES DE MANTENIMIENTO
-- ============================================================

-- Función para crear particiones automáticamente (ejecutar mensualmente)
CREATE OR REPLACE FUNCTION create_next_month_partitions()
RETURNS void AS $$
DECLARE
    next_month DATE;
    month_after DATE;
    partition_name TEXT;
BEGIN
    next_month := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    month_after := next_month + INTERVAL '1 month';

    -- Crear particiones para appointments
    partition_name := 'appointments_' || TO_CHAR(next_month, 'YYYY_MM');
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF appointments FOR VALUES FROM (%L) TO (%L)',
        partition_name, next_month, month_after);

    -- Crear particiones para invoices
    partition_name := 'invoices_' || TO_CHAR(next_month, 'YYYY_MM');
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF invoices FOR VALUES FROM (%L) TO (%L)',
        partition_name, next_month, month_after);

    -- Crear particiones para stock_movements
    partition_name := 'stock_movements_' || TO_CHAR(next_month, 'YYYY_MM');
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF stock_movements FOR VALUES FROM (%L) TO (%L)',
        partition_name, next_month, month_after);
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- COMENTARIOS EN TABLAS PARA DOCUMENTACIÓN
-- ============================================================

COMMENT ON TABLE patients IS 'Tabla de pacientes optimizada para millones de registros con búsqueda fuzzy';
COMMENT ON TABLE appointments IS 'Citas médicas particionadas por mes para alto rendimiento';
COMMENT ON TABLE invoices IS 'Facturas particionadas por mes para reportes financieros rápidos';
COMMENT ON TABLE stock_movements IS 'Historial de movimientos de inventario particionado';
COMMENT ON TABLE medical_records IS 'Historia clínica particionada por año';
COMMENT ON TABLE audit_logs IS 'Logs de auditoría particionados trimestralmente';

-- ============================================================
-- CONFIGURACIONES DE RENDIMIENTO
-- ============================================================

-- Aumentar work_mem para queries complejas
-- ALTER DATABASE your_database_name SET work_mem = '256MB';

-- Nota: Storage parameters no se pueden aplicar a tablas particionadas
-- Deben aplicarse individualmente a cada partición si es necesario
-- Ejemplo para una partición:
-- ALTER TABLE appointments_2025_01 SET (
--     autovacuum_vacuum_scale_factor = 0.05,
--     autovacuum_analyze_scale_factor = 0.02
-- );

-- ============================================================
-- DATOS INICIALES
-- ============================================================

INSERT INTO roles (role_id, name) VALUES
    (1, 'admin'),
    (2, 'doctor'),
    (3, 'receptionist')
ON CONFLICT (role_id) DO NOTHING;

-- ============================================================
-- FIN DEL ESQUEMA
-- ============================================================
