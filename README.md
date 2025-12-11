# Sistema de Gestión Clínica 🏥

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon.tech-blue.svg)](https://neon.tech/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema integral de gestión para clínicas médicas desarrollado con arquitectura de microservicios. Diseñado para Ecuador, cumple con normativas locales y soporta facturación electrónica.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Microservicios](#-microservicios)
- [Base de Datos](#-base-de-datos)
- [API Documentation](#-api-documentation)
- [Testing](#-testing)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

### Funcionalidades Principales

- **Gestión de Pacientes**: Registro completo con identificación ecuatoriana (RUC/Cédula)
- **Historia Clínica**: Antecedentes médicos, alergias, patologías y evoluciones
- **Agenda de Citas**: Sistema de agendamiento con asignación de doctores
- **Inventario Inteligente**: Control automático de productos y recetas de tratamientos
- **Facturación Electrónica SRI**: Sistema completo de facturación electrónica según normativas del SRI Ecuador
  - ✅ Generación de XML v2.1.0 compatible con SRI
  - ✅ Clave de acceso automática (49 dígitos con módulo 11)
  - ✅ Integración con Web Services SOAP del SRI
  - ✅ Soporte para ambiente de pruebas y producción
  - ✅ Cálculo automático de IVA 0% y 15%
  - ✅ Registro de auditoría completo
- **Reportes Financieros**: Análisis de ingresos, egresos y rentabilidad
- **Sistema de Logs**: Auditoría completa de todas las operaciones del sistema
- **Autenticación JWT**: Seguridad basada en tokens con control de roles (RBAC)

### Características Técnicas

- **Arquitectura de Microservicios**: 6 servicios independientes y escalables
- **API RESTful**: Endpoints bien documentados con Swagger/OpenAPI
- **Base de Datos Centralizada**: PostgreSQL en Neon.tech (serverless)
- **CORS Configurado**: Listo para integración con frontend
- **Pool de Conexiones**: Gestión eficiente de conexiones a BD
- **Sistema de Logs**: Registro centralizado de eventos y errores

## 🏗️ Arquitectura

```
Sistema Médico/
├── backend/
│   ├── auth_service/              # Autenticación y usuarios
│   ├── inventario_service/        # Productos y tratamientos
│   ├── historia_clinica_service/  # Pacientes e historias
│   ├── facturacion_service/       # Facturas y reportes
│   ├── citas_service/             # Citas y agenda
│   ├── logs_service/              # Auditoría y logs
│   ├── common/                    # Utilidades compartidas
│   │   ├── database.py            # Pool de conexiones
│   │   ├── auth_middleware.py     # Autenticación JWT
│   │   ├── logger.py              # Logger centralizado
│   │   └── utils.py               # Funciones comunes
│   └── scripts/                   # Scripts de utilidad
│       ├── init_database.sql      # Inicialización de BD
│       ├── setup_database.py      # Script de setup
│       └── add_logs_table.sql     # Tabla de logs
├── docs/                          # Documentación
└── README.md
```

### Flujo de Datos

```
Cliente → Auth Service (Login) → JWT Token
Cliente + Token → Cualquier Servicio → Logs Service
Servicios → PostgreSQL (Neon.tech)
```

## 📦 Requisitos

- **Python**: 3.12 o superior
- **PostgreSQL**: Base de datos en Neon.tech
- **pip**: Gestor de paquetes de Python
- **Git**: Para control de versiones

### Dependencias Principales

```
Flask==3.0.0
Flask-CORS==4.0.0
flask-restx==1.3.0
psycopg2-binary==2.9.9
PyJWT==2.8.0
bcrypt==4.1.2
python-dotenv==1.0.0
```

## 🚀 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-medico.git
cd sistema-medico
```

### 2. Configurar Variables de Entorno

```bash
cd backend
cp .env.example .env
```

Edita `.env` con tus credenciales de Neon.tech:

```env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
JWT_SECRET_KEY=tu-clave-secreta-muy-segura
```

### 3. Instalar Dependencias

```bash
# Instalar dependencias de todos los servicios
pip install -r auth_service/requirements.txt
```

### 4. Inicializar Base de Datos

```bash
cd scripts
python setup_database.py
```

Este script creará todas las tablas y datos iniciales.

## 💻 Uso

### Iniciar Todos los Servicios

**Windows:**
```bash
cd backend
run_all.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x run_all.sh
./run_all.sh
```

### Servicios Disponibles

| Servicio | Puerto | URL | Swagger |
|----------|--------|-----|---------|
| Auth Service | 5001 | http://localhost:5001 | [/docs](http://localhost:5001/docs) |
| Inventario | 5002 | http://localhost:5002 | [/docs](http://localhost:5002/docs) |
| Historia Clínica | 5003 | http://localhost:5003 | [/docs](http://localhost:5003/docs) |
| Facturación | 5004 | http://localhost:5004 | [/docs](http://localhost:5004/docs) |
| Citas | 5005 | http://localhost:5005 | [/docs](http://localhost:5005/docs) |
| Logs | 5006 | http://localhost:5006 | [/api/logs](http://localhost:5006/api/logs) |

### Credenciales por Defecto

```
Email:    admin@clinica.com
Password: admin123
```

**⚠️ Importante:** Cambia estas credenciales en producción.

## 🔧 Microservicios

### 1. Auth Service (Puerto 5001)

Gestión de autenticación, usuarios y roles.

**Endpoints principales:**
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/register` - Registrar usuario
- `GET /api/auth/me` - Info del usuario actual
- `GET /api/auth/users` - Listar usuarios
- `GET /api/auth/roles` - Listar roles

### 2. Inventario Service (Puerto 5002)

Gestión de productos médicos y tratamientos.

**Endpoints principales:**
- `GET /api/inventario/products` - Listar productos
- `POST /api/inventario/products` - Crear producto
- `GET /api/inventario/treatments` - Listar tratamientos
- `POST /api/inventario/treatments/{id}/recipe` - Asignar receta

**Motor de Recetas:**
Los tratamientos pueden tener recetas asociadas que descuentan automáticamente productos del inventario.

### 3. Historia Clínica Service (Puerto 5003)

Gestión de pacientes e historias clínicas.

**Endpoints principales:**
- `GET /api/historia-clinica/patients` - Listar pacientes
- `POST /api/historia-clinica/patients` - Crear paciente
- `GET /api/historia-clinica/patients/{id}/history` - Historial médico
- `PUT /api/historia-clinica/patients/{id}/history` - Actualizar historia

**Validaciones Ecuador:**
- Cédula: 10 dígitos
- RUC: 13 dígitos
- Pasaporte: Alfanumérico

### 4. Facturación Service (Puerto 5004)

Facturación y reportes financieros.

**Endpoints principales:**
- `GET /api/facturacion/invoices` - Listar facturas
- `POST /api/facturacion/invoices` - Crear factura
- `GET /api/facturacion/reports/summary` - Reporte de utilidad
- `POST /api/facturacion/expenses` - Registrar gasto

**Cálculos automáticos:**
- IVA configurable (15% por defecto)
- Costo de ventas basado en inventario
- Utilidad = Ingresos - (Egresos + Costo de Ventas)

### 5. Citas Service (Puerto 5005)

Agendamiento y gestión de citas médicas.

**Endpoints principales:**
- `GET /api/citas/appointments` - Listar citas
- `POST /api/citas/appointments` - Crear cita
- `POST /api/citas/appointments/{id}/treatments` - Agregar tratamiento
- `POST /api/citas/appointments/{id}/notes` - Agregar nota clínica

**Estados de cita:**
- PENDING: Pendiente
- CONFIRMED: Confirmada
- COMPLETED: Completada
- CANCELLED: Cancelada

### 6. Logs Service (Puerto 5006) ⭐ NUEVO

Sistema centralizado de auditoría y registro de eventos.

**Endpoints principales:**
- `POST /api/logs/logs` - Crear log
- `GET /api/logs/logs` - Listar logs con filtros
- `GET /api/logs/logs/{id}` - Obtener log específico
- `GET /api/logs/logs/stats` - Estadísticas de logs
- `POST /api/logs/logs/cleanup` - Limpiar logs antiguos

**Niveles de log:**
- DEBUG: Información de depuración
- INFO: Eventos informativos
- WARNING: Advertencias
- ERROR: Errores recuperables
- CRITICAL: Errores críticos

**Uso desde otros servicios:**
```python
from common.logger import auth_logger

# Registrar un evento
auth_logger.info(
    action="Usuario inició sesión",
    user_id=user_id,
    details="Login exitoso",
    ip_address=request.remote_addr
)
```

## 🗄️ Base de Datos

### Arquitectura

- **Motor**: PostgreSQL 15
- **Hosting**: Neon.tech (serverless)
- **Tablas**: 14 tablas normalizadas
- **Índices**: Optimizados para consultas frecuentes

### Tablas Principales

1. **roles**: Roles del sistema (Admin, Doctor, Recepción)
2. **users**: Usuarios del sistema
3. **patients**: Pacientes con identificación ecuatoriana
4. **medical_history**: Historias clínicas
5. **products**: Inventario de productos
6. **treatments**: Tratamientos/servicios médicos
7. **treatment_recipes**: Recetas de tratamientos
8. **appointments**: Citas médicas
9. **clinical_notes**: Notas de evolución
10. **appointment_treatments**: Tratamientos realizados
11. **appointment_extras**: Consumos adicionales
12. **invoices**: Facturas
13. **operational_expenses**: Gastos operativos
14. **system_logs**: Logs de auditoría ⭐ NUEVO

### Diagrama ER

Ver [docs/arquitecturaBD.md](docs/arquitecturaBD.md) para más detalles.

## 📚 API Documentation

### Swagger UI

Cada microservicio incluye documentación interactiva Swagger:

- Auth: http://localhost:5001/docs
- Inventario: http://localhost:5002/docs
- Historia Clínica: http://localhost:5003/docs
- Facturación: http://localhost:5004/docs
- Citas: http://localhost:5005/docs

### Autenticación

La mayoría de endpoints requieren un JWT token:

1. Obtener token:
```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@clinica.com", "password": "admin123"}'
```

2. Usar token:
```bash
curl -X GET http://localhost:5002/api/inventario/products \
  -H "Authorization: Bearer {tu-token}"
```

### Ejemplo de Respuesta

```json
{
  "success": true,
  "message": "Operation successful",
  "data": {
    "products": [...]
  }
}
```

## 🧪 Testing

```bash
cd backend
python -m pytest tests/ -v
```

### Cobertura

```bash
pytest --cov=. --cov-report=html
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Guía de Estilo

- **Python**: Seguir PEP 8
- **Commits**: Mensajes descriptivos en español
- **Documentación**: Actualizar README y docs

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📞 Soporte

Para preguntas o issues, crear un issue en GitHub o contactar:

- Email: soporte@tu-empresa.com
- GitHub Issues: [https://github.com/tu-usuario/sistema-medico/issues](https://github.com/tu-usuario/sistema-medico/issues)

## 🙏 Agradecimientos

- [Flask](https://flask.palletsprojects.com/) - Framework web
- [Neon.tech](https://neon.tech/) - Base de datos serverless
- [PostgreSQL](https://www.postgresql.org/) - Sistema de base de datos
- Comunidad de desarrolladores open source

---

**Desarrollado con ❤️ para mejorar la gestión de clínicas médicas en Ecuador**
