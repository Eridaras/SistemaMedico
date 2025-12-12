# Documentación Técnica: Base de Datos SaaS Gestión Clínica

**Versión:** 1.0  
**Motor:** PostgreSQL (Neon.tech)  
**Enfoque:** Multi-tenant (preparado), Normativa Ecuador, Automatización de Inventario.

---

## 1. Resumen de Arquitectura Lógica

El sistema se basa en 5 pilares fundamentales diseñados para automatizar la gestión médica y financiera:

1.  **Seguridad (RBAC):** Control de acceso basado en roles con menús dinámicos almacenados en JSON.
2.  **Motor de "Recetas":** Vinculación inteligente entre **Tratamientos** (Servicios) y **Productos** (Inventario). Un tratamiento descuenta automáticamente múltiples insumos.
3.  **Pacientes (Normativa Ecuador):** Estructura compatible con identificación fiscal (RUC/Cédula) y facturación electrónica.
4.  **Operaciones:** Ciclo completo de Cita -> Atención -> Consumo de Recursos -> Historial.
5.  **Financiero:** Cálculo de utilidad real comparando Ingresos (Facturas) vs. Egresos (Gastos Operativos + Costo de Ventas de Inventario).

---

## 2. Script SQL de Instalación

Copia y pega el siguiente código en el **SQL Editor de Neon**. El orden es estricto para respetar las claves foráneas.

### A. Módulo de Seguridad y Usuarios

```sql
-- 1. Roles y Permisos (Configuración de Menú Dinámico)
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL, -- Ej: 'Admin', 'Doctor', 'Recepcion'
    menu_config JSONB, -- Estructura del menú permitida (Rutas, Iconos)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Usuarios del Sistema
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    role_id INT REFERENCES roles(role_id),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inventario (Productos físicos)
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    sku VARCHAR(50) UNIQUE, 
    name VARCHAR(150) NOT NULL,
    description TEXT,
    cost_price DECIMAL(10, 2) NOT NULL DEFAULT 0, -- Costo de compra (para Egresos)
    sale_price DECIMAL(10, 2) NOT NULL DEFAULT 0, -- Precio si se vende suelto
    stock_quantity INT DEFAULT 0,
    min_stock_alert INT DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. Tratamientos (Servicios intangibles)
CREATE TABLE treatments (
    treatment_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    category VARCHAR(50), -- Ej: 'Odontología', 'Medicina General'
    base_price DECIMAL(10, 2) NOT NULL, -- Precio base del servicio
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE
);

-- 5. Receta del Tratamiento (TABLA CLAVE)
-- Define qué insumos consume cada tratamiento automáticamente
CREATE TABLE treatment_recipes (
    recipe_id SERIAL PRIMARY KEY,
    treatment_id INT REFERENCES treatments(treatment_id) ON DELETE CASCADE,
    product_id INT REFERENCES products(product_id),
    quantity_needed INT NOT NULL DEFAULT 1, 
    UNIQUE(treatment_id, product_id)
);

-- 6. Pacientes
CREATE TABLE patients (
    patient_id SERIAL PRIMARY KEY,
    -- Identificación Fiscal
    doc_type VARCHAR(20) DEFAULT 'CEDULA', -- RUC, CEDULA, PASAPORTE
    doc_number VARCHAR(20) UNIQUE NOT NULL, -- VARCHAR para soportar ceros a la izquierda
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    
    -- Contacto y Facturación
    email VARCHAR(150), 
    phone VARCHAR(20),
    address TEXT,
    
    -- Demográficos
    birth_date DATE,
    gender VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Historia Clínica (Antecedentes)
CREATE TABLE medical_history (
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
CREATE TABLE appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    doctor_id INT REFERENCES users(user_id),
    
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    
    status VARCHAR(20) DEFAULT 'PENDING', -- PENDING, CONFIRMED, COMPLETED, CANCELLED
    reason TEXT, 
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Evolución / Notas de la Cita
CREATE TABLE clinical_notes (
    note_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    observations TEXT NOT NULL, -- Nota de evolución
    diagnosis TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Detalles Realizados (Disparador de Recetas)
CREATE TABLE appointment_treatments (
    detail_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    treatment_id INT REFERENCES treatments(treatment_id),
    price_at_moment DECIMAL(10, 2), 
    quantity INT DEFAULT 1
);

-- 11. Consumo Extra (Items fuera de receta)
CREATE TABLE appointment_extras (
    extra_id SERIAL PRIMARY KEY,
    appointment_id INT REFERENCES appointments(appointment_id),
    product_id INT REFERENCES products(product_id),
    quantity INT NOT NULL,
    price_charged DECIMAL(10, 2) DEFAULT 0 -- 0 si es consumo interno, >0 si se cobra
);

-- 12. Gastos Operativos (Egresos fijos)
CREATE TABLE operational_expenses (
    expense_id SERIAL PRIMARY KEY,
    description VARCHAR(150) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    expense_date DATE DEFAULT CURRENT_DATE,
    category VARCHAR(50), 
    registered_by INT REFERENCES users(user_id)
);

-- 13. Facturas (Ingresos)
CREATE TABLE invoices (
    invoice_id SERIAL PRIMARY KEY,
    patient_id INT REFERENCES patients(patient_id),
    appointment_id INT REFERENCES appointments(appointment_id), -- Opcional
    
    invoice_number VARCHAR(50), -- Secuencial SRI
    issue_date DATE DEFAULT CURRENT_DATE,
    
    subtotal DECIMAL(10, 2) DEFAULT 0,
    iva_rate DECIMAL(5, 2) DEFAULT 15.00,
    iva_amount DECIMAL(10, 2) DEFAULT 0,
    total_amount DECIMAL(10, 2) DEFAULT 0,
    
    status VARCHAR(20) DEFAULT 'DRAFT' -- DRAFT, ISSUED, PAID, ANNULLED
);