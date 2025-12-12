# 🚀 Inicio Rápido - Sistema de Gestión Clínica

Guía paso a paso para tener el sistema funcionando en menos de 5 minutos.

## Prerrequisitos

- Python 3.12+ instalado
- Credenciales de Neon.tech (PostgreSQL)
- Git instalado

## Paso 1: Clonar e Instalar (2 minutos)

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-medico.git
cd sistema-medico/backend

# Instalar dependencias
pip install -r auth_service/requirements.txt
```

## Paso 2: Configurar Variables de Entorno (1 minuto)

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar con tus credenciales de Neon.tech
# DATABASE_URL=postgresql://user:password@host/database?sslmode=require
```

## Paso 3: Inicializar Base de Datos (1 minuto)

```bash
cd scripts
python setup_database.py
```

Esto creará:
- ✅ 14 tablas
- ✅ 3 roles (Admin, Doctor, Recepción)
- ✅ Usuario admin (admin@clinica.com / admin123)
- ✅ Productos y tratamientos de ejemplo

## Paso 4: Iniciar Servicios (1 minuto)

**Windows:**
```bash
cd ..
run_all.bat
```

**Linux/Mac:**
```bash
cd ..
./run_all.sh
```

## ✅ ¡Listo! Verificar que Funciona

### 1. Health Checks

Abre estos URLs en tu navegador:

- Auth: http://localhost:5001/api/auth/health
- Inventario: http://localhost:5002/api/inventario/health
- Historia Clínica: http://localhost:5003/api/historia-clinica/health
- Facturación: http://localhost:5004/api/facturacion/health
- Citas: http://localhost:5005/api/citas/health
- Logs: http://localhost:5006/api/logs/health

Deberías ver: `{"success": true, "data": {"status": "healthy", "service": "..."}}`

### 2. Probar Login

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinica.com", "password": "admin123"}'
```

Deberías recibir un token JWT.

### 3. Explorar Swagger UI

Abre en tu navegador:

- http://localhost:5001/docs (Auth Service)
- http://localhost:5002/docs (Inventario)
- http://localhost:5003/docs (Historia Clínica)
- http://localhost:5004/docs (Facturación)
- http://localhost:5005/docs (Citas)

## 📖 Uso Básico con Swagger

### Autenticar en Swagger

1. Ve a http://localhost:5001/docs
2. Busca `POST /api/auth/login`
3. Click "Try it out"
4. Ingresa:
   ```json
   {
     "email": "admin@clinica.com",
     "password": "admin123"
   }
   ```
5. Click "Execute"
6. Copia el token de la respuesta

### Autorizar Otros Servicios

1. En cualquier servicio, click en **"Authorize"** (candado verde arriba a la derecha)
2. Ingresa: `Bearer {tu-token-aqui}`
3. Click "Authorize"
4. Ahora puedes probar todos los endpoints

## 🎯 Casos de Uso Comunes

### Crear un Paciente

1. Ve a http://localhost:5003/docs (Historia Clínica)
2. Autoriza con tu token
3. Busca `POST /api/historia-clinica/patients`
4. Try it out:
   ```json
   {
     "doc_type": "CEDULA",
     "doc_number": "1234567890",
     "first_name": "Juan",
     "last_name": "Pérez",
     "email": "juan@email.com",
     "phone": "0999999999",
     "birth_date": "1990-01-01",
     "gender": "M"
   }
   ```

### Crear una Cita

1. Ve a http://localhost:5005/docs (Citas)
2. Autoriza con tu token
3. Busca `POST /api/citas/appointments`
4. Try it out:
   ```json
   {
     "patient_id": 1,
     "doctor_id": 2,
     "start_time": "2025-01-15T10:00:00",
     "end_time": "2025-01-15T11:00:00",
     "reason": "Consulta general"
   }
   ```

### Crear Factura

1. Ve a http://localhost:5004/docs (Facturación)
2. Autoriza con tu token
3. Busca `POST /api/facturacion/invoices`
4. Try it out:
   ```json
   {
     "patient_id": 1,
     "appointment_id": 1,
     "invoice_number": "001-001-000000001",
     "subtotal": 25.00,
     "iva_rate": 15
   }
   ```

## 🔍 Ver Logs del Sistema

```bash
curl -X GET "http://localhost:5006/api/logs/logs?page=1&per_page=10" \
  -H "Authorization: Bearer {tu-token}"
```

## 📊 Ver Reportes Financieros

```bash
curl -X GET "http://localhost:5004/api/facturacion/reports/summary?start_date=2025-01-01&end_date=2025-12-31" \
  -H "Authorization: Bearer {tu-token}"
```

## ❗ Solución de Problemas

### Error: "Database connection pool created successfully" no aparece

**Causa**: Las variables de entorno no están cargadas correctamente.

**Solución**:
```bash
# Verifica que .env exista
cd backend
cat .env

# Verifica DATABASE_URL
echo $DATABASE_URL  # Linux/Mac
echo %DATABASE_URL%  # Windows
```

### Error: "ModuleNotFoundError: No module named 'flask'"

**Causa**: Las dependencias no están instaladas.

**Solución**:
```bash
pip install -r auth_service/requirements.txt
```

### Los servicios no inician en el puerto esperado

**Causa**: Los puertos están ocupados.

**Solución**:
```bash
# Verificar qué proceso usa el puerto
netstat -ano | findstr :5001  # Windows
lsof -i :5001  # Linux/Mac

# Cambiar el puerto en .env
AUTH_SERVICE_PORT=5011
```

### Error 401 (Unauthorized) en Swagger

**Causa**: El token no está configurado o expiró.

**Solución**:
1. Obtén un nuevo token con `/api/auth/login`
2. Click en "Authorize" en Swagger
3. Ingresa: `Bearer {nuevo-token}`

## 📚 Próximos Pasos

1. **Leer la documentación completa**: [README.md](README.md)
2. **Ver arquitectura de BD**: [docs/arquitecturaBD.md](docs/arquitecturaBD.md)
3. **Explorar tests**: [docs/SWAGGER_TESTS_INTEGRATION.md](docs/SWAGGER_TESTS_INTEGRATION.md)
4. **Integrar con tu frontend**: Ver sección de CORS en README

## 🆘 ¿Necesitas Ayuda?

- Documentación completa: [README.md](README.md)
- Reportar bugs: GitHub Issues
- Preguntas: Crear un issue con la etiqueta "question"

---

**¡Feliz desarrollo! 🎉**
