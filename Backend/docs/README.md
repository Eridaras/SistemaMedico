# Sistema de Gestión Clínica - Backend Microservicios

Sistema de gestión médica con arquitectura de microservicios desarrollado en Flask y PostgreSQL.

## 📋 Descripción

Este sistema está diseñado para gestionar clínicas médicas con las siguientes características:

- **Arquitectura de Microservicios**: Cada servicio es independiente y puede ser reutilizado
- **Motor de Recetas**: Vinculación automática entre tratamientos y productos del inventario
- **Normativa Ecuador**: Compatible con cédula, RUC y facturación electrónica
- **RBAC**: Control de acceso basado en roles con menús dinámicos
- **Cálculo Financiero**: Análisis de utilidad (Ingresos vs Egresos)

## 🏗️ Arquitectura

### Microservicios

1. **Autenticación (Puerto 5001)**
   - Login/Registro de usuarios
   - Gestión de roles y permisos
   - Validación JWT

2. **Inventario (Puerto 5002)**
   - Gestión de productos
   - Gestión de tratamientos
   - Motor de recetas (vinculación tratamiento-producto)
   - Alertas de stock bajo

3. **Historia Clínica (Puerto 5003)**
   - Gestión de pacientes
   - Antecedentes médicos
   - Notas clínicas

4. **Facturación (Puerto 5004)**
   - Generación de facturas
   - Gastos operativos
   - Reportes financieros
   - Dashboard de métricas

5. **Citas/Agendamiento (Puerto 5005)**
   - Gestión de citas
   - Verificación de disponibilidad
   - Agenda del doctor
   - Tratamientos y consumos por cita

## 🗄️ Base de Datos

- **Motor**: PostgreSQL (Neon.tech)
- **Esquema**: Ver `arquitecturaBD.md`
- **Conexión**: Configurada en `.env`

### Tablas Principales

- `roles`, `users` - Seguridad y usuarios
- `products`, `treatments`, `treatment_recipes` - Inventario y motor de recetas
- `patients`, `medical_history` - Pacientes
- `appointments`, `clinical_notes` - Citas
- `appointment_treatments`, `appointment_extras` - Tratamientos realizados
- `invoices`, `operational_expenses` - Facturación

## 🚀 Instalación

### Prerrequisitos

- Python 3.9 o superior
- PostgreSQL (o acceso a Neon.tech)
- pip

### Pasos de Instalación

1. **Clonar el repositorio** (si aplica)

2. **Configurar variables de entorno**

```bash
cp .env.example .env
```

Editar `.env` con tus credenciales de base de datos.

3. **Instalar dependencias**

```bash
# Windows
install.bat

# Linux/Mac
chmod +x install.sh
./install.sh
```

O manualmente para cada servicio:

```bash
cd auth_service
pip install -r requirements.txt

cd ../inventario_service
pip install -r requirements.txt

# ... y así para cada servicio
```

4. **Verificar la base de datos**

Asegúrate de que todas las tablas estén creadas según `arquitecturaBD.md`.

## ▶️ Ejecución

### Ejecutar todos los servicios

```bash
# Windows
run_all.bat

# Linux/Mac
chmod +x run_all.sh
./run_all.sh
```

### Ejecutar servicios individuales

```bash
# Servicio de Autenticación
cd auth_service
python app.py

# Servicio de Inventario
cd inventario_service
python app.py

# Servicio de Historia Clínica
cd historia_clinica_service
python app.py

# Servicio de Facturación
cd facturacion_service
python app.py

# Servicio de Citas
cd citas_service
python app.py
```

## 📡 Endpoints

### Autenticación (5001)

- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `GET /api/auth/me` - Obtener usuario actual
- `GET /api/auth/users` - Listar usuarios
- `GET /api/auth/roles` - Listar roles
- `POST /api/auth/roles` - Crear rol
- `GET /api/auth/health` - Health check

### Inventario (5002)

**Productos:**
- `GET /api/inventario/products` - Listar productos
- `GET /api/inventario/products/:id` - Obtener producto
- `POST /api/inventario/products` - Crear producto
- `PUT /api/inventario/products/:id` - Actualizar producto
- `PATCH /api/inventario/products/:id/stock` - Actualizar stock
- `GET /api/inventario/products/low-stock` - Productos con stock bajo

**Tratamientos:**
- `GET /api/inventario/treatments` - Listar tratamientos
- `GET /api/inventario/treatments/:id` - Obtener tratamiento
- `POST /api/inventario/treatments` - Crear tratamiento
- `PUT /api/inventario/treatments/:id` - Actualizar tratamiento
- `GET /api/inventario/treatments/categories` - Categorías

**Recetas:**
- `GET /api/inventario/treatments/:id/recipe` - Obtener receta
- `POST /api/inventario/treatments/:id/recipe` - Agregar ingrediente
- `DELETE /api/inventario/treatments/:id/recipe/:product_id` - Eliminar ingrediente
- `GET /api/inventario/treatments/:id/check-stock` - Verificar disponibilidad

### Historia Clínica (5003)

**Pacientes:**
- `GET /api/historia-clinica/patients` - Listar pacientes
- `GET /api/historia-clinica/patients/:id` - Obtener paciente
- `POST /api/historia-clinica/patients` - Crear paciente
- `PUT /api/historia-clinica/patients/:id` - Actualizar paciente
- `GET /api/historia-clinica/patients/search` - Buscar por cédula

