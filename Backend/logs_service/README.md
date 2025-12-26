# 📝 Logs Service - Servicio de Logs y Auditoría

Microservicio de gestión de logs y auditoría del Sistema Médico. Centraliza registros de eventos y errores.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Centralización de Logs**: Todos los servicios envían logs aquí
- **Niveles de Log**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Búsqueda y Filtrado**: Por servicio, nivel, fecha, usuario
- **Auditoría de Acciones**: Registro de acciones críticas
- **Monitoreo de Errores**: Detección temprana de problemas
- **Rotación de Logs**: Limpieza automática de logs antiguos
- **Formato JSON**: Logs estructurados para análisis
- **Exportación**: Descarga de logs en formatos CSV/JSON

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5006/api/logs
```

### Documentación Interactiva
```
http://localhost:5006/docs
```

### Lista de Endpoints

#### Logs

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/logs` | Listar todos los logs (paginado) | Sí (Admin) |
| `GET` | `/logs/:id` | Obtener log por ID | Sí (Admin) |
| `POST` | `/logs` | Crear nuevo log | Sí |
| `GET` | `/logs/search` | Buscar logs (query params) | Sí (Admin) |
| `GET` | `/logs/service/:service_name` | Logs por servicio | Sí (Admin) |
| `GET` | `/logs/level/:level` | Logs por nivel | Sí (Admin) |
| `DELETE` | `/logs/old` | Eliminar logs antiguos | Sí (Admin) |

#### Auditoría

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/audit` | Listar eventos de auditoría | Sí (Admin) |
| `POST` | `/audit` | Registrar evento de auditoría | Sí |
| `GET` | `/audit/user/:user_id` | Auditoría por usuario | Sí (Admin) |

#### Estadísticas

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/stats` | Estadísticas de logs | Sí (Admin) |
| `GET` | `/stats/errors` | Conteo de errores por servicio | Sí (Admin) |

---

## 📊 Modelos de Datos

### Log Entry

