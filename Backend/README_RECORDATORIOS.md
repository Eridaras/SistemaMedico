# Sistema de Recordatorios - Backend

## 🎯 Inicio Rápido

```bash
# 1. Instalar dependencias
pip install -r requirements-reminders.txt

# 2. Ejecutar migración
python scripts/run_reminder_migration.py

# 3. Configurar .env (ver .env.example)
# Agregar credenciales SMTP y Twilio

# 4. Iniciar servicio
python notifications_service/app.py

# 5. Configurar cron job
*/30 * * * * cd /path/to/backend && python run_reminders_cron.py
```

## 📁 Archivos Creados

### Servicios Core
- **`common/email_service.py`** - Servicio SMTP con plantillas HTML profesionales
- **`common/whatsapp_service.py`** - Integración Twilio para WhatsApp
- **`common/reminder_manager.py`** - Orquestador principal del sistema

### API Endpoints
- **`notifications_service/routes.py`** - 4 nuevos endpoints:
  - `GET /reminder-settings` - Obtener configuración
  - `PUT /reminder-settings` - Actualizar configuración
  - `GET /reminder-logs` - Ver historial de envíos
  - `POST /reminders/send-now` - Envío manual

### Base de Datos
- **`scripts/add_reminder_settings.sql`** - Tablas reminder_settings y reminder_logs
- **`scripts/run_reminder_migration.py`** - Script de migración

### Automatización
- **`run_reminders_cron.py`** - Script para cron job (ejecutar cada 30 min)

### Configuración
- **`requirements-reminders.txt`** - Dependencia twilio
- **`.env.example`** - Variables SMTP y Twilio agregadas

## 🔧 Configuración SMTP (Email)

### Gmail
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=app-password-16-chars  # App Password, no contraseña regular
FROM_EMAIL=tu-email@gmail.com
FROM_NAME=Clínica Bienestar
```

Crear App Password: https://myaccount.google.com/apppasswords

### Otros Proveedores
- **SendGrid:** `smtp.sendgrid.net:587`
- **Mailgun:** `smtp.mailgun.org:587`
- **Outlook:** `smtp-mail.outlook.com:587`

## 📱 Configuración WhatsApp (Twilio)

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

### Setup Twilio
1. Crear cuenta: https://www.twilio.com/try-twilio
2. Configurar Sandbox: **Messaging → Try it out → WhatsApp**
3. Enviar `join <codigo>` a +1 415 523 8886 desde WhatsApp
4. Copiar credenciales de Dashboard

## 🧪 Probar Servicios

### Email Service
```python
from common.email_service import EmailService

service = EmailService()
data = {
    'patient_name': 'Juan Pérez',
    'doctor_name': 'Dra. María López',
    'appointment_date': '2025-01-15',
    'appointment_time': '10:30',
    'reason': 'Consulta',
    'clinic_address': 'Av. Principal 123',
    'clinic_phone': '02-123-4567'
}

service.send_appointment_reminder('paciente@email.com', data, hours_before=24)
```

### WhatsApp Service
```python
from common.whatsapp_service import WhatsAppService

service = WhatsAppService()
data = {  # Same as above
    'patient_name': 'Juan Pérez',
    # ...
}

service.send_appointment_reminder('+593987654321', data, hours_before=24)
```

### Reminder Manager (Completo)
```python
from common.reminder_manager import ReminderManager

