# 📅 Citas Service - Servicio de Agendamiento

Microservicio de gestión de citas médicas del Sistema Médico. Controla agendamiento, disponibilidad de médicos y estados de citas.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Estados de Citas](#-estados-de-citas)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Agendamiento de Citas**: Reserva de citas médicas con validación de disponibilidad
- **Gestión de Disponibilidad**: Control de horarios de médicos
- **Estados de Citas**: PENDING, CONFIRMED, COMPLETED, CANCELLED
- **Validación de Conflictos**: Prevención de doble agendamiento
- **Calendario Médico**: Vista de agenda por médico y fecha
- **Citas del Día**: Consulta rápida de citas programadas
- **Notificaciones**: Recordatorios de citas (integración futura)
- **Vinculación con Tratamientos**: Asociación de citas con servicios médicos

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5005/api/citas
```

### Documentación Interactiva
```
http://localhost:5005/docs
```

### Lista de Endpoints

#### Citas

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/appointments` | Listar todas las citas | Sí |
| `GET` | `/appointments/:id` | Obtener cita por ID | Sí |
| `POST` | `/appointments` | Crear nueva cita | Sí |
| `PUT` | `/appointments/:id` | Actualizar cita | Sí |
| `DELETE` | `/appointments/:id` | Cancelar cita | Sí |
| `GET` | `/appointments/today` | Citas del día actual | Sí |
| `GET` | `/appointments/doctor/:doctor_id` | Citas por médico | Sí |
| `GET` | `/appointments/patient/:patient_id` | Citas por paciente | Sí |
| `PATCH` | `/appointments/:id/status` | Cambiar estado de cita | Sí |

#### Disponibilidad

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/availability` | Obtener disponibilidad de médicos | Sí |
| `GET` | `/availability/:doctor_id` | Disponibilidad por médico y fecha | Sí |
| `POST` | `/availability/check` | Verificar disponibilidad de horario | Sí |

---

## 📊 Modelos de Datos

### Appointment (Cita)

```python
{
    "appointment_id": 1,
    "patient_id": 10,
    "patient_name": "Juan Pérez García",
    "doctor_id": 2,
    "doctor_name": "Dra. María González",
    "start_time": "2025-12-20T10:00:00Z",
    "end_time": "2025-12-20T10:30:00Z",
    "status": "CONFIRMED",
    "reason": "Consulta de control",
    "notes": "Paciente refiere mejoría",
    "treatment_id": 3,
    "created_at": "2025-12-17T10:00:00Z",
    "updated_at": "2025-12-18T15:30:00Z"
}
```

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `appointment_id` | int | ID único de la cita | PK, Autoincremental |
| `patient_id` | int | ID del paciente | FK a `patients` |
| `doctor_id` | int | ID del médico | FK a `users` |
| `start_time` | datetime | Inicio de la cita | ISO 8601 |
| `end_time` | datetime | Fin de la cita | > start_time |
| `status` | string | Estado de la cita | Ver estados |
| `reason` | string | Motivo de consulta | Requerido |
| `notes` | text | Notas adicionales | Opcional |
| `treatment_id` | int | Tratamiento asociado | FK a `treatments` |
| `created_at` | timestamp | Fecha de creación | Auto |
| `updated_at` | timestamp | Última actualización | Auto |

### Availability (Disponibilidad)

```python
{
    "doctor_id": 2,
    "doctor_name": "Dra. María González",
    "date": "2025-12-20",
    "available_slots": [
        {
            "start": "09:00",
            "end": "09:30",
            "available": true
        },
        {
            "start": "09:30",
            "end": "10:00",
            "available": true
        },
        {
            "start": "10:00",
            "end": "10:30",
            "available": false  # Ocupado
        }
    ]
}
```

---

## 🔄 Estados de Citas

### Flujo de Estados

```
PENDING → CONFIRMED → COMPLETED
   ↓
CANCELLED
```

### Descripción de Estados

| Estado | Descripción | Acciones Permitidas |
|--------|-------------|---------------------|
| **PENDING** | Cita creada, pendiente de confirmación | Confirmar, Cancelar, Editar |
| **CONFIRMED** | Cita confirmada por paciente/clínica | Completar, Cancelar, Editar |
| **COMPLETED** | Cita atendida | Ver historial, No editable |
| **CANCELLED** | Cita cancelada | Ver historial, No editable |

### Cambios de Estado

```bash
# Confirmar cita
PATCH /api/citas/appointments/1/status
{
  "status": "CONFIRMED"
}

# Completar cita
PATCH /api/citas/appointments/1/status
{
  "status": "COMPLETED"
}

# Cancelar cita
PATCH /api/citas/appointments/1/status
{
  "status": "CANCELLED",
  "cancellation_reason": "Paciente no pudo asistir"
}
```

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/citas_service
pip install -r ../requirements-base.txt
```

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db
JWT_SECRET_KEY=tu_clave_secreta
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
cd backend/citas_service
python app.py
```

El servicio estará disponible en `http://localhost:5005`

### Ejemplo de Creación de Cita

```bash
curl -X POST http://localhost:5005/api/citas/appointments \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 10,
    "doctor_id": 2,
    "start_time": "2025-12-20T10:00:00Z",
    "end_time": "2025-12-20T10:30:00Z",
    "reason": "Consulta de control",
    "treatment_id": 3
  }'
```

**Validaciones:**
- Verifica que el horario esté disponible
- Verifica que no haya conflicto con otras citas
- Calcula duración mínima: 15 minutos

### Ejemplo de Consulta de Citas del Día

```bash
curl -X GET http://localhost:5005/api/citas/appointments/today \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "date": "2025-12-20",
    "total_appointments": 8,
    "appointments": [
      {
        "appointment_id": 1,
        "patient_name": "Juan Pérez",
        "doctor_name": "Dra. María González",
        "start_time": "09:00",
        "status": "CONFIRMED",
        "reason": "Consulta general"
      }
    ]
  }
}
```

### Ejemplo de Verificación de Disponibilidad

```bash
curl -X POST http://localhost:5005/api/citas/availability/check \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": 2,
    "start_time": "2025-12-20T10:00:00Z",
    "end_time": "2025-12-20T10:30:00Z"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "available": false,
    "conflict": {
      "appointment_id": 5,
      "patient_name": "Carlos Ruiz",
      "start_time": "2025-12-20T10:00:00Z"
    }
  }
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_citas.py -v
```

### Casos de Prueba

- ✅ Creación de cita con validación de disponibilidad
- ✅ Prevención de doble agendamiento
- ✅ Cambio de estados de cita
- ✅ Consulta de citas por médico
- ✅ Consulta de citas por paciente
- ✅ Citas del día
- ✅ Validación de duración mínima
- ✅ Cancelación de citas

---

## ⏰ Configuración de Horarios

### Horario de Atención Predeterminado

```python
HORARIO_ATENCION = {
    "lunes": ["09:00-13:00", "15:00-19:00"],
    "martes": ["09:00-13:00", "15:00-19:00"],
    "miércoles": ["09:00-13:00", "15:00-19:00"],
    "jueves": ["09:00-13:00", "15:00-19:00"],
    "viernes": ["09:00-13:00", "15:00-19:00"],
    "sábado": ["09:00-13:00"],
    "domingo": []  # Cerrado
}
```

### Duración de Citas

- **Duración mínima**: 15 minutos
- **Duración estándar**: 30 minutos
- **Duración máxima**: 120 minutos (2 horas)

---

## 🔔 Notificaciones (Futuro)

### Recordatorios Automáticos

- **24 horas antes**: SMS/WhatsApp
- **2 horas antes**: Notificación push
- **Al confirmar**: Email de confirmación

### Integración con WhatsApp Business API

```python
# Ejemplo futuro
def send_appointment_reminder(appointment_id):
    """Enviar recordatorio por WhatsApp"""
    pass
```

---

## 🔗 Integración con Otros Servicios

### Historia Clínica Service
- Obtiene datos del paciente
- Crea notas clínicas al completar cita

### Inventario Service
- Vincula tratamientos con citas
- Descuenta stock de productos utilizados

### Auth Service
- Validación de médicos (role_id = 2)
- Permisos de edición por rol

---

## 🐛 Troubleshooting

### Error: "Time slot not available"
- El horario ya está ocupado
- Verifica disponibilidad antes de agendar

### Error: "Invalid doctor_id"
- El ID del médico no existe
- Solo usuarios con role_id = 2 (Médico) son válidos

### Error: "Invalid time range"
- `end_time` debe ser mayor que `start_time`
- Duración mínima: 15 minutos

### Error: "Past date not allowed"
- No se pueden crear citas en fechas pasadas
- Verifica la fecha actual

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5005/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Esquema de BD**: [../../docs/ESQUEMA_BASE_DATOS.md](../../docs/ESQUEMA_BASE_DATOS.md)

---

**Última actualización:** 2025-12-17
