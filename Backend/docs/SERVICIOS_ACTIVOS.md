# Sistema Médico - Servicios Activos

## Estado del Sistema

Todos los microservicios están **ACTIVOS** y funcionando correctamente.

## Base de Datos

- **PostgreSQL (Neon.tech)**: Inicializada con todas las tablas
- **13 Tablas creadas**:
  - roles
  - users
  - products
  - treatments
  - treatment_recipes
  - patients
  - medical_history
  - appointments
  - clinical_notes
  - appointment_treatments
  - appointment_extras
  - operational_expenses
  - invoices

## Microservicios Disponibles

### 1. Auth Service (Puerto 5001)
- **URL Base**: http://localhost:5001
- **Swagger UI**: http://localhost:5001/docs
- **Endpoints principales**:
  - POST `/api/auth/login` - Iniciar sesión
  - POST `/api/auth/register` - Registrar usuario
  - GET `/api/auth/me` - Información del usuario actual
  - GET `/api/auth/users` - Listar usuarios
  - GET `/api/auth/roles` - Listar roles
  - POST `/api/auth/roles` - Crear rol
  - PUT `/api/auth/roles/{id}` - Actualizar rol
  - GET `/api/auth/validate` - Validar token
  - GET `/api/auth/health` - Health check

### 2. Inventario Service (Puerto 5002)
- **URL Base**: http://localhost:5002
- **Swagger UI**: http://localhost:5002/docs
- **Endpoints principales**:
  - GET `/api/inventario/products` - Listar productos
  - POST `/api/inventario/products` - Crear producto
  - GET `/api/inventario/products/{id}` - Obtener producto
  - PUT `/api/inventario/products/{id}` - Actualizar producto
  - DELETE `/api/inventario/products/{id}` - Eliminar producto
  - GET `/api/inventario/treatments` - Listar tratamientos
  - POST `/api/inventario/treatments` - Crear tratamiento
  - GET `/api/inventario/health` - Health check

### 3. Historia Clínica Service (Puerto 5003)
- **URL Base**: http://localhost:5003
- **Swagger UI**: http://localhost:5003/docs
- **Endpoints principales**:
  - GET `/api/historia-clinica/patients` - Listar pacientes
  - POST `/api/historia-clinica/patients` - Crear paciente
  - GET `/api/historia-clinica/patients/{id}` - Obtener paciente
  - PUT `/api/historia-clinica/patients/{id}` - Actualizar paciente
  - GET `/api/historia-clinica/patients/{id}/history` - Historial médico
  - POST `/api/historia-clinica/patients/{id}/history` - Crear historial
  - GET `/api/historia-clinica/health` - Health check

### 4. Facturación Service (Puerto 5004)
- **URL Base**: http://localhost:5004
- **Swagger UI**: http://localhost:5004/docs
- **Endpoints principales**:
  - GET `/api/facturacion/invoices` - Listar facturas
  - POST `/api/facturacion/invoices` - Crear factura
  - GET `/api/facturacion/invoices/{id}` - Obtener factura
  - PUT `/api/facturacion/invoices/{id}` - Actualizar factura
  - GET `/api/facturacion/expenses` - Listar gastos
  - POST `/api/facturacion/expenses` - Crear gasto
  - GET `/api/facturacion/reports/summary` - Reporte financiero
  - GET `/api/facturacion/health` - Health check

### 5. Citas Service (Puerto 5005)
- **URL Base**: http://localhost:5005
- **Swagger UI**: http://localhost:5005/docs
- **Endpoints principales**:
  - GET `/api/citas/appointments` - Listar citas
  - POST `/api/citas/appointments` - Crear cita
  - GET `/api/citas/appointments/{id}` - Obtener cita
  - PUT `/api/citas/appointments/{id}` - Actualizar cita
  - DELETE `/api/citas/appointments/{id}` - Cancelar cita
  - POST `/api/citas/appointments/{id}/treatments` - Agregar tratamiento
  - POST `/api/citas/appointments/{id}/notes` - Agregar nota clínica
  - GET `/api/citas/health` - Health check

## Credenciales de Acceso

### Usuario Administrador
- **Email**: admin@clinica.com
- **Password**: admin123

## Cómo Usar Swagger

### Paso 1: Obtener Token de Autenticación

1. Abre http://localhost:5001/docs en tu navegador
2. Busca el endpoint `POST /api/auth/login`
3. Click en "Try it out"
4. Ingresa las credenciales:
```json
{
  "email": "admin@clinica.com",
  "password": "admin123"
}
```
5. Click en "Execute"
6. Copia el token de la respuesta (campo `data.token`)

### Paso 2: Autorizar en Swagger

1. En cualquier servicio, click en el botón **"Authorize"** (candado verde) en la parte superior derecha
2. Ingresa el token en el formato: `Bearer {tu-token}`
   Ejemplo: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
3. Click en "Authorize"
4. Click en "Close"

### Paso 3: Probar Endpoints

Ahora puedes probar cualquier endpoint en cualquier servicio. El token se enviará automáticamente con cada petición.

## Ejemplos de Uso con cURL

### Login
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinica.com", "password": "admin123"}'
```

### Listar Productos (requiere token)
```bash
curl -X GET http://localhost:5002/api/inventario/products \
  -H "Authorization: Bearer {tu-token}"
```

### Listar Pacientes (requiere token)
```bash
curl -X GET http://localhost:5003/api/historia-clinica/patients \
  -H "Authorization: Bearer {tu-token}"
```

### Health Check (no requiere token)
```bash
curl http://localhost:5001/api/auth/health
curl http://localhost:5002/api/inventario/health
curl http://localhost:5003/api/historia-clinica/health
curl http://localhost:5004/api/facturacion/health
curl http://localhost:5005/api/citas/health
```

## Datos de Prueba

La base de datos incluye datos iniciales:

### Roles
- Admin (ID: 1)
- Doctor (ID: 2)
- Recepcion (ID: 3)

### Productos de Ejemplo
- Paracetamol 500mg
- Ibuprofeno 400mg
- Guantes de látex (caja)
- Jeringas 5ml (paquete)

### Tratamientos de Ejemplo
- Consulta General ($25.00)
- Limpieza Dental ($35.00)
- Extracción Simple ($50.00)

## Troubleshooting

### Los servicios no inician
```bash
# Verificar que el archivo .env exista
ls .env

# Verificar las dependencias
pip install -r auth_service/requirements.txt
```

### Error de conexión a base de datos
- Verifica que DATABASE_URL en .env sea correcta
- Verifica que tengas conexión a internet

### Error 401 (Unauthorized)
- Verifica que el token sea válido
- Verifica que estés usando el formato correcto: `Bearer {token}`

## Scripts Útiles

### Inicializar/Reinicializar Base de Datos
```bash
python setup_database.py
```

### Actualizar Contraseña del Admin
```bash
python fix_admin_password.py
```

### Ejecutar Todos los Servicios (Windows)
```bash
run_all.bat
```

### Ejecutar Tests
```bash
run_tests.bat
```

## Arquitectura

El sistema utiliza una arquitectura de microservicios donde:
- Cada servicio es independiente y tiene su propia lógica de negocio
- Todos los servicios comparten la misma base de datos PostgreSQL
- La autenticación se maneja con JWT tokens
- CORS está configurado para permitir requests desde localhost

## Próximos Pasos

1. Explorar cada servicio en Swagger
2. Crear pacientes de prueba
3. Crear citas
4. Registrar tratamientos
5. Generar facturas
6. Ver reportes financieros

¡Todo está listo para usar! 🚀