manager = ReminderManager()
stats = manager.process_scheduled_reminders()
print(stats)
# {'total_processed': 5, 'email_sent': 3, 'whatsapp_sent': 2, 'failed': 0}
```

## 📊 Estructura de Datos

### reminder_settings
```python
{
    'user_id': 2,
    'email_enabled': True,
    'email_hours_before': [72, 24, 3],  # 3 días, 1 día, 3 horas
    'whatsapp_enabled': True,
    'whatsapp_hours_before': [24],  # 1 día
    'auto_send_enabled': True,
    'send_on_days': ['mon', 'tue', 'wed', 'thu', 'fri'],
    'quiet_hours_start': '22:00:00',
    'quiet_hours_end': '08:00:00'
}
```

### reminder_logs
```python
{
    'log_id': 1,
    'appointment_id': 123,
    'patient_id': 45,
    'reminder_type': 'email',  # or 'whatsapp'
    'hours_before': 24,
    'status': 'sent',  # or 'failed'
    'sent_at': '2025-01-14T10:30:00',
    'recipient_email': 'paciente@email.com',
    'recipient_phone': '+593987654321',
    'error_message': None
}
```

## 🔄 Flujo de Trabajo

1. **Configuración (One-time):**
   - Doctor va a `/settings` en frontend
   - Configura horarios de recordatorios
   - Se guarda en `reminder_settings`

2. **Creación de Cita:**
   - Se crea cita en `appointments` tabla
   - Sistema calcula cuándo enviar recordatorios

3. **Procesamiento Automático (Cada 30 min):**
   - Cron ejecuta `run_reminders_cron.py`
   - `ReminderManager.process_scheduled_reminders()`:
     - Busca citas en ventana de tiempo (±30 min)
     - Verifica que no se haya enviado (chequea `reminder_logs`)
     - Obtiene configuración del doctor
     - Envía email si habilitado
     - Envía WhatsApp si habilitado
     - Registra en `reminder_logs`

4. **Auditoría:**
   - Todos los envíos se registran
   - Ver historial en `/api/notifications/reminder-logs`

## 🐛 Debugging

### Ver logs en vivo
```bash
# Terminal 1: Iniciar servicio con logs
python notifications_service/app.py

# Terminal 2: Ejecutar cron manualmente
python run_reminders_cron.py
```

### Verificar tablas
```sql
-- Ver configuraciones
SELECT * FROM reminder_settings;

-- Ver logs recientes
SELECT * FROM reminder_logs ORDER BY created_at DESC LIMIT 10;

-- Ver citas próximas
SELECT
    a.appointment_id,
    a.start_time,
    p.first_name || ' ' || p.last_name as patient_name,
    p.email,
    p.phone
FROM appointments a
JOIN patients p ON a.patient_id = p.patient_id
WHERE a.start_time > NOW()
AND a.status IN ('PENDING', 'CONFIRMED')
ORDER BY a.start_time
LIMIT 10;
```

### Envío manual de prueba
```bash
curl -X POST http://localhost:5007/api/notifications/reminders/send-now \
  -H "Authorization: Bearer <doctor_token>" \
  -H "Content-Type: application/json" \
  -d '{"appointment_id": 1, "hours_before": 24}'
```

## 📈 Escalabilidad

- **Cron cada 30 min** → Procesa hasta ~1000 citas/min
- **Múltiples workers** → Usar Celery + Redis para producción
- **Rate limiting** → Twilio: 1 msg/seg, Gmail: 500 emails/día
- **Batch sending** → WhatsAppService.send_bulk_reminders()

## 🔐 Seguridad

- ✅ Credenciales en `.env` (no commitear)
- ✅ JWT auth en todos los endpoints
- ✅ Logs encriptados en producción
- ✅ SMTP con TLS/SSL
- ✅ Validación de números telefónicos

## 📚 Documentación Completa

Ver: **`/GUIA_RECORDATORIOS.md`** en raíz del proyecto

## ⚙️ Variables de Entorno Requeridas

```bash
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@gmail.com
SMTP_PASSWORD=app-password
FROM_EMAIL=clinica@ejemplo.com
FROM_NAME=Clínica Bienestar

# WhatsApp
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Service
NOTIFICATIONS_SERVICE_PORT=5007
```

---

**¿Preguntas?** Ver código fuente con comentarios detallados en:
- `common/email_service.py`
- `common/whatsapp_service.py`
- `common/reminder_manager.py`
