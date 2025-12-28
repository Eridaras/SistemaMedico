# Google Calendar y Sistema de Notificaciones

**Fecha:** 2025-12-28
**Versión:** 2.0

---

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Google Calendar - Integración Automática](#google-calendar---integración-automática)
3. [Sistema de Notificaciones](#sistema-de-notificaciones)
4. [Widgets del Dashboard](#widgets-del-dashboard)
5. [Configuración](#configuración)
6. [Endpoints API](#endpoints-api)
7. [Uso del Sistema](#uso-del-sistema)

---

## Descripción General

Este documento describe las nuevas funcionalidades implementadas para mejorar la gestión de citas y el control de inventario:

✅ **Integración Automática con Google Calendar**
✅ **Sistema de Notificaciones en Tiempo Real**
✅ **Alertas de Stock Bajo**
✅ **Recordatorios de Citas Diarias**
✅ **Panel de Notificaciones en el Header**
✅ **Widgets Informativos en el Dashboard**

---

## Google Calendar - Integración Automática

### Características

- **Sincronización Bidireccional**: Las citas creadas en el sistema se sincronizan automáticamente con Google Calendar
- **Recordatorios Automáticos**:
  - 📧 Email 24 horas antes
  - 🔔 Popup 1 hora antes
  - 🔔 Popup 10 minutos antes
- **Actualizaciones en Tiempo Real**: Los cambios en las citas se reflejan automáticamente en Google Calendar
- **Eliminación Sincronizada**: Al cancelar una cita, también se elimina del calendario

### Módulo Principal

**Ubicación**: `backend/common/google_calendar.py`

#### Clases Principales

##### 1. `GoogleCalendarService`

Maneja la autenticación OAuth 2.0 y operaciones CRUD con Google Calendar.

```python
from common.google_calendar import GoogleCalendarService

# Inicializar para un doctor
calendar = GoogleCalendarService(user_id=doctor_id)

# Autenticar (solo la primera vez)
if calendar.authenticate():
    # Crear evento
    event = calendar.create_event(
        summary="Cita: Juan Pérez",
        start_time="2025-12-28T10:00:00",
        end_time="2025-12-28T11:00:00",
        description="Consulta general",
        attendees=["paciente@example.com"]
    )

    print(f"Evento creado: {event['event_id']}")
```

**Métodos disponibles**:

- `authenticate(credentials_path)`: Autenticar con OAuth 2.0
- `create_event(...)`: Crear nuevo evento
- `update_event(event_id, ...)`: Actualizar evento existente
- `delete_event(event_id)`: Eliminar evento
- `get_events(time_min, time_max)`: Obtener eventos en un rango
- `sync_appointment_to_calendar(appointment_data)`: Sincronizar cita completa

##### 2. `CalendarSyncManager`

Maneja la sincronización automática entre la base de datos y Google Calendar.

```python
from common.google_calendar import CalendarSyncManager

# Sincronizar nueva cita
google_event_id = CalendarSyncManager.sync_appointment_create(
    appointment_id=123,
    doctor_id=456
)

# Actualizar cita sincronizada
CalendarSyncManager.sync_appointment_update(
    appointment_id=123,
    doctor_id=456
)

# Eliminar de Google Calendar
CalendarSyncManager.sync_appointment_delete(
    appointment_id=123,
    doctor_id=456,
    google_event_id="abc123xyz"
)
```

### Integración Automática en Citas

La sincronización ocurre automáticamente cuando:

1. **Se crea una cita** → Se crea evento en Google Calendar
2. **Se actualiza una cita** → Se actualiza el evento
3. **Se cancela una cita** → Se elimina el evento

**Código en** `backend/citas_service/routes.py`:

```python
# Al crear una cita
appointment = AppointmentModel.create(...)

# Sync automático (no bloquea la respuesta)
try:
    from common.google_calendar import CalendarSyncManager
    CalendarSyncManager.sync_appointment_create(
        appointment['appointment_id'],
        doctor_id
    )
except Exception as e:
    print(f"Google Calendar sync warning: {str(e)}")
```

### Configuración de Google Calendar

#### 1. Obtener Credenciales de Google

1. Ir a [Google Cloud Console](https://console.cloud.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar **Google Calendar API**
4. Crear credenciales OAuth 2.0:
   - Tipo: Aplicación de escritorio
   - Descargar el archivo JSON
5. Renombrar el archivo a `credentials.json`
6. Colocar en `backend/credentials.json`

#### 2. Primera Autenticación

La primera vez que un doctor usa la integración:

```bash
cd backend
python -c "from common.google_calendar import GoogleCalendarService; service = GoogleCalendarService(1); service.authenticate()"
```

Esto abrirá un navegador para autorizar la aplicación. Los tokens se guardarán en `backend/tokens/user_{id}_token.pickle`.

#### 3. Variables de Entorno

En `backend/.env`:

```bash
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
```

### Base de Datos

Se agregó el campo `google_event_id` a la tabla `appointments`:

```sql
ALTER TABLE appointments ADD COLUMN google_event_id VARCHAR(255);
CREATE INDEX idx_appointments_google_event_id ON appointments(google_event_id);
```

---

## Sistema de Notificaciones

### Nuevo Servicio: Notifications Service

**Puerto**: 5007
**Ubicación**: `backend/notifications_service/`

#### Endpoints Principales

##### Notificaciones del Usuario

```bash
# Obtener notificaciones
GET /api/notifications/notifications?limit=20&unread_only=false
Authorization: Bearer {token}

# Marcar como leída
PATCH /api/notifications/notifications/{log_id}/read
Authorization: Bearer {token}
```

##### Alertas de Stock Bajo

```bash
# Obtener productos con stock bajo
GET /api/notifications/low-stock
Authorization: Bearer {token}

# Enviar alertas a todos los admins/doctores
POST /api/notifications/low-stock/alerts/send
Authorization: Bearer {token}
```

##### Recordatorios de Citas

```bash
# Citas del día actual
GET /api/notifications/appointments/today
Authorization: Bearer {token}

# Citas próximas (7 días)
GET /api/notifications/appointments/upcoming?days=7
Authorization: Bearer {token}

# Resumen diario
GET /api/notifications/daily-summary
Authorization: Bearer {token}

# Enviar resúmenes a todos los doctores
POST /api/notifications/daily-summary/send
Authorization: Bearer {token}
```

##### Preferencias de Notificaciones

```bash
# Obtener preferencias
GET /api/notifications/preferences
Authorization: Bearer {token}

# Actualizar preferencias
PUT /api/notifications/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "low_stock_notifications": true,
  "appointment_reminders": true,
  "daily_summary_enabled": true,
  "summary_time": "08:00:00"
}
```

### Módulo de Servicio de Notificaciones

**Ubicación**: `backend/common/notification_service.py`

#### Métodos Principales

```python
from common.notification_service import NotificationService

# Obtener productos con stock bajo
low_stock = NotificationService.get_low_stock_products()
# Returns: [{ product_id, name, current_stock, minimum_stock, units_needed, ... }]

# Citas del día para un doctor
today = NotificationService.get_today_appointments_for_doctor(doctor_id=5)
# Returns: { count, appointments: [...], date }

# Crear notificación
log_id = NotificationService.create_notification(
    user_id=5,
    notification_type='low_stock',
    title='⚠️ Alerta de Stock Bajo',
    message='Hay 3 productos con stock bajo',
    metadata={'product_count': 3}
)

# Generar resumen diario
summary = NotificationService.generate_daily_summary_for_doctor(doctor_id=5)
# Returns: {
#   appointments_count, appointments[],
#   low_stock_count, low_stock_items[],
#   summary_message
# }

# Enviar alertas automáticas
notifications_sent = NotificationService.send_low_stock_alerts()
summaries_sent = NotificationService.send_daily_summaries()
```

### Tablas de Base de Datos

#### `notification_preferences`

```sql
CREATE TABLE notification_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    low_stock_notifications BOOLEAN DEFAULT TRUE,
    appointment_reminders BOOLEAN DEFAULT TRUE,
    daily_summary_enabled BOOLEAN DEFAULT TRUE,
    summary_time TIME DEFAULT '08:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);
```

#### `notification_logs`

```sql
CREATE TABLE notification_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    metadata JSONB
);
```

Tipos de notificación:
- `low_stock`: Alerta de inventario bajo
- `appointment_reminder`: Recordatorio de cita
- `daily_summary`: Resumen diario

---

## Widgets del Dashboard

### 1. Panel de Notificaciones (Header)

**Ubicación**: `Frontend/src/components/notifications-panel.tsx`

**Características**:
- 🔔 Icono de campana con badge de cantidad
- ⏱️ Actualización cada 60 segundos
- ✅ Marcar como leída individualmente
- 📱 Responsive con scroll
- 🎨 Iconos por tipo de notificación

**Uso**:

```tsx
import { NotificationsPanel } from '@/components/notifications-panel';

// En el layout
<NotificationsPanel />
```

### 2. Widget de Citas del Día

**Ubicación**: `Frontend/src/components/today-appointments-widget.tsx`

**Características**:
- 📅 Muestra todas las citas del día para el doctor autenticado
- ⏰ Hora de inicio y fin
- 👤 Nombre del paciente
- 📞 Teléfono clickeable
- 📝 Motivo de consulta
- 🎨 Estados con colores:
  - Verde: Confirmada
  - Amarillo: Pendiente
  - Azul: Completada
  - Rojo: Cancelada
- 🔄 Actualización cada 5 minutos

**Uso**:

```tsx
import { TodayAppointmentsWidget } from '@/components/today-appointments-widget';

<TodayAppointmentsWidget />
```

### 3. Widget de Stock Bajo

**Ubicación**: `Frontend/src/components/low-stock-widget.tsx`

**Características**:
- 📦 Lista de productos con stock bajo
- ⚠️ Severidad por colores:
  - Rojo: Stock agotado (0 unidades)
  - Naranja: Stock crítico (≤50% del mínimo)
  - Amarillo: Stock bajo
- 📊 Muestra: stock actual, mínimo, unidades necesarias
- 🔄 Actualización cada 10 minutos
- 🔗 Botón directo al inventario

**Uso**:

```tsx
import { LowStockWidget } from '@/components/low-stock-widget';

<LowStockWidget />
```

---

## Configuración

### Backend

#### 1. Instalar Dependencias de Google Calendar

```bash
cd backend
pip install -r requirements-calendar.txt
```

Contenido de `requirements-calendar.txt`:
```
google-auth==2.28.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.118.0
```

#### 2. Ejecutar Migraciones

```bash
cd backend
python scripts/run_calendar_migration.py
```

Esto crea:
- Campo `google_event_id` en `appointments`
- Campo `google_calendar_sync` en `users`
- Tabla `notification_preferences`
- Tabla `notification_logs`

#### 3. Actualizar .env

```bash
# Service Ports
NOTIFICATIONS_SERVICE_PORT=5007

# Service URLs
NOTIFICATIONS_SERVICE_URL=http://localhost:5007/api/notifications

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_PATH=credentials.json
```

#### 4. Iniciar Notifications Service

```bash
cd backend
python notifications_service/app.py
```

### Frontend

#### 1. Actualizar Variables de Entorno

En `Frontend/.env.local`:

```bash
NOTIFICATIONS_SERVICE_URL=http://localhost:5007/api/notifications
```

#### 2. Verificar Proxy Routes

El proxy ya está configurado en:
`Frontend/src/app/api/notifications/[...path]/route.ts`

---

## Endpoints API

### Resumen de Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/notifications/notifications` | Obtener notificaciones del usuario |
| PATCH | `/api/notifications/notifications/:id/read` | Marcar notificación como leída |
| GET | `/api/notifications/low-stock` | Productos con stock bajo |
| POST | `/api/notifications/low-stock/alerts/send` | Enviar alertas de stock (admin) |
| GET | `/api/notifications/appointments/today` | Citas del día |
| GET | `/api/notifications/appointments/upcoming` | Citas próximas |
| GET | `/api/notifications/daily-summary` | Resumen diario |
| POST | `/api/notifications/daily-summary/send` | Enviar resúmenes (admin) |
| GET | `/api/notifications/preferences` | Obtener preferencias |
| PUT | `/api/notifications/preferences` | Actualizar preferencias |

### Ejemplos de Respuestas

#### GET /api/notifications/notifications

```json
{
  "success": true,
  "data": {
    "notifications": [
      {
        "log_id": 1,
        "notification_type": "low_stock",
        "title": "⚠️ Alerta de Stock Bajo (3 productos)",
        "message": "Hay 3 producto(s) con stock bajo:\n\n• Paracetamol 500mg: 5 unidades (necesita 15 más)\n• Gasas estériles: 2 unidades (necesita 8 más)",
        "sent_at": "2025-12-28T08:00:00Z",
        "read_at": null,
        "metadata": {"product_count": 3}
      }
    ],
    "unread_count": 12
  }
}
```

#### GET /api/notifications/appointments/today

```json
{
  "success": true,
  "data": {
    "count": 3,
    "date": "2025-12-28",
    "appointments": [
      {
        "appointment_id": 45,
        "start_time": "2025-12-28T09:00:00Z",
        "end_time": "2025-12-28T10:00:00Z",
        "status": "CONFIRMED",
        "reason": "Consulta general",
        "patient_name": "Juan Pérez",
        "patient_phone": "0998765432",
        "patient_email": "juan@example.com"
      }
    ]
  }
}
```

#### GET /api/notifications/low-stock

```json
{
  "success": true,
  "data": {
    "count": 5,
    "products": [
      {
        "product_id": 10,
        "sku": "MED-001",
        "name": "Paracetamol 500mg",
        "current_stock": 5,
        "minimum_stock": 20,
        "units_needed": 15,
        "category": "Medicamentos",
        "type": "medicamento"
      }
    ]
  }
}
```

---

## Uso del Sistema

### Para Doctores

#### 1. Ver Citas del Día

Al iniciar sesión, el dashboard muestra automáticamente:
- Widget "Citas de Hoy" con todas las citas programadas
- Información de cada paciente
- Hora de cada cita
- Estado de las citas

#### 2. Recibir Notificaciones

- 🔔 El icono de campana en el header muestra notificaciones no leídas
- Click para ver todas las notificaciones
- Click en el check ✅ para marcar como leída

#### 3. Configurar Preferencias

1. Ir a Configuración
2. Buscar "Notificaciones"
3. Activar/Desactivar:
   - Alertas de stock bajo
   - Recordatorios de citas
   - Resumen diario
4. Configurar hora del resumen diario (ej: 08:00 AM)

#### 4. Google Calendar

**Primera vez**:
1. Admin ejecuta autenticación OAuth
2. Autoriza acceso a Google Calendar
3. Token se guarda automáticamente

**Uso diario**:
- Las citas se sincronizan automáticamente
- Los cambios se reflejan en ambos sistemas
- Los recordatorios llegan por email y notificaciones

### Para Administradores

#### 1. Monitorear Stock Bajo

- Dashboard muestra widget de Stock Bajo
- Click en "Ir a Inventario" para ver detalles
- Editar productos desde la página de inventario

#### 2. Enviar Alertas Manuales

```bash
# Enviar alertas de stock bajo
POST /api/notifications/low-stock/alerts/send

# Enviar resúmenes diarios
POST /api/notifications/daily-summary/send
```

#### 3. Ver Notificaciones de Todos

Los administradores pueden:
- Ver resumen de notificaciones enviadas
- Monitorear stock crítico
- Gestionar inventario proactivamente

### Automatización (Opcional)

Para enviar notificaciones automáticamente cada día:

#### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar a las 8 AM diario)
0 8 * * * curl -X POST http://localhost:5007/api/notifications/daily-summary/send \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

#### Windows (Task Scheduler)

1. Crear script `send_daily_summary.bat`:
```batch
curl -X POST http://localhost:5007/api/notifications/daily-summary/send ^
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

2. Crear tarea programada:
   - Trigger: Diario a las 8:00 AM
   - Acción: Ejecutar `send_daily_summary.bat`

---

## Próximos Pasos

### Mejoras Sugeridas

1. **Notificaciones Push** (Opcional)
   - Integrar Firebase Cloud Messaging
   - Enviar push notifications al navegador

2. **Email Notifications** (Opcional)
   - Enviar emails para alertas críticas
   - Usar SendGrid o AWS SES

3. **SMS Notifications** (Opcional)
   - Enviar SMS para recordatorios de citas
   - Usar Twilio

4. **Dashboard de Métricas**
   - Gráfica de notificaciones enviadas
   - Tasa de apertura de notificaciones
   - Productos más frecuentes en alertas

---

## Soporte

Para problemas o preguntas:

1. **Errores de Google Calendar**:
   - Verificar que `credentials.json` existe
   - Re-autenticar con `python -c "..."`
   - Revisar logs en `backend/logs/`

2. **Notificaciones no aparecen**:
   - Verificar que Notifications Service está corriendo (puerto 5007)
   - Verificar preferencias del usuario
   - Revisar logs del servicio

3. **Widgets no cargan**:
   - Verificar permisos del usuario (solo doctores ven citas del día)
   - Revisar errores en consola del navegador
   - Verificar que endpoints responden correctamente

---

**Última actualización**: 2025-12-28
**Autor**: Sistema Médico - Clínica Bienestar
**Versión**: 2.0
