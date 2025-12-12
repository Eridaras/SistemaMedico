# 📁 Estructura del Proyecto - Sistema de Gestión Clínica

## Vista General

```
SistemaMedico/
├── backend/                          # Código del backend (microservicios)
│   ├── auth_service/                 # Servicio de Autenticación
│   │   ├── __init__.py
│   │   ├── app.py                    # Aplicación Flask principal
│   │   ├── models.py                 # Modelos de datos (User, Role)
│   │   ├── routes.py                 # Endpoints API
│   │   ├── swagger_config.py         # Configuración Swagger
│   │   └── requirements.txt          # Dependencias Python
│   │
│   ├── inventario_service/           # Servicio de Inventario
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── models.py                 # Modelos (Product, Treatment, Recipe)
│   │   ├── routes.py
│   │   └── requirements.txt
│   │
│   ├── historia_clinica_service/     # Servicio de Historia Clínica
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── models.py                 # Modelos (Patient, MedicalHistory)
│   │   ├── routes.py
│   │   └── requirements.txt
│   │
│   ├── facturacion_service/          # Servicio de Facturación
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── models.py                 # Modelos (Invoice, Expense, Reports)
│   │   ├── routes.py
│   │   └── requirements.txt
│   │
│   ├── citas_service/                # Servicio de Citas
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── models.py                 # Modelos (Appointment, Treatment, Extra)
│   │   ├── routes.py
│   │   └── requirements.txt
│   │
│   ├── logs_service/                 # Servicio de Logs (NUEVO)
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── models.py                 # Modelo (Log)
│   │   ├── routes.py
│   │   └── requirements.txt
│   │
│   ├── common/                       # Utilidades compartidas
│   │   ├── __init__.py
│   │   ├── database.py               # Pool de conexiones PostgreSQL
│   │   ├── auth_middleware.py        # Middleware JWT
│   │   ├── logger.py                 # Helper de logging (NUEVO)
│   │   └── utils.py                  # Funciones utilitarias
│   │
│   ├── scripts/                      # Scripts de utilidad
│   │   ├── init_database.sql         # Script SQL inicial
│   │   ├── add_logs_table.sql        # Script SQL para logs (NUEVO)
│   │   ├── setup_database.py         # Inicializar BD
│   │   └── fix_admin_password.py     # Resetear contraseña admin
│   │
│   ├── .env                          # Variables de entorno (NO en Git)
│   ├── .env.example                  # Ejemplo de variables de entorno
│   ├── run_all.bat                   # Ejecutar todos los servicios (Windows)
│   ├── run_all.sh                    # Ejecutar todos los servicios (Linux/Mac)
│   ├── run_tests.bat                 # Ejecutar tests (Windows)
│   ├── run_tests.sh                  # Ejecutar tests (Linux/Mac)
│   ├── install.bat                   # Script de instalación (Windows)
│   └── install.sh                    # Script de instalación (Linux/Mac)
│
├── docs/                             # Documentación
│   ├── arquitecturaBD.md             # Arquitectura de Base de Datos
│   ├── INICIO_RAPIDO.md              # Guía de inicio rápido
│   ├── README.md                     # Documentación anterior
│   ├── SERVICIOS_ACTIVOS.md          # Estado de servicios
│   ├── SWAGGER_TESTS_INTEGRATION.md  # Tests y Swagger
│   └── LOGS_SERVICE.md               # Documentación de Logs (NUEVO)
│
├── .git/                             # Control de versiones Git
├── .gitignore                        # Archivos ignorados por Git
├── README.md                         # Documentación principal (NUEVO)
├── INICIO_RAPIDO.md                  # Guía de inicio (NUEVO)
└── ESTRUCTURA_PROYECTO.md            # Este archivo (NUEVO)
```

## Descripción de Componentes

### 📂 backend/

Contiene todo el código del sistema backend organizado en microservicios.

#### 🔐 auth_service/ (Puerto 5001)
**Responsabilidad**: Autenticación, autorización y gestión de usuarios

**Tablas BD**:
- `users` - Usuarios del sistema
- `roles` - Roles y permisos

**Endpoints clave**:
- Login/Logout
- Registro de usuarios
- Gestión de roles
- Validación de tokens

#### 📦 inventario_service/ (Puerto 5002)
**Responsabilidad**: Control de inventario y tratamientos médicos

