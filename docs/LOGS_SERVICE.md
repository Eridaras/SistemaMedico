# 📊 Servicio de Logs - Documentación Técnica

Sistema centralizado de auditoría y registro de eventos para todos los microservicios.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Base de Datos](#base-de-datos)
- [API Endpoints](#api-endpoints)
- [Integración](#integración)
- [Niveles de Log](#niveles-de-log)
- [Mejores Prácticas](#mejores-prácticas)
- [Mantenimiento](#mantenimiento)

## Descripción

El Servicio de Logs proporciona un sistema centralizado para registrar todos los eventos, acciones y errores que ocurren en los microservicios del sistema médico. Es fundamental para:

- **Auditoría**: Rastrear quién hizo qué y cuándo
- **Debugging**: Identificar y diagnosticar problemas
- **Seguridad**: Detectar actividades sospechosas
- **Compliance**: Cumplir con normativas de registros médicos
- **Analytics**: Analizar patrones de uso del sistema

## Arquitectura

```
┌─────────────┐
│   Cliente   │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│   Servicio  │────>│ Logs Service │
│  (cualquiera)│     │  Puerto 5006 │
└─────────────┘     └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  PostgreSQL  │
                    │system_logs   │
                    └──────────────┘
```

### Componentes

1. **Logs Service** (Puerto 5006)
   - API REST para gestionar logs
   - No requiere autenticación para crear logs (permite registro de errores de autenticación)
   - Requiere autenticación para consultar logs

2. **Logger Utility** (`common/logger.py`)
   - Helper para que otros servicios registren eventos fácilmente
   - Envío asíncrono (no bloquea requests)
   - Manejo silencioso de errores (nunca rompe la aplicación principal)

3. **Tabla `system_logs`**
   - Almacenamiento persistente de todos los logs
   - Índices optimizados para consultas frecuentes
   - Retención configurable

## Base de Datos

### Esquema de la Tabla

```sql
CREATE TABLE system_logs (
    log_id BIGSERIAL PRIMARY KEY,
    service_name VARCHAR(50) NOT NULL,
    action VARCHAR(255) NOT NULL,
    user_id INT REFERENCES users(user_id),
    details TEXT,
    level VARCHAR(20) DEFAULT 'INFO',
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices
CREATE INDEX idx_logs_service_name ON system_logs(service_name);
CREATE INDEX idx_logs_level ON system_logs(level);
CREATE INDEX idx_logs_created_at ON system_logs(created_at);
CREATE INDEX idx_logs_user_id ON system_logs(user_id);
```

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `log_id` | BIGSERIAL | ID único del log |
| `service_name` | VARCHAR(50) | Nombre del microservicio (auth, inventario, etc.) |
| `action` | VARCHAR(255) | Descripción de la acción realizada |
| `user_id` | INT | ID del usuario que realizó la acción (nullable) |
| `details` | TEXT | Detalles adicionales, puede ser JSON |
| `level` | VARCHAR(20) | Nivel de severidad (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `ip_address` | VARCHAR(45) | IP del cliente (IPv4 o IPv6) |
| `created_at` | TIMESTAMP | Fecha y hora del evento |

## API Endpoints

### 1. Crear Log

**Endpoint**: `POST /api/logs/logs`

**Autenticación**: No requerida

**Body**:
```json
{
  "service_name": "auth",
  "action": "User login attempt",
  "user_id": 2,
  "details": "Successful login from Chrome browser",
  "level": "INFO",
  "ip_address": "192.168.1.100"
}
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Log created successfully",
  "data": {
    "log": {
      "log_id": 123,
      "service_name": "auth",
      "action": "User login attempt",
      "user_id": 2,
      "details": "Successful login from Chrome browser",
      "level": "INFO",
      "ip_address": "192.168.1.100",
      "created_at": "2025-01-10T15:30:00"
    }
  }
}
```

### 2. Listar Logs

**Endpoint**: `GET /api/logs/logs`

**Autenticación**: Requerida (JWT Token)

**Query Parameters**:
- `service_name`: Filtrar por servicio (ej: "auth", "inventario")
- `level`: Filtrar por nivel (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `user_id`: Filtrar por usuario
- `start_date`: Fecha inicio (ISO 8601)
- `end_date`: Fecha fin (ISO 8601)
- `page`: Número de página (default: 1)
- `per_page`: Registros por página (default: 20, max: 100)

**Ejemplo**:
```bash
GET /api/logs/logs?service_name=auth&level=ERROR&page=1&per_page=10
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": 456,
        "service_name": "auth",
        "action": "Failed login attempt",
        "user_id": null,
        "user_name": null,
        "user_email": null,
        "details": "Invalid password",
        "level": "ERROR",
        "ip_address": "192.168.1.200",
        "created_at": "2025-01-10T16:45:00"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 45,
      "pages": 5
    }
  }
}
```

### 3. Obtener Log Específico

**Endpoint**: `GET /api/logs/logs/{log_id}`

**Autenticación**: Requerida

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "log": {
      "log_id": 123,
      "service_name": "citas",
      "action": "Appointment created",
      "user_id": 2,
      "user_name": "Dr. Juan Pérez",
      "user_email": "dr.perez@clinica.com",
      "details": "{\"patient_id\": 45, \"appointment_id\": 123}",
      "level": "INFO",
      "ip_address": "192.168.1.100",
      "created_at": "2025-01-10T10:00:00"
    }
  }
}
```

### 4. Estadísticas de Logs

**Endpoint**: `GET /api/logs/logs/stats`

**Autenticación**: Requerida

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "stats": {
      "total": 12500,
      "by_service": [
        {"service_name": "auth", "count": 4500},
        {"service_name": "citas", "count": 3200},
        {"service_name": "inventario", "count": 2100}
      ],
      "by_level": [
        {"level": "INFO", "count": 10000},
        {"level": "WARNING", "count": 1500},
        {"level": "ERROR", "count": 900},
        {"level": "CRITICAL", "count": 100}
      ],
      "recent_errors": [
        {
          "log_id": 789,
          "service_name": "facturacion",
          "action": "Invoice calculation failed",
          "details": "Division by zero",
          "created_at": "2025-01-10T18:30:00"
        }
      ]
    }
  }
}
```

### 5. Limpiar Logs Antiguos

**Endpoint**: `POST /api/logs/logs/cleanup`

**Autenticación**: Requerida (Solo Admin)

**Body**:
```json
{
  "days": 90
}
```

**Respuesta**:
```json
{
  "success": true,
  "message": "Deleted 1250 logs older than 90 days",
  "data": {
    "deleted_count": 1250
  }
}
```

**Restricciones**:
- Mínimo 30 días (no se pueden borrar logs más recientes)

### 6. Health Check

**Endpoint**: `GET /api/logs/health`

**Autenticación**: No requerida

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "service": "logs"
  }
}
```

## Integración

### Desde Otros Servicios

```python
from common.logger import auth_logger, inventario_logger, citas_logger

# Ejemplo en Auth Service
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        # ... lógica de login ...

        # Log exitoso
        auth_logger.info(
            action=f"Usuario {user['email']} inició sesión",
            user_id=user['user_id'],
            details="Login exitoso",
            ip_address=request.remote_addr
        )

        return success_response(response_data, 'Login successful')

    except Exception as e:
        # Log de error
        auth_logger.error(
            action="Error en proceso de login",
            user_id=None,
            details=str(e),
            ip_address=request.remote_addr
        )
        return error_response('An error occurred during login', 500)
```

### Loggers Disponibles

```python
from common.logger import (
    auth_logger,              # Para auth_service
    inventario_logger,        # Para inventario_service
    historia_clinica_logger,  # Para historia_clinica_service
    facturacion_logger,       # Para facturacion_service
    citas_logger,             # Para citas_service
    logs_logger               # Para logs_service
)
```

## Niveles de Log

### DEBUG
**Cuándo usar**: Información detallada para debugging
```python
inventario_logger.debug(
    action="Stock check performed",
    details=f"Checked {product_count} products"
)
```

### INFO
**Cuándo usar**: Eventos normales del sistema
```python
citas_logger.info(
    action="Cita creada exitosamente",
    user_id=doctor_id,
    details=f"Patient ID: {patient_id}, Date: {appointment_date}"
)
```

### WARNING
**Cuándo usar**: Situaciones anormales pero no críticas
```python
inventario_logger.warning(
    action="Producto con stock bajo",
    details=f"Product {product_id} has only {stock} units left"
)
```

### ERROR
**Cuándo usar**: Errores que afectan funcionalidad pero no rompen el sistema
```python
facturacion_logger.error(
    action="Error al calcular IVA",
    user_id=user_id,
    details=f"Invalid subtotal: {subtotal}"
)
```

### CRITICAL
**Cuándo usar**: Errores graves que requieren atención inmediata
```python
auth_logger.critical(
    action="Fallo en conexión a base de datos",
    details="Database connection pool exhausted"
)
```

## Mejores Prácticas

### 1. Qué Registrar

**✅ SI registrar**:
- Login/logout de usuarios
- Creación/modificación/eliminación de registros
- Errores y excepciones
- Accesos denegados
- Cambios en configuración
- Transacciones financieras

**❌ NO registrar**:
- Contraseñas o datos sensibles
- Tokens de autenticación completos
- Información médica personal (HIPAA/GDPR)
- Números de tarjetas de crédito

### 2. Detalles Útiles

```python
# ✅ BUENO: Contexto claro
citas_logger.info(
    action="Cita cancelada por paciente",
    user_id=user_id,
    details=json.dumps({
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "cancellation_reason": reason,
        "cancelled_by": "patient"
    })
)

# ❌ MALO: Información insuficiente
citas_logger.info(action="Cita cancelada")
```

### 3. Niveles Apropiados

```python
# ✅ CORRECTO
inventario_logger.warning(
    action="Stock bajo detectado",
    details=f"Product {name} tiene solo {stock} unidades"
)

# ❌ INCORRECTO: Usar ERROR para advertencias
inventario_logger.error(
    action="Stock bajo detectado",  # Debería ser WARNING
    details=f"Product {name} tiene solo {stock} unidades"
)
```

## Mantenimiento

### Limpieza Automática

Recomendado ejecutar mensualmente:

```bash
curl -X POST http://localhost:5006/api/logs/logs/cleanup \
  -H "Authorization: Bearer {admin-token}" \
  -H "Content-Type: application/json" \
  -d '{"days": 90}'
```

### Monitoreo

Consultar errores recientes:

```bash
curl -X GET "http://localhost:5006/api/logs/logs?level=ERROR&page=1&per_page=20" \
  -H "Authorization: Bearer {token}"
```

### Análisis de Estadísticas

```bash
curl -X GET http://localhost:5006/api/logs/logs/stats \
  -H "Authorization: Bearer {token}"
```

## Configuración Avanzada

### Variables de Entorno

```env
# En .env
LOGS_SERVICE_PORT=5006
LOGS_SERVICE_URL=http://localhost:5006/api/logs

# Para cambiar el tiempo de retención por defecto
LOGS_RETENTION_DAYS=90

# Para habilitar/deshabilitar logging
ENABLE_LOGGING=true
```

### Personalizar Logger

```python
from common.logger import ServiceLogger

# Crear logger personalizado
custom_logger = ServiceLogger('my_custom_service')

custom_logger.info(
    action="Acción personalizada",
    details="Detalles específicos"
)
```

## Ejemplos de Uso Real

### Caso 1: Auditoría de Acceso a Historias Clínicas

```python
@historia_clinica_bp.route('/patients/<int:patient_id>/history', methods=['GET'])
@token_required
def get_medical_history(current_user, patient_id):
    try:
        history = MedicalHistoryModel.get_by_patient_id(patient_id)

        # Log de acceso a información sensible
        historia_clinica_logger.info(
            action=f"Acceso a historia clínica del paciente {patient_id}",
            user_id=current_user['user_id'],
            details=json.dumps({
                "patient_id": patient_id,
                "accessed_by": current_user['email'],
                "accessed_at": datetime.now().isoformat()
            }),
            ip_address=request.remote_addr
        )

        return success_response({'history': history})
    except Exception as e:
        historia_clinica_logger.error(
            action="Error al acceder a historia clínica",
            user_id=current_user['user_id'],
            details=str(e)
        )
        return error_response('Error retrieving medical history', 500)
```

### Caso 2: Rastreo de Transacciones Financieras

```python
@facturacion_bp.route('/invoices', methods=['POST'])
@token_required
def create_invoice(current_user):
    try:
        # ... crear factura ...

        facturacion_logger.info(
            action=f"Factura {invoice_number} creada",
            user_id=current_user['user_id'],
            details=json.dumps({
                "invoice_id": invoice['invoice_id'],
                "invoice_number": invoice_number,
                "patient_id": patient_id,
                "total_amount": float(total_amount),
                "created_by": current_user['email']
            }),
            ip_address=request.remote_addr
        )

        return success_response({'invoice': invoice}, 'Invoice created', 201)
    except Exception as e:
        facturacion_logger.critical(
            action="Error crítico al crear factura",
            user_id=current_user['user_id'],
            details=f"Error: {str(e)}. Data: {json.dumps(data)}",
            ip_address=request.remote_addr
        )
        return error_response('Error creating invoice', 500)
```

## Conclusión

El Servicio de Logs es una pieza fundamental del sistema que proporciona:

- ✅ Visibilidad completa de eventos del sistema
- ✅ Auditoría para cumplimiento normativo
- ✅ Debugging efectivo de problemas
- ✅ Análisis de patrones de uso
- ✅ Detección de seguridad

**Recuerda**: Un buen sistema de logs es la diferencia entre resolver un problema en minutos u horas.

---

**Desarrollado como parte del Sistema de Gestión Clínica**
