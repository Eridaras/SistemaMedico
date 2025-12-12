-- Agregar tabla de Logs al sistema
-- Sistema de Auditoría y Registro de Eventos

CREATE TABLE IF NOT EXISTS system_logs (
    log_id BIGSERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    action VARCHAR(255) NOT NULL,
    user_id INT REFERENCES users(user_id) ON DELETE SET NULL,
    details TEXT,
    level VARCHAR(20) DEFAULT 'INFO',
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_logs_service_name ON system_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_logs_level ON system_logs(level);
CREATE INDEX IF NOT EXISTS idx_logs_created_at ON system_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON system_logs(user_id);

-- Comentarios explicativos
COMMENT ON TABLE system_logs IS 'Tabla de auditoría y registro de eventos del sistema';
COMMENT ON COLUMN system_logs.service_name IS 'Nombre del microservicio: auth, inventario, historia_clinica, facturacion, citas, logs';
COMMENT ON COLUMN system_logs.action IS 'Descripción de la acción realizada';
COMMENT ON COLUMN system_logs.level IS 'Nivel de severidad: DEBUG, INFO, WARNING, ERROR, CRITICAL';
COMMENT ON COLUMN system_logs.details IS 'Información adicional sobre el evento, puede ser JSON';
