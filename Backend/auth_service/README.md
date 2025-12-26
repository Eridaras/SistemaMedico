# 🔐 Auth Service - Servicio de Autenticación

Microservicio de autenticación y autorización del Sistema Médico. Gestiona login, registro, roles y permisos con JWT.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Autenticación JWT**: Login seguro con tokens de acceso
- **Gestión de Roles**: Admin, Médico, Recepcionista con permisos granulares
- **Registro de Usuarios**: Creación de nuevas cuentas con validación
- **Renovación de Tokens**: Refresh token para sesiones largas
- **Validación de Email**: Verificación de formato y unicidad
- **Hash de Contraseñas**: Bcrypt con factor configurable
- **Middleware de Autorización**: Decoradores `@token_required` y `@role_required`

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5001/api/auth
```

### Documentación Interactiva
```
http://localhost:5001/docs
```

### Lista de Endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `POST` | `/login` | Iniciar sesión con email/password | No |
| `POST` | `/register` | Registrar nuevo usuario | No |
| `POST` | `/refresh` | Renovar token JWT | Sí |
| `GET` | `/me` | Obtener datos del usuario autenticado | Sí |
| `GET` | `/users` | Listar todos los usuarios | Sí (Admin) |
| `GET` | `/users/:id` | Obtener usuario por ID | Sí (Admin) |
| `PUT` | `/users/:id` | Actualizar usuario | Sí (Admin) |
| `DELETE` | `/users/:id` | Eliminar usuario | Sí (Admin) |
| `GET` | `/roles` | Listar roles disponibles | Sí |

---

## 📊 Modelos de Datos

### User (Usuario)

```python
{
    "user_id": 1,
    "email": "admin@clinica.com",
    "full_name": "Admin Sistema",
    "role_id": 1,
    "is_active": true,
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `user_id` | int | ID único del usuario | PK, Autoincremental |
| `email` | string | Email de acceso | Único, formato email |
| `password_hash` | string | Contraseña hasheada (bcrypt) | Mínimo 8 caracteres |
| `full_name` | string | Nombre completo | Requerido |
| `role_id` | int | ID del rol asignado | FK a `roles` |
| `is_active` | boolean | Estado activo/inactivo | Default: true |
| `created_at` | timestamp | Fecha de creación | Auto |

### Role (Rol)

```python
{
    "role_id": 1,
    "name": "Admin",
    "menu_config": {
        "dashboard": true,
        "patients": true,
        "appointments": true,
        "inventory": true,
        "billing": true,
        "reports": true
    }
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `role_id` | int | ID único del rol |
| `name` | string | Nombre del rol (Admin, Doctor, Receptionist) |
| `menu_config` | jsonb | Configuración de permisos del menú |

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/auth_service
pip install -r ../requirements-base.txt
```

### Variables de Entorno

Crea un archivo `.env` en la raíz del backend:

```env
# Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db

# JWT
JWT_SECRET_KEY=tu_clave_secreta_segura_aqui
JWT_EXPIRATION_HOURS=24
JWT_ALGORITHM=HS256
JWT_ISSUER=clinica-bienestar
JWT_AUDIENCE=clinica-api

# Bcrypt
BCRYPT_LOG_ROUNDS=12

# Flask
FLASK_ENV=development
```

### Migrar Base de Datos

```bash
cd backend
alembic upgrade head
```

---

## 🔧 Configuración

### Configuración de JWT

El servicio utiliza JWT (JSON Web Tokens) para autenticación stateless:

- **Algoritmo**: HS256
- **Expiración**: Configurable (default 24h)
- **Claims**: `user_id`, `email`, `role`, `iss`, `aud`, `exp`

### Configuración de Bcrypt

- **Log Rounds**: 12 (ajustable según hardware)
- **Tiempo estimado**: ~300ms por hash

### Roles Predefinidos

1. **Admin** (`role_id: 1`): Acceso completo al sistema
2. **Médico** (`role_id: 2`): Consultas, historia clínica, citas
3. **Recepcionista** (`role_id: 3`): Citas, pacientes, facturación

---

## 💻 Uso

### Ejecutar el Servicio

#### Modo Desarrollo
```bash
cd backend/auth_service
python app.py
```

El servicio estará disponible en `http://localhost:5001`

#### Modo Producción
```bash
cd backend
gunicorn -c gunicorn_conf.py auth_service.app:app
```

### Ejemplo de Login

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinica.com",
    "password": "admin123"
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "user_id": 1,
      "email": "admin@clinica.com",
      "full_name": "Admin Sistema",
      "role": "Admin"
    }
  }
}
```

### Ejemplo de Uso del Token

```bash
curl -X GET http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_auth.py -v
```

### Casos de Prueba

- ✅ Login con credenciales válidas
- ✅ Login con credenciales inválidas (401)
- ✅ Registro de nuevo usuario
- ✅ Validación de email duplicado
- ✅ Verificación de token JWT
- ✅ Expiración de token
- ✅ Renovación de token
- ✅ Control de acceso por roles

---

## 🔒 Seguridad

### Mejores Prácticas Implementadas

1. **Hash de Contraseñas**: Bcrypt con salt único por usuario
2. **JWT con Claims**: Validación de `iss`, `aud`, `exp`
3. **Validación de Input**: Prevención de inyección SQL
4. **CORS Configurado**: Solo orígenes permitidos
5. **Rate Limiting**: Protección contra brute force (común)
6. **HTTPS**: Recomendado en producción

### Configuración de Seguridad

Ver [../../docs/IMPROVEMENT_PLAN.md](../../docs/IMPROVEMENT_PLAN.md) para el plan de mejora de seguridad.

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5001/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Estructura del Proyecto**: [../ESTRUCTURA_PROYECTO.md](../ESTRUCTURA_PROYECTO.md)
- **Guía de Pruebas**: [../../docs/ESTRATEGIA_PRUEBAS.md](../../docs/ESTRATEGIA_PRUEBAS.md)

---

## 🐛 Troubleshooting

### Error: "Database connection failed"
- Verifica que PostgreSQL esté corriendo
- Verifica el `DATABASE_URL` en `.env`

### Error: "Invalid JWT"
- Verifica que el `JWT_SECRET_KEY` sea el mismo en todos los servicios
- Verifica que el token no haya expirado

### Error: "bcrypt module not found"
- Reinstala: `pip install bcrypt`

---

**Última actualización:** 2025-12-17