```python
{
    "log_id": 1,
    "timestamp": "2025-12-17T10:15:32.456Z",
    "service_name": "auth_service",
    "level": "INFO",
    "message": "User logged in successfully",
    "user_id": 5,
    "ip_address": "192.168.1.100",
    "endpoint": "/api/auth/login",
    "method": "POST",
    "status_code": 200,
    "duration_ms": 45,
    "metadata": {
        "user_email": "user@example.com",
        "role": "Admin"
    },
    "stack_trace": null
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `log_id` | int | ID único del log |
| `timestamp` | datetime | Fecha y hora del evento |
| `service_name` | string | Nombre del microservicio |
| `level` | string | Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `message` | text | Mensaje descriptivo |
| `user_id` | int | ID del usuario (si aplica) |
| `ip_address` | string | IP del cliente |
| `endpoint` | string | Endpoint llamado |
| `method` | string | Método HTTP |
| `status_code` | int | Código de respuesta HTTP |
| `duration_ms` | int | Duración de la petición en ms |
| `metadata` | jsonb | Datos adicionales en JSON |
| `stack_trace` | text | Stack trace si es error |

### Audit Event

```python
{
    "audit_id": 1,
    "timestamp": "2025-12-17T10:15:32.456Z",
    "user_id": 5,
    "action": "CREATE_PATIENT",
    "resource_type": "PATIENT",
    "resource_id": 123,
    "old_value": null,
    "new_value": {"name": "Juan Pérez", "cedula": "1234567890"},
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `audit_id` | int | ID único del evento |
| `timestamp` | datetime | Fecha y hora del evento |
| `user_id` | int | ID del usuario que realizó la acción |
| `action` | string | Acción realizada (CREATE, UPDATE, DELETE, etc.) |
| `resource_type` | string | Tipo de recurso afectado |
| `resource_id` | int | ID del recurso afectado |
| `old_value` | jsonb | Valor anterior (para UPDATE) |
| `new_value` | jsonb | Valor nuevo |
| `ip_address` | string | IP del cliente |
| `user_agent` | string | User agent del navegador |

---

## 🎯 Niveles de Log

### DEBUG
- Información detallada para diagnóstico
- Solo en ambiente de desarrollo
- Ejemplo: "Query SQL ejecutada: SELECT * FROM users"

### INFO
- Eventos informativos normales
- Confirmación de operaciones exitosas
- Ejemplo: "User logged in successfully"

### WARNING
- Advertencias que no impiden la operación
- Situaciones que requieren atención
- Ejemplo: "JWT token expires in 5 minutes"

### ERROR
- Errores que impiden una operación específica
- La aplicación continúa funcionando
- Ejemplo: "Failed to send email notification"

### CRITICAL
- Errores graves que pueden detener el sistema
- Requieren atención inmediata
- Ejemplo: "Database connection lost"

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/logs_service
pip install -r ../requirements-base.txt
```

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db
JWT_SECRET_KEY=tu_clave_secreta
LOG_RETENTION_DAYS=90  # Días para retener logs
```

### Migrar Base de Datos

```bash
cd backend
alembic upgrade head
```

---

## 💻 Uso

### Ejecutar el Servicio

```bash
cd backend/logs_service
python app.py
```

El servicio estará disponible en `http://localhost:5006`

### Ejemplo de Creación de Log desde Otro Servicio

```python
import requests

def log_event(level, message, **kwargs):
    """Enviar log al servicio de logs"""
    payload = {
        "service_name": "auth_service",
        "level": level,
        "message": message,
        **kwargs
    }
    requests.post(
        "http://localhost:5006/api/logs/logs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

# Uso
log_event("INFO", "User logged in", user_id=5, ip_address=request.remote_addr)
log_event("ERROR", "Database connection failed", stack_trace=traceback.format_exc())
```

### Ejemplo de Búsqueda de Logs

```bash
# Buscar logs de errores del último día
curl -X GET "http://localhost:5006/api/logs/logs/search?level=ERROR&since=2025-12-16" \
  -H "Authorization: Bearer TOKEN"

# Buscar logs de un servicio específico
curl -X GET "http://localhost:5006/api/logs/logs/service/auth_service" \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "total": 15,
    "page": 1,
    "per_page": 50,
    "logs": [
      {
        "log_id": 123,
        "timestamp": "2025-12-17T10:15:32Z",
        "level": "ERROR",
        "message": "Failed to connect to database",
        "service_name": "auth_service"
      }
    ]
  }
}
```

### Ejemplo de Registro de Auditoría

```python
# Desde otro servicio
def audit_log(action, resource_type, resource_id, user_id, **kwargs):
    """Registrar evento de auditoría"""
    payload = {
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "user_id": user_id,
        **kwargs
    }
    requests.post(
        "http://localhost:5006/api/logs/audit",
        json=payload,
        headers={"Authorization": f"Bearer {token}"}
    )

# Uso
audit_log(
    action="DELETE_PATIENT",
    resource_type="PATIENT",
    resource_id=123,
    user_id=5,
    old_value=patient_data,
    ip_address=request.remote_addr
)
```

---

## 📊 Dashboard de Logs

### Estadísticas

```bash
curl -X GET http://localhost:5006/api/logs/stats \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "total_logs_today": 1245,
    "errors_today": 12,
    "warnings_today": 45,
    "by_service": {
      "auth_service": 350,
      "inventario_service": 280,
      "citas_service": 190,
      "facturacion_service": 245,
      "historia_clinica_service": 180
    },
    "error_rate": 0.96
  }
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_logs.py -v
```

### Casos de Prueba

- ✅ Creación de logs con diferentes niveles
- ✅ Búsqueda de logs por servicio
- ✅ Búsqueda de logs por nivel
- ✅ Filtrado por rango de fechas
- ✅ Registro de eventos de auditoría
- ✅ Consulta de auditoría por usuario
- ✅ Eliminación de logs antiguos
- ✅ Estadísticas de logs

---

## 🔄 Rotación y Limpieza

### Configuración de Retención

Por defecto, los logs se mantienen por **90 días**. Configurar en `.env`:

```env
LOG_RETENTION_DAYS=90
```

### Limpieza Manual

```bash
curl -X DELETE "http://localhost:5006/api/logs/logs/old?days=90" \
  -H "Authorization: Bearer TOKEN"
```

### Limpieza Automática (Cron)

```bash
# Agregar a crontab para ejecutar diariamente a las 2 AM
0 2 * * * curl -X DELETE http://localhost:5006/api/logs/logs/old?days=90 -H "Authorization: Bearer TOKEN"
```

---

## 📁 Estructura de Logs en Disco

Además de la base de datos, los logs también se escriben en archivos:

```
backend/
├── logs/
│   ├── auth_service.log
│   ├── inventario_service.log
│   ├── citas_service.log
│   ├── facturacion_service.log
│   └── historia_clinica_service.log
```

### Formato de Log en Archivo

```json
{
  "timestamp": "2025-12-17T10:15:32.456Z",
  "service": "auth_service",
  "level": "INFO",
  "message": "User logged in",
  "user_id": 5
}
```

---

## 🔒 Seguridad

### Control de Acceso

- Solo **Admin** puede ver todos los logs
- Otros roles solo ven logs de sus propias acciones

### Datos Sensibles

- **NO** loguear contraseñas
- **NO** loguear datos de tarjetas de crédito
- **ENMASCARAR** datos sensibles (cédulas, emails)

### Ejemplo de Enmascaramiento

```python
def mask_cedula(cedula):
    """Enmascara cédula: 1234567890 -> 123****890"""
    return cedula[:3] + "****" + cedula[-3:]
```

---

## 🔗 Integración con Otros Servicios

### Todos los Servicios
- Envían logs automáticamente
- Middleware de logging en cada request
- Captura automática de errores

### Configuración en Otros Servicios

```python
# common/logging_middleware.py
import requests

class LoggingMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Log request
        start_time = time.time()

        # Execute request
        response = self.app(environ, start_response)

        # Log response
        duration = (time.time() - start_time) * 1000
        self.send_log(
            level="INFO",
            message=f"{environ['REQUEST_METHOD']} {environ['PATH_INFO']}",
            duration_ms=duration
        )

        return response
```

---

## 🐛 Troubleshooting

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo
- Verifica el `DATABASE_URL` en `.env`

### Error: "Logs table full"
- Ejecuta limpieza de logs antiguos
- Aumenta espacio en disco

### Warning: "High error rate detected"
- Revisa logs de nivel ERROR
- Identifica servicio problemático

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5006/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Estrategia de Pruebas**: [../../docs/ESTRATEGIA_PRUEBAS.md](../../docs/ESTRATEGIA_PRUEBAS.md)

---

**Última actualización:** 2025-12-17
