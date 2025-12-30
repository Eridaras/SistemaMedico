# Guía de Configuración - Sistema de Recordatorios

## 📋 Descripción

Sistema completo de recordatorios automáticos para citas médicas mediante **Email** y **WhatsApp**. Los recordatorios se envían automáticamente según la configuración del usuario (1 hora, 3 horas, 24 horas, 72 horas antes, etc.).

## ✨ Características

- ✅ Recordatorios por **Email** con plantillas HTML profesionales
- ✅ Recordatorios por **WhatsApp** mediante Twilio API
- ✅ Configuración flexible de **horarios** (1h, 3h, 6h, 12h, 24h, 48h, 72h antes)
- ✅ **Múltiples recordatorios** por cita (ej: 72h y 3h antes)
- ✅ **Horario silencioso** configurable (no enviar de 22:00 a 08:00)
- ✅ **Días de envío** configurables (de lunes a domingo)
- ✅ **Logs de auditoría** de todos los recordatorios enviados
- ✅ Interfaz gráfica de configuración en `/settings`
- ✅ Envío manual de recordatorios para pruebas

## 🚀 Instalación Rápida (5 minutos)

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements-reminders.txt
```

Esto instalará:
- `twilio==9.0.0` (WhatsApp API)

### 2. Ejecutar Migración de Base de Datos

```bash
cd backend
python scripts/run_reminder_migration.py
```

✅ Esto crea las tablas:
- `reminder_settings` - Configuración por usuario
- `reminder_logs` - Historial de recordatorios enviados

### 3. Configurar Variables de Entorno

Editar `backend/.env` (o crear desde `.env.example`):

```bash
# =====================================================
# EMAIL CONFIGURATION (SMTP)
# =====================================================
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password
FROM_EMAIL=clinica@ejemplo.com
FROM_NAME=Clínica Bienestar

# =====================================================
# WHATSAPP CONFIGURATION (Twilio)
# =====================================================
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### 4. Iniciar Notifications Service

```bash
cd backend
python notifications_service/app.py
```

✅ El servicio debe iniciar en puerto **5007**

### 5. Verificar Frontend

```bash
cd Frontend
npm run dev
```

Abrir http://localhost:9002 y navegar a **Configuración** (Settings)

---

## 📧 Configuración de Email (Gmail)

### Opción 1: Gmail con App Password (Recomendado)

1. **Habilitar 2FA** en tu cuenta de Google:
   - https://myaccount.google.com/security

2. **Crear App Password**:
   - Ir a https://myaccount.google.com/apppasswords
   - Seleccionar "Correo" y "Otro (nombre personalizado)"
   - Copiar la contraseña de 16 caracteres

3. **Configurar `.env`**:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # App Password de 16 caracteres
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=Clínica Bienestar
```

### Opción 2: Otro Proveedor SMTP

**SendGrid:**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=tu_sendgrid_api_key
```

**Mailgun:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@tu-dominio.mailgun.org
SMTP_PASSWORD=tu_mailgun_password
```

**Outlook/Office365:**
```bash
SMTP_HOST=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USER=tu-email@outlook.com
SMTP_PASSWORD=tu_password
```

---

## 📱 Configuración de WhatsApp (Twilio)

### Paso 1: Crear Cuenta Twilio

1. Ir a https://www.twilio.com/try-twilio
2. Registrarse (cuenta gratuita incluye $15 USD de crédito)
3. Verificar número de teléfono

### Paso 2: Configurar WhatsApp Sandbox

1. En el Dashboard de Twilio, ir a:
   **Messaging → Try it out → Send a WhatsApp message**

2. Copiar el código de sandbox (ej: `join yellow-tiger`)

3. Desde WhatsApp, enviar ese código a:
   **+1 415 523 8886** (número sandbox de Twilio)

4. Recibirás confirmación de activación

### Paso 3: Obtener Credenciales

1. En Dashboard de Twilio, ir a **Account → API keys & tokens**

2. Copiar:
   - **Account SID** (ej: `AC1234567890abcdef...`)
   - **Auth Token** (revelar y copiar)

3. El número WhatsApp sandbox es:
   - `whatsapp:+14155238886`

### Paso 4: Configurar `.env`

```bash
TWILIO_ACCOUNT_SID=AC1234567890abcdef...
TWILIO_AUTH_TOKEN=1234567890abcdef...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Paso 5: Registrar Números de Prueba