**Tablas BD**:
- `products` - Productos e insumos médicos
- `treatments` - Servicios/tratamientos
- `treatment_recipes` - Recetas de tratamientos

**Características**:
- Motor de recetas (descuento automático de inventario)
- Alertas de stock bajo
- Control de costos

#### 🏥 historia_clinica_service/ (Puerto 5003)
**Responsabilidad**: Gestión de pacientes e historias médicas

**Tablas BD**:
- `patients` - Datos demográficos de pacientes
- `medical_history` - Historias clínicas

**Validaciones**:
- Cédula ecuatoriana (10 dígitos)
- RUC (13 dígitos)
- Campos HIPAA compliant

#### 💰 facturacion_service/ (Puerto 5004)
**Responsabilidad**: Facturación y reportes financieros

**Tablas BD**:
- `invoices` - Facturas
- `operational_expenses` - Gastos operativos

**Características**:
- Cálculo automático de IVA
- Reportes de utilidad
- Compatible con SRI Ecuador

#### 📅 citas_service/ (Puerto 5005)
**Responsabilidad**: Agendamiento y gestión de citas

**Tablas BD**:
- `appointments` - Citas médicas
- `clinical_notes` - Notas de evolución
- `appointment_treatments` - Tratamientos aplicados
- `appointment_extras` - Consumos adicionales

**Estados**:
- PENDING, CONFIRMED, COMPLETED, CANCELLED

#### 📊 logs_service/ (Puerto 5006) ⭐ NUEVO
**Responsabilidad**: Auditoría y registro de eventos del sistema

**Tablas BD**:
- `system_logs` - Logs de todos los servicios

**Características**:
- Logging asíncrono (no bloquea)
- Filtrado avanzado
- Estadísticas y análisis
- Limpieza automática de logs antiguos
- 5 niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL

#### 🔧 common/
**Responsabilidad**: Código compartido entre servicios

**Componentes**:
- `database.py` - Pool de conexiones PostgreSQL
- `auth_middleware.py` - Decoradores @token_required, @role_required
- `logger.py` - Helpers para logging centralizado ⭐ NUEVO
- `utils.py` - Validaciones, formateo, respuestas estándar

#### 📜 scripts/
**Responsabilidad**: Scripts de administración y mantenimiento

**Scripts**:
- `init_database.sql` - Crear todas las tablas
- `add_logs_table.sql` - Agregar tabla de logs ⭐ NUEVO
- `setup_database.py` - Inicializar BD con datos de ejemplo
- `fix_admin_password.py` - Resetear contraseña del admin

### 📚 docs/

Documentación técnica y guías de usuario.

**Archivos**:
- `arquitecturaBD.md` - Diseño de base de datos
- `LOGS_SERVICE.md` - Documentación completa del servicio de logs ⭐ NUEVO
- `SWAGGER_TESTS_INTEGRATION.md` - Testing con Swagger
- `SERVICIOS_ACTIVOS.md` - Estado y URLs de servicios

## Flujos de Datos

### Flujo de Autenticación

```
1. Cliente → POST /api/auth/login
2. Auth Service → Validar credenciales en BD
3. Auth Service → Generar JWT token
4. Auth Service → Logs Service (registrar login)
5. Auth Service → Cliente (retornar token)
```

### Flujo de Operación con Logs

```
1. Cliente + Token → POST /api/citas/appointments
2. Citas Service → Middleware: Validar JWT
3. Citas Service → BD: Crear cita
4. Citas Service → Logs Service: Registrar evento (async)
5. Citas Service → Cliente: Retornar respuesta
```

### Flujo de Tratamiento con Receta

```
1. Doctor aplica tratamiento en cita
2. Citas Service → Inventario Service: Consultar receta
3. Inventario Service → Retornar productos necesarios
4. Inventario Service → Descontar stock automáticamente
5. Logs Service → Registrar movimiento de inventario
```

## Tecnologías Utilizadas

### Backend
- **Python 3.12+** - Lenguaje principal
- **Flask 3.0.0** - Framework web
- **Flask-RESTX** - Swagger/OpenAPI
- **PostgreSQL** - Base de datos
- **Neon.tech** - Hosting de BD (serverless)

### Seguridad
- **JWT (PyJWT)** - Autenticación sin estado
- **bcrypt** - Hash de contraseñas
- **CORS** - Control de acceso cross-origin

### Base de Datos
- **psycopg2** - Driver PostgreSQL
- **Connection Pooling** - Gestión eficiente de conexiones

