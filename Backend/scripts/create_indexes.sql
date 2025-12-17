-- =====================================================
-- ÍNDICES OPTIMIZADOS PARA POSTGRESQL 16
-- Sistema Médico Integral - Sprint 3
-- =====================================================
-- Este script crea índices para optimizar las consultas más frecuentes
-- Ejecutar con: psql -d medical_db -f create_indexes.sql

-- =====================================================
-- ÍNDICES PARA TABLA: users
-- =====================================================
-- Búsqueda por email (login)
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Filtrado por estado activo
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active) WHERE is_active = true;

-- Búsqueda por rol
CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);

-- =====================================================
-- ÍNDICES PARA TABLA: patients (pacientes)
-- =====================================================
-- Búsqueda por cédula/RUC (identificación ecuatoriana)
CREATE INDEX IF NOT EXISTS idx_patients_identification ON patients(identification_number);
CREATE INDEX IF NOT EXISTS idx_patients_identification_type ON patients(identification_type);

-- Búsqueda por nombre (para autocomplete)
CREATE INDEX IF NOT EXISTS idx_patients_full_name_trgm ON patients USING gin (full_name gin_trgm_ops);

-- Filtrado por estado activo
CREATE INDEX IF NOT EXISTS idx_patients_is_active ON patients(is_active) WHERE is_active = true;

-- =====================================================
-- ÍNDICES PARA TABLA: appointments (citas)
-- =====================================================
-- Filtrado por fecha (consulta de agenda diaria)
CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);

-- Filtrado por médico y fecha (agenda del doctor)
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_date ON appointments(doctor_id, appointment_date);

-- Filtrado por paciente (historial de citas)
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments(patient_id);

-- Filtrado por estado
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Índice compuesto para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_appointments_date_status ON appointments(appointment_date, status);

-- =====================================================
-- ÍNDICES PARA TABLA: invoices (facturas)
-- =====================================================
-- Búsqueda por RUC del cliente
CREATE INDEX IF NOT EXISTS idx_invoices_client_ruc ON invoices(client_ruc);

-- Filtrado por fecha de emisión
CREATE INDEX IF NOT EXISTS idx_invoices_issue_date ON invoices(issue_date);

-- Búsqueda por número de factura
CREATE INDEX IF NOT EXISTS idx_invoices_number ON invoices(invoice_number);

-- Filtrado por estado (anulada, pagada, etc.)
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);

-- Índice para reportes mensuales
CREATE INDEX IF NOT EXISTS idx_invoices_year_month ON invoices(EXTRACT(YEAR FROM issue_date), EXTRACT(MONTH FROM issue_date));

-- =====================================================
-- ÍNDICES PARA TABLA: products (inventario)
-- =====================================================
-- Búsqueda por código de producto
CREATE INDEX IF NOT EXISTS idx_products_code ON products(product_code);

-- Búsqueda por nombre
CREATE INDEX IF NOT EXISTS idx_products_name_trgm ON products USING gin (name gin_trgm_ops);

-- Filtrado por categoría
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category_id);

-- Filtrado por stock bajo
CREATE INDEX IF NOT EXISTS idx_products_low_stock ON products(current_stock) WHERE current_stock <= minimum_stock;

-- =====================================================
-- ÍNDICES PARA TABLA: medical_history (historia clínica)
-- =====================================================
-- Búsqueda por paciente
CREATE INDEX IF NOT EXISTS idx_medical_history_patient ON medical_history(patient_id);

-- Ordenamiento por fecha
CREATE INDEX IF NOT EXISTS idx_medical_history_date ON medical_history(created_at DESC);

-- =====================================================
-- ÍNDICES PARA TABLA: treatments (tratamientos)
-- =====================================================
-- Búsqueda por nombre
CREATE INDEX IF NOT EXISTS idx_treatments_name ON treatments(name);

-- Filtrado por categoría
CREATE INDEX IF NOT EXISTS idx_treatments_category ON treatments(category);

-- Filtrado por activos
CREATE INDEX IF NOT EXISTS idx_treatments_active ON treatments(is_active) WHERE is_active = true;

-- =====================================================
-- ÍNDICES PARA TABLA: system_logs (auditoría)
-- =====================================================
-- Filtrado por fecha (para limpieza)
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system_logs(created_at);

-- Filtrado por usuario
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON system_logs(user_id);

-- Filtrado por nivel de log
CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level);

-- Filtrado por acción
CREATE INDEX IF NOT EXISTS idx_logs_action ON system_logs(action);

-- =====================================================
-- HABILITAR EXTENSIÓN pg_trgm (para búsqueda difusa)
-- =====================================================
-- Necesario para los índices gin_trgm_ops
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =====================================================
-- ANÁLISIS DE TABLAS (actualizar estadísticas)
-- =====================================================
ANALYZE users;
ANALYZE patients;
ANALYZE appointments;
ANALYZE invoices;
ANALYZE products;
ANALYZE medical_history;
ANALYZE treatments;
ANALYZE system_logs;

-- =====================================================
-- VERIFICACIÓN
-- =====================================================
-- Mostrar índices creados
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;
