-- Script para poblar datos de prueba iniciales
-- Autor: Sistema Médico
-- Fecha: 2025-12-12

BEGIN;

-- 1. Actualizar Doctor Principal
UPDATE users 
SET full_name = 'Dr. Michael Morales' 
WHERE email = 'admin@clinica.com';

-- 2. Pacientes
INSERT INTO patients (doc_type, doc_number, first_name, last_name, email, phone, address, birth_date, gender) VALUES
('CEDULA', '1712345678', 'Carlos', 'Ramirez', 'carlos.ramirez@email.com', '0998765432', 'Av. Amazonas N45-12', '1985-05-15', 'M'),
('CEDULA', '0987654321', 'Sofia', 'Vega', 'sofia.vega@email.com', '0987123456', 'Calle Larga 123', '1992-10-20', 'F'),
('CEDULA', '1801234567', 'Juan', 'Martinez', 'juan.martinez@email.com', '0976543210', 'Urb. El Bosque', '1978-03-12', 'M'),
('CEDULA', '0102030405', 'Lucia', 'Fernandez', 'lucia.fernandez@email.com', '0965432109', 'Sector La Mariscal', '2000-01-01', 'F'),
('CEDULA', '1122334455', 'Mateo', 'Castillo', 'mateo.castillo@email.com', '0954321098', 'Cumbayá Centro', '1995-07-30', 'M')
ON CONFLICT (doc_number) DO NOTHING;

-- 3. Productos / Medicamentos
INSERT INTO products (sku, name, description, cost_price, sale_price, stock_quantity, min_stock_alert) VALUES
('MED-001', 'Paracetamol 500mg', 'Analgésico y antipirético (Caja x20)', 1.50, 3.00, 100, 20),
('MED-002', 'Amoxicilina 500mg', 'Antibiótico de amplio espectro (Caja x15)', 3.25, 6.50, 50, 10),
('INS-001', 'Guantes de Nitrilo M', 'Caja de 100 guantes talla M', 5.00, 8.50, 200, 30),
('INS-002', 'Mascarilla Quirúrgica', 'Caja de 50 mascarillas', 2.50, 5.00, 300, 50),
('EQU-001', 'Termómetro Digital', 'Termómetro infrarrojo sin contacto', 15.00, 25.00, 15, 3)
ON CONFLICT (sku) DO NOTHING;

COMMIT;
