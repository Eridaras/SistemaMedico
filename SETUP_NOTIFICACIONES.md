# Setup Rápido - Google Calendar y Notificaciones

## ⚡ Inicio Rápido (5 minutos)

### 1. Instalar Dependencias

```bash
cd backend
pip install -r requirements-calendar.txt
```

### 2. Ejecutar Migración de Base de Datos

```bash
cd backend
python scripts/run_calendar_migration.py
```

✅ Esto crea las tablas `notification_preferences` y `notification_logs`

### 3. Iniciar Notifications Service

```bash
cd backend
python notifications_service/app.py
```

✅ El servicio debe iniciar en puerto 5007

### 4. Verificar Frontend

```bash
cd Frontend
npm run dev
```

### 5. Probar el Sistema

1. Login al sistema
2. Observar el icono de campana 🔔 en el header
3. Ver el Dashboard con los nuevos widgets:
   - **Citas de Hoy** (solo para doctores)
   - **Stock Bajo**

---

## 🔧 Configuración Opcional - Google Calendar

### Requisitos Previos

- Cuenta de Google
- Proyecto en Google Cloud Console

### Pasos

#### 1. Crear Proyecto en Google Cloud

1. Ir a https://console.cloud.google.com/
2. Crear nuevo proyecto: "Sistema Médico"
3. Seleccionar el proyecto

#### 2. Habilitar Google Calendar API

1. Ir a "APIs & Services" > "Library"
2. Buscar "Google Calendar API"
3. Click en "Enable"

#### 3. Crear Credenciales OAuth 2.0

1. Ir a "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Tipo de aplicación: **Desktop app**
4. Nombre: "Sistema Médico Desktop"
5. Click "Create"
6. Descargar el archivo JSON

#### 4. Configurar en el Sistema

```bash
# Mover credenciales
mv ~/Downloads/client_secret_*.json backend/credentials.json

# Primera autenticación
cd backend
python -c "from common.google_calendar import GoogleCalendarService; service = GoogleCalendarService(1); service.authenticate()"
```

Esto abrirá un navegador para autorizar:
1. Seleccionar cuenta de Google
2. Click "Permitir"
3. El token se guarda en `backend/tokens/`

✅ **Listo!** Ahora las citas se sincronizarán automáticamente con Google Calendar

---

## 📊 Endpoints Disponibles

### Notificaciones

```bash
# Ver notificaciones
GET http://localhost:5007/api/notifications/notifications

# Marcar como leída
PATCH http://localhost:5007/api/notifications/notifications/{id}/read
```

### Citas del Día

```bash
# Ver citas de hoy
GET http://localhost:5007/api/notifications/appointments/today
```

### Stock Bajo

```bash
# Ver productos con stock bajo
GET http://localhost:5007/api/notifications/low-stock

# Enviar alertas
POST http://localhost:5007/api/notifications/low-stock/alerts/send
```

---

## ✅ Verificación

### Backend

```bash
# Verificar que todos los servicios están corriendo
curl http://localhost:5001/api/auth/health    # Auth Service
curl http://localhost:5002/api/inventario/health  # Inventario
curl http://localhost:5003/api/historia-clinica/health  # Historia Clínica
curl http://localhost:5004/api/facturacion/health  # Facturación
curl http://localhost:5005/api/citas/health  # Citas
curl http://localhost:5007/api/notifications/health  # Notificaciones ✨
```

Todos deben responder:
```json
{"success": true, "data": {"status": "healthy", "service": "..."}}
```

### Frontend

1. Abrir http://localhost:9002
2. Login como doctor (cmendoza@clinica.ec / doctor123)
3. Verificar Dashboard:
   - ✅ Widget "Citas de Hoy" visible
   - ✅ Widget "Stock Bajo" visible
   - ✅ Icono de campana en header
4. Click en campana:
   - ✅ Panel de notificaciones abre

---

## 🐛 Troubleshooting

### Error: "Notifications service unavailable"

```bash
# Verificar que el servicio está corriendo
curl http://localhost:5007/api/notifications/health

# Si no responde, iniciar manualmente
cd backend
python notifications_service/app.py
```

### Error: "google.auth not found"

```bash
pip install -r requirements-calendar.txt
```

### Error: "Table notification_logs does not exist"

```bash
python scripts/run_calendar_migration.py
```

### Google Calendar no sincroniza

1. Verificar `credentials.json` existe en `backend/`
2. Re-ejecutar autenticación:
```bash
rm -rf backend/tokens/*
python -c "from common.google_calendar import GoogleCalendarService; service = GoogleCalendarService(1); service.authenticate()"
```

---

## 📝 Notas

- **Sin Google Calendar**: El sistema funciona perfectamente sin configurar Google Calendar. Solo se pierden los recordatorios automáticos.
- **Permisos**: Solo doctores ven el widget "Citas de Hoy"
- **Actualización**: Las notificaciones se actualizan cada 60 segundos
- **Stock Bajo**: Se actualiza cada 10 minutos

---

**Documentación completa**: Ver `docs/GOOGLE_CALENDAR_Y_NOTIFICACIONES.md`