### Desarrollo
- **python-dotenv** - Variables de entorno
- **pytest** - Testing
- **requests** - Cliente HTTP

## Variables de Entorno

### Configuración Principal (.env)

```env
# Base de Datos
DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# Seguridad
JWT_SECRET_KEY=tu-clave-secreta
JWT_EXPIRATION_HOURS=24

# Puertos de Servicios
AUTH_SERVICE_PORT=5001
INVENTARIO_SERVICE_PORT=5002
HISTORIA_CLINICA_SERVICE_PORT=5003
FACTURACION_SERVICE_PORT=5004
CITAS_SERVICE_PORT=5005
LOGS_SERVICE_PORT=5006

# URLs de Servicios (para comunicación inter-servicio)
AUTH_SERVICE_URL=http://localhost:5001/api/auth
INVENTARIO_SERVICE_URL=http://localhost:5002/api/inventario
HISTORIA_CLINICA_SERVICE_URL=http://localhost:5003/api/historia-clinica
FACTURACION_SERVICE_URL=http://localhost:5004/api/facturacion
CITAS_SERVICE_URL=http://localhost:5005/api/citas
LOGS_SERVICE_URL=http://localhost:5006/api/logs

# Flask
FLASK_ENV=development
FLASK_DEBUG=True

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## Base de Datos - Resumen

### 14 Tablas Principales

| Tabla | Servicio | Descripción |
|-------|----------|-------------|
| `roles` | Auth | Roles del sistema |
| `users` | Auth | Usuarios |
| `patients` | Historia Clínica | Pacientes |
| `medical_history` | Historia Clínica | Historias médicas |
| `products` | Inventario | Productos e insumos |
| `treatments` | Inventario | Servicios médicos |
| `treatment_recipes` | Inventario | Recetas de tratamientos |
| `appointments` | Citas | Citas médicas |
| `clinical_notes` | Citas | Notas de evolución |
| `appointment_treatments` | Citas | Tratamientos aplicados |
| `appointment_extras` | Citas | Consumos adicionales |
| `invoices` | Facturación | Facturas |
| `operational_expenses` | Facturación | Gastos |
| `system_logs` | Logs | Auditoría ⭐ NUEVO |

## Comandos Útiles

### Desarrollo

```bash
# Iniciar todos los servicios
cd backend
./run_all.sh  # Linux/Mac
run_all.bat   # Windows

# Inicializar BD
cd backend/scripts
python setup_database.py

# Agregar tabla de logs
python -c "import psycopg2; from dotenv import load_dotenv; import os; load_dotenv(); conn = psycopg2.connect(os.getenv('DATABASE_URL')); cursor = conn.cursor(); cursor.execute(open('add_logs_table.sql').read()); conn.commit()"

# Resetear contraseña admin
python fix_admin_password.py

# Ejecutar tests
cd backend
./run_tests.sh  # Linux/Mac
run_tests.bat   # Windows
```

### Git

```bash
# Clonar proyecto
git clone https://github.com/tu-usuario/sistema-medico.git

# Crear rama para feature
git checkout -b feature/nueva-funcionalidad

# Commit
git add .
git commit -m "feat: descripción del cambio"

# Push
git push origin feature/nueva-funcionalidad
```

## Próximos Desarrollos

### En Roadmap

1. **Frontend Web**
   - React/Vue.js
   - Dashboard administrativo
   - Portal de pacientes

2. **Notificaciones**
   - Email (recordatorios de citas)
   - SMS
   - Push notifications

3. **Reportes Avanzados**
   - Excel/PDF exports
   - Gráficos y analytics
   - Business Intelligence

4. **Integraciones**
   - Facturación electrónica SRI
   - Sistemas de pago
   - Laboratorios externos

5. **Móvil**
   - App para doctores
   - App para pacientes

## Soporte y Contribuciones

### Reportar Bugs

Crear un issue en GitHub con:
- Descripción del problema
- Pasos para reproducir
- Logs relevantes
- Ambiente (OS, Python version)

### Contribuir

1. Fork del proyecto
2. Crear rama feature
3. Implementar cambios
4. Agregar tests
5. Actualizar documentación
6. Pull request

## Licencia

MIT License - Ver archivo LICENSE

---

**Sistema de Gestión Clínica v1.0**
**Desarrollado con ❤️ para la comunidad médica de Ecuador**