Cada paciente que recibirá WhatsApp debe:
1. Enviar `join <tu-codigo-sandbox>` al número +1 415 523 8886
2. Confirmar activación

⚠️ **Limitaciones Sandbox:**
- Solo números registrados en sandbox
- Prefijo automático en mensajes
- Para producción, necesitas número WhatsApp Business aprobado

### Paso 6: Producción (Opcional)

Para eliminar limitaciones:
1. Solicitar número WhatsApp Business
2. Esperar aprobación de Twilio (1-2 semanas)
3. Actualizar `TWILIO_WHATSAPP_NUMBER` con tu número

---

## 🎨 Plantillas de Mensajes

### Email Template

Ubicación: `backend/common/email_service.py`

**Características:**
- HTML responsive con inline CSS
- Header con gradiente azul
- Tabla de detalles de cita
- Sección de notas importantes
- Información de contacto
- Botón de acción
- Versión plain text alternativa

**Variables disponibles:**
```python
{
    'patient_name': 'Juan Pérez',
    'doctor_name': 'Dra. María López',
    'appointment_date': '2025-01-15',
    'appointment_time': '10:30',
    'reason': 'Consulta de rutina',
    'clinic_address': 'Av. Principal 123, Quito',
    'clinic_phone': '02-123-4567'
}
```

### WhatsApp Template

Ubicación: `backend/common/whatsapp_service.py`

**Características:**
- Formato conciso optimizado para móvil
- Emojis para mejor legibilidad
- Markdown bold para destacar
- Información de contacto

**Ejemplo:**
```
🏥 *Clínica Bienestar*
_Recordatorio de Cita Médica_

Hola *Juan Pérez*,

Le recordamos que tiene una cita médica programada *mañana*.

📅 *Fecha:* 15/01/2025
⏰ *Hora:* 10:30
👨‍⚕️ *Doctor:* Dra. María López
📋 *Motivo:* Consulta de rutina

📍 *Dirección:* Av. Principal 123, Quito
📞 *Teléfono:* 02-123-4567

Por favor, llegue 10 minutos antes de su hora.
```

---

## 🔧 API Endpoints

### Configuración de Recordatorios

#### GET `/api/notifications/reminder-settings`
Obtener configuración actual del usuario

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email_enabled": true,
    "email_hours_before": [24, 3],
    "whatsapp_enabled": true,
    "whatsapp_hours_before": [24],
    "auto_send_enabled": true,
    "send_on_days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    "quiet_hours_start": "22:00:00",
    "quiet_hours_end": "08:00:00"
  }
}
```

#### PUT `/api/notifications/reminder-settings`
Actualizar configuración de recordatorios

**Body:**
```json
{
  "email_enabled": true,
  "email_hours_before": [72, 24, 3],
  "whatsapp_enabled": true,
  "whatsapp_hours_before": [24],
  "auto_send_enabled": true,
  "send_on_days": ["mon", "tue", "wed", "thu", "fri"],
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00"
}
```

### Logs de Recordatorios

#### GET `/api/notifications/reminder-logs?appointment_id=123&limit=100`
Ver historial de recordatorios enviados

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "log_id": 1,
        "appointment_id": 123,
        "patient_name": "Juan Pérez",
        "reminder_type": "email",
        "hours_before": 24,
        "status": "sent",
        "sent_at": "2025-01-14T10:30:00",
        "recipient_email": "juan@email.com"
      }
    ],
    "count": 1
  }
}
```

### Envío Manual

#### POST `/api/notifications/reminders/send-now`
Enviar recordatorio manualmente (para pruebas)

