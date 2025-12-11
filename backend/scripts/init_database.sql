-- Sistema de Gestión Clínica - Inicialización de Base de Datos
-- Motor: PostgreSQL (Neon.tech)

-- 1. Roles y Permisos (Configuración de Menú Dinámico)
CREATE TABLE IF NOT EXISTS roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    menu_config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Usuarios del Sistema
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    role_id INT REFERENCES roles(role_id),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inventario (Productos físicos)
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    sale_price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    stock_quantity INT DEFAULT 0,
    min_stock_alert INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. Tratamientos (Servicios intangibles)
CREATE TABLE IF NOT EXISTS treatments (
    treatment_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50),
    base_price DECIMAL(10, 2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 5. Receta del Tratamiento
CREATE TABLE IF NOT EXISTS treatment_recipes (
    recipe_id SERIAL PRIMARY KEY,
    treatment_id INT REFERENCES treatments(treatment_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id),
    quantity_needed INT NOT NULL DEFAULT 1,
    UNIQUE(treatment_id, product_id)
);

-- 6. Pacientes
CREATE TABLE IF NOT EXISTS patients (
    patient_id SERIAL PRIMARY KEY,
    doc_type VARCHAR(20) DEFAULT 'CEDULA',
    doc_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    address TEXT,
    birth_date DATE,
    gender VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Historia Clínica (Antecedentes)
CREATE TABLE IF NOT EXISTS medical_history (
    history_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id) ON DELETE CASCADE,
    allergies TEXT,
    pathologies TEXT,
    surgeries TEXT,
    family_history TEXT,
    blood_type VARCHAR(5),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. Citas (Agendamiento)
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES users(user_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Evolución / Notas de la Cita
CREATE TABLE IF NOT EXISTS clinical_notes (
    note_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    observations TEXT NOT NULL,
    diagnosis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Detalles Realizados (Disparador de Recetas)
CREATE TABLE IF NOT EXISTS appointment_treatments (
    detail_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    treatment_id INT REFERENCES treatments(treatment_id),
    price_at_moment DECIMAL(10, 2),
    quantity INT DEFAULT 1
);

-- 11. Consumo Extra (Items fuera de receta)
CREATE TABLE IF NOT EXISTS appointment_extras (
    extra_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    price_charged DECIMAL(10, 2) DEFAULT 0
);

-- 12. Gastos Operativos (Egresos fijos)
CREATE TABLE IF NOT EXISTS operational_expenses (
    expense_id SERIAL PRIMARY KEY,
    description VARCHAR(150) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    expense_date DATE DEFAULT CURRENT_DATE,
    category VARCHAR(50),
    registered_by INT REFERENCES users(user_id)
);

-- 13. Facturas (Ingresos)
CREATE TABLE IF NOT EXISTS invoices (
    invoice_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    appointment_id INT REFERENCES appointments(appointment_id),
    invoice_number VARCHAR(50),
    issue_date DATE DEFAULT CURRENT_DATE,
    subtotal DECIMAL(10, 2) DEFAULT 0,
    iva_rate DECIMAL(5, 2) DEFAULT 15.00,
    iva_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'DRAFT'
);

-- Insertar datos iniciales

-- Roles por defecto
INSERT INTO roles (name, menu_config) VALUES
('Admin', '{"menu": ["dashboard", "users", "patients", "appointments", "inventory", "billing", "reports"]}'::jsonb),
('Doctor', '{"menu": ["dashboard", "patients", "appointments", "medical_history"]}'::jsonb),
('Recepcion', '{"menu": ["dashboard", "patients", "appointments", "billing"]}'::jsonb)
ON CONFLICT (name) DO NOTHING;

-- Usuario administrador por defecto (password: admin123)
INSERT INTO users (role_id, full_name, email, password_hash)
SELECT role_id, 'Administrador', 'admin@clinica.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5U3rGpNnZnkiu'
FROM roles WHERE name = 'Admin'
ON CONFLICT (email) DO NOTHING;

-- Productos de ejemplo
INSERT INTO products (sku, name, description, cost_price, sale_price, stock_quantity, min_stock_alert) VALUES
('MED-001', 'Paracetamol 500mg', 'Analgesico y antipiretico', 0.50, 1.50, 100, 20),
('MED-002', 'Ibuprofeno 400mg', 'Antiinflamatorio', 0.75, 2.00, 80, 15),
('INS-001', 'Guantes de látex (caja)', 'Guantes desechables', 5.00, 10.00, 50, 10),
('INS-002', 'Jeringas 5ml (paquete)', 'Jeringas desechables', 3.00, 7.00, 60, 10)
ON CONFLICT (sku) DO NOTHING;

-- Tratamientos de ejemplo
INSERT INTO treatments (name, category, base_price, description) VALUES
('Consulta General', 'Medicina General', 25.00, 'Consulta medica general'),
('Limpieza Dental', 'Odontologia', 35.00, 'Limpieza y profilaxis dental'),
('Extracción Simple', 'Odontologia', 50.00, 'Extraccion dental simple')
ON CONFLICT DO NOTHING;