**Historia Médica:**
- `GET /api/historia-clinica/patients/:id/medical-history` - Obtener historia
- `POST /api/historia-clinica/patients/:id/medical-history` - Crear/actualizar historia

**Notas Clínicas:**
- `GET /api/historia-clinica/patients/:id/notes` - Notas del paciente
- `GET /api/historia-clinica/appointments/:id/notes` - Notas de la cita
- `POST /api/historia-clinica/appointments/:id/notes` - Crear nota
- `PUT /api/historia-clinica/notes/:id` - Actualizar nota

### Facturación (5004)

**Facturas:**
- `GET /api/facturacion/invoices` - Listar facturas
- `GET /api/facturacion/invoices/:id` - Obtener factura
- `POST /api/facturacion/invoices` - Crear factura
- `PUT /api/facturacion/invoices/:id` - Actualizar factura
- `PATCH /api/facturacion/invoices/:id/status` - Cambiar estado
- `GET /api/facturacion/invoices/totals` - Totales por período

**Gastos:**
- `GET /api/facturacion/expenses` - Listar gastos
- `GET /api/facturacion/expenses/:id` - Obtener gasto
- `POST /api/facturacion/expenses` - Crear gasto
- `PUT /api/facturacion/expenses/:id` - Actualizar gasto
- `DELETE /api/facturacion/expenses/:id` - Eliminar gasto
- `GET /api/facturacion/expenses/totals` - Totales por período

**Reportes:**
- `GET /api/facturacion/reports/dashboard` - Métricas del dashboard

### Citas (5005)

**Citas:**
- `GET /api/citas/appointments` - Listar citas
- `GET /api/citas/appointments/:id` - Obtener cita
- `POST /api/citas/appointments` - Crear cita
- `PUT /api/citas/appointments/:id` - Actualizar cita
- `PATCH /api/citas/appointments/:id/status` - Cambiar estado
- `POST /api/citas/appointments/check-availability` - Verificar disponibilidad
- `GET /api/citas/doctors/:id/schedule` - Agenda del doctor

**Tratamientos de la Cita:**
- `GET /api/citas/appointments/:id/treatments` - Listar tratamientos
- `POST /api/citas/appointments/:id/treatments` - Agregar tratamiento
- `PUT /api/citas/appointments/treatments/:id` - Actualizar tratamiento
- `DELETE /api/citas/appointments/treatments/:id` - Eliminar tratamiento

**Extras:**
- `GET /api/citas/appointments/:id/extras` - Listar extras
- `POST /api/citas/appointments/:id/extras` - Agregar extra
- `PUT /api/citas/appointments/extras/:id` - Actualizar extra
- `DELETE /api/citas/appointments/extras/:id` - Eliminar extra

## 🔐 Autenticación

Todos los endpoints (excepto `/login`, `/register` y `/health`) requieren autenticación mediante JWT.

### Obtener Token

```bash
POST /api/auth/login
{
  "email": "usuario@ejemplo.com",
  "password": "password123"
}
```

### Usar Token

Incluir en el header de cada petición:

```
Authorization: Bearer <token>
```

## 📦 Estructura del Proyecto

```
Backend/
├── common/                      # Utilidades compartidas
│   ├── database.py             # Configuración de BD
│   ├── auth_middleware.py      # Middleware JWT
│   └── utils.py                # Funciones comunes
│
├── auth_service/               # Microservicio de Autenticación
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── requirements.txt
│
├── inventario_service/         # Microservicio de Inventario
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── requirements.txt
│
├── historia_clinica_service/   # Microservicio de Historia Clínica
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── requirements.txt
│
├── facturacion_service/        # Microservicio de Facturación
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── requirements.txt
│
├── citas_service/              # Microservicio de Citas
│   ├── app.py
│   ├── models.py
│   ├── routes.py
│   └── requirements.txt
│
├── .env.example                # Ejemplo de variables de entorno
├── .gitignore
└── README.md
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```env
# Database
DATABASE_URL=postgresql://user:pass@host/db

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_EXPIRATION_HOURS=24

# Puertos
AUTH_SERVICE_PORT=5001
INVENTARIO_SERVICE_PORT=5002
HISTORIA_CLINICA_SERVICE_PORT=5003
FACTURACION_SERVICE_PORT=5004
CITAS_SERVICE_PORT=5005

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Testing

```bash
# Probar health checks
curl http://localhost:5001/api/auth/health
curl http://localhost:5002/api/inventario/health
curl http://localhost:5003/api/historia-clinica/health
curl http://localhost:5004/api/facturacion/health
curl http://localhost:5005/api/citas/health
```

## 📝 Notas Importantes

1. **Seguridad**: Cambiar `JWT_SECRET_KEY` en producción
2. **Base de Datos**: Verificar que todas las tablas estén creadas
3. **CORS**: Configurar orígenes permitidos según tu frontend
4. **Puertos**: Asegurar que los puertos estén disponibles

## 🐛 Troubleshooting

### Error de Conexión a Base de Datos

- Verificar `DATABASE_URL` en `.env`
- Comprobar conectividad a PostgreSQL
- Verificar que las tablas existen

### Error de Puerto en Uso

```bash
# Windows
netstat -ano | findstr :5001

# Linux/Mac
lsof -i :5001
```

### Error de Módulo No Encontrado

```bash
pip install -r requirements.txt
```

## 🤝 Contribución

Este es un proyecto base que puedes extender según tus necesidades.

## 📄 Licencia

Uso interno - Sistema de gestión clínica

---

**Desarrollado con Flask y PostgreSQL**
