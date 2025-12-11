# 📝 Changelog - Sistema de Gestión Clínica

Todos los cambios importantes del proyecto serán documentados en este archivo.

## [1.1.0] - 2025-12-10

### ⭐ Añadido

#### Nuevo Servicio: Logs Service (Puerto 5006)
- **Sistema completo de auditoría** para todos los microservicios
- **14ª tabla en BD**: `system_logs` con índices optimizados
- **5 niveles de logging**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **API REST completa**:
  - POST `/api/logs/logs` - Crear log (sin autenticación)
  - GET `/api/logs/logs` - Listar con filtros avanzados
  - GET `/api/logs/logs/{id}` - Obtener log específico
  - GET `/api/logs/logs/stats` - Estadísticas y métricas
  - POST `/api/logs/logs/cleanup` - Limpieza automática
  - GET `/api/logs/health` - Health check

#### Helper de Logging (`common/logger.py`)
- **Loggers pre-configurados** para cada servicio
- **Envío asíncrono**: No bloquea las operaciones principales
- **Manejo robusto de errores**: Nunca rompe la aplicación
- **Fácil integración**:
  ```python
  from common.logger import auth_logger
  auth_logger.info(action="Login exitoso", user_id=123)
  ```

#### Documentación Completa
- **README.md principal**: Documentación profesional con badges, guías y ejemplos
- **INICIO_RAPIDO.md**: Guía paso a paso para tener el sistema funcionando en 5 minutos
- **ESTRUCTURA_PROYECTO.md**: Documentación detallada de arquitectura y componentes
- **docs/LOGS_SERVICE.md**: Documentación técnica completa del servicio de logs
- **CHANGELOG.md**: Este archivo de cambios

### 🔄 Cambios

#### Reorganización del Proyecto
- **Todo el backend** movido a carpeta `backend/`
- **Scripts** organizados en `backend/scripts/`
- **Documentación** centralizada en carpeta `docs/`
- **Estructura más limpia** y profesional

#### Variables de Entorno Actualizadas
- Agregado `LOGS_SERVICE_PORT=5006`
- Agregado `LOGS_SERVICE_URL=http://localhost:5006/api/logs`

#### Scripts de Ejecución
- **run_all.bat/sh actualizados** para incluir Logs Service
- Nuevos mensajes informativos con URLs de Swagger

### 🗑️ Eliminado

- Carpeta temporal "Modelos Frontend" eliminada
- Archivos duplicados de scripts en raíz movidos a backend/

### 🐛 Correcciones

- **Encoding UTF-8** corregido en `common/database.py` para Windows
- **Sintaxis SQL** corregida en scripts de inicialización
- **Hash de contraseña admin** corregido con script `fix_admin_password.py`

---

## [1.0.0] - 2025-12-10 (Versión Inicial)

### ⭐ Añadido

#### Microservicios Base
- **Auth Service** (5001): Autenticación con JWT y gestión de usuarios/roles
- **Inventario Service** (5002): Gestión de productos y tratamientos con motor de recetas
- **Historia Clínica Service** (5003): Pacientes e historias médicas
- **Facturación Service** (5004): Facturas, gastos y reportes financieros
- **Citas Service** (5005): Agendamiento y gestión de citas médicas

#### Base de Datos
- **13 tablas iniciales** en PostgreSQL (Neon.tech)
- **Pool de conexiones** con gestión eficiente
- **Índices optimizados** para consultas frecuentes

#### Seguridad
- **Autenticación JWT** con middleware personalizado
- **RBAC** (Control de acceso basado en roles)
- **Hash de contraseñas** con bcrypt
- **CORS configurado** para integración con frontend

#### API y Documentación
- **Swagger UI** en todos los servicios
- **Endpoints RESTful** bien estructurados
- **Respuestas estándar** con formato JSON consistente

#### Scripts y Utilidades
- `setup_database.py`: Inicialización automática de BD
- `fix_admin_password.py`: Reseteo de contraseña admin
- `run_all.bat/sh`: Ejecución de todos los servicios
- `install.bat/sh`: Script de instalación

#### Características Especiales
- **Motor de Recetas**: Descuento automático de inventario al aplicar tratamientos
- **Validación Ecuador**: Cédula, RUC, compatibilidad con SRI
- **Cálculo automático**: IVA, utilidad, costos
- **Datos de ejemplo**: Roles, admin, productos y tratamientos

---

## Leyenda de Símbolos

- ⭐ **Añadido**: Nuevas características
- 🔄 **Cambios**: Modificaciones en funcionalidad existente
- 🐛 **Correcciones**: Bugs resueltos
- 🗑️ **Eliminado**: Características removidas
- 🔒 **Seguridad**: Mejoras de seguridad
- 📚 **Documentación**: Cambios en docs

---

## Roadmap - Próximas Versiones

### [1.2.0] - Planeado
- [ ] Integración real del logger en todos los servicios
- [ ] Tests automatizados para Logs Service
- [ ] Dashboard web para visualizar logs
- [ ] Exportación de logs a CSV/JSON
- [ ] Alertas automáticas para errores críticos

### [2.0.0] - Futuro
- [ ] Frontend completo (React/Vue)
- [ ] Sistema de notificaciones (Email/SMS)
- [ ] Reportes avanzados con gráficos
- [ ] Integración con facturación electrónica SRI
- [ ] App móvil (React Native/Flutter)

---

**Mantenido por**: Equipo de Desarrollo Sistema Médico
**Última actualización**: 2025-12-10