**Body (cita específica):**
```json
{
  "appointment_id": 123,
  "hours_before": 24
}
```

**Body (procesar todos):**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email_sent": true,
    "whatsapp_sent": true
  },
  "message": "Reminders sent"
}
```

---

## ⏰ Sistema de Recordatorios Automáticos

### Cómo Funciona

1. **Configuración por Usuario:**
   - Cada doctor/admin configura sus preferencias en `/settings`
   - Se guardan en `reminder_settings` tabla

2. **Ventanas de Tiempo:**
   - Si configurado para enviar 24h antes, busca citas entre 23.5h y 24.5h
   - Ventana de ±30 minutos para evitar duplicados

3. **Procesamiento:**
   - `ReminderManager.process_scheduled_reminders()` se ejecuta periódicamente
   - Busca todas las horas configuradas (ej: 1h, 3h, 24h, 72h)
   - Para cada cita encontrada:
     - Verifica que no se haya enviado ya (chequea `reminder_logs`)
     - Obtiene configuración del doctor
     - Envía email si habilitado
     - Envía WhatsApp si habilitado
     - Registra resultado en `reminder_logs`

4. **Prevención de Duplicados:**
   - Antes de enviar, verifica tabla `reminder_logs`
   - Solo envía si no existe registro con mismo `appointment_id`, `hours_before` y `status='sent'`

### Cron Job (Linux/Mac)

Ejecutar cada 30 minutos:

```bash
crontab -e
```

Agregar:
```cron
*/30 * * * * cd /path/to/backend && python -c "from common.reminder_manager import ReminderManager; ReminderManager().process_scheduled_reminders()"
```

### Programador de Tareas (Windows)

1. Abrir **Task Scheduler**
2. Crear nueva tarea básica
3. Trigger: **Cada 30 minutos**
4. Acción: **Iniciar programa**
   - Programa: `C:\Python311\python.exe`
   - Argumentos: `-c "from common.reminder_manager import ReminderManager; ReminderManager().process_scheduled_reminders()"`
   - Directorio: `C:\path\to\backend`

### Script Standalone

Crear `backend/run_reminders_cron.py`:

```python
"""
Cron job para procesar recordatorios automáticos
Ejecutar cada 30 minutos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.reminder_manager import ReminderManager

if __name__ == '__main__':
    manager = ReminderManager()
    stats = manager.process_scheduled_reminders()
    print(f"Recordatorios procesados: {stats}")
```

Ejecutar:
```bash
python backend/run_reminders_cron.py
```

---

## 🧪 Pruebas

### 1. Verificar Servicios

```bash
# Backend services
curl http://localhost:5001/api/auth/health
curl http://localhost:5007/api/notifications/health

# Frontend
curl http://localhost:9002
```

### 2. Configurar Recordatorios

1. Login al sistema (http://localhost:9002)
2. Ir a **Configuración** (Settings)
3. Activar Email y/o WhatsApp
4. Seleccionar horarios (ej: 24h y 3h antes)
5. Guardar

### 3. Crear Cita de Prueba

```bash
# Crear cita para dentro de 24 horas
POST /api/citas/appointments
{
  "patient_id": 1,
  "doctor_id": 2,
  "start_time": "2025-01-15T10:00:00",  # 24 horas desde ahora
  "end_time": "2025-01-15T10:30:00",
  "reason": "Consulta de prueba"
}
```

### 4. Enviar Recordatorio Manual

```bash
POST http://localhost:5007/api/notifications/reminders/send-now
Authorization: Bearer <doctor_token>
Content-Type: application/json

{
  "appointment_id": 1,
  "hours_before": 24
}
```

### 5. Verificar Logs

```bash
GET http://localhost:5007/api/notifications/reminder-logs?appointment_id=1
```

---

## 🐛 Troubleshooting

### Error: "SMTPAuthenticationError"

**Causa:** Credenciales SMTP incorrectas

**Solución:**
1. Verificar `SMTP_USER` y `SMTP_PASSWORD` en `.env`
2. Si usas Gmail, crear App Password
3. Verificar que 2FA esté habilitado

### Error: "TwilioRestException: Unable to create record"

**Causa:** Número no registrado en sandbox o credenciales incorrectas

**Solución:**
1. Verificar `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN`
2. Registrar número destino en sandbox WhatsApp
3. Verificar formato: +593XXXXXXXXX

### Error: "Table reminder_settings does not exist"

**Causa:** Migración no ejecutada

**Solución:**
```bash
python backend/scripts/run_reminder_migration.py
```

### Recordatorios No Se Envían Automáticamente

**Causa:** Cron job no configurado

**Solución:**
1. Configurar cron/Task Scheduler
2. O ejecutar manualmente:
```bash
python -c "from common.reminder_manager import ReminderManager; ReminderManager().process_scheduled_reminders()"
```

### Email Llega a Spam

**Causa:** Falta configuración SPF/DKIM

**Solución:**
1. Usar servicio SMTP profesional (SendGrid, Mailgun)
2. Configurar SPF y DKIM en DNS
3. Calentar IP gradualmente

---

## 📊 Estructura de Base de Datos

### Tabla: `reminder_settings`

```sql
CREATE TABLE reminder_settings (
    setting_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) UNIQUE,

    -- Email
    email_enabled BOOLEAN DEFAULT TRUE,
    email_hours_before JSONB DEFAULT '[24, 3]'::jsonb,

    -- WhatsApp
    whatsapp_enabled BOOLEAN DEFAULT FALSE,
    whatsapp_hours_before JSONB DEFAULT '[24]'::jsonb,

    -- General
    auto_send_enabled BOOLEAN DEFAULT TRUE,
    send_on_days JSONB DEFAULT '["mon","tue","wed","thu","fri","sat","sun"]'::jsonb,
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '08:00:00',

    -- Optional overrides
    smtp_host VARCHAR(255),
    smtp_port INTEGER,
    smtp_user VARCHAR(255),
    smtp_password VARCHAR(255),
    from_email VARCHAR(255),
    from_name VARCHAR(255),
    twilio_account_sid VARCHAR(255),
    twilio_auth_token VARCHAR(255),
    twilio_whatsapp_number VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Tabla: `reminder_logs`

```sql
CREATE TABLE reminder_logs (
    log_id SERIAL PRIMARY KEY,
    appointment_id INTEGER,
    patient_id INTEGER,
    reminder_type VARCHAR(20) NOT NULL,  -- 'email' or 'whatsapp'
    hours_before INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'pending', 'sent', 'failed'
    sent_at TIMESTAMP,
    error_message TEXT,
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 📝 Notas Importantes

- **Sin Gmail/Twilio:** El sistema funciona sin configurar servicios externos, solo no enviará recordatorios
- **Sandbox WhatsApp:** Solo para pruebas, cada destinatario debe registrarse
- **Múltiples Recordatorios:** Puedes configurar varios horarios (ej: 72h, 24h, 3h antes)
- **Horario Silencioso:** Por defecto 22:00-08:00, configurable
- **Logs de Auditoría:** Todos los envíos se registran en `reminder_logs`
- **Permisos:** Solo doctores y admins pueden configurar recordatorios

---

## 🚀 Próximos Pasos

1. **Ejecutar migración:**
   ```bash
   python backend/scripts/run_reminder_migration.py
   ```

2. **Configurar `.env`** con credenciales SMTP y Twilio

3. **Iniciar servicio:**
   ```bash
   python backend/notifications_service/app.py
   ```

4. **Configurar desde UI:** http://localhost:9002/settings

5. **Configurar cron job** para envío automático

6. **Probar envío manual** desde API

---

**¿Preguntas?** Consultar la documentación completa en:
- Email Service: `backend/common/email_service.py`
- WhatsApp Service: `backend/common/whatsapp_service.py`
- Reminder Manager: `backend/common/reminder_manager.py`
- API Routes: `backend/notifications_service/routes.py`
