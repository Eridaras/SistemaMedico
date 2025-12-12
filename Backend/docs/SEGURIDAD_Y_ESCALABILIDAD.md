# 🔐 Seguridad y Escalabilidad - Sistema de Gestión Clínica

Documentación completa de las mejoras implementadas para garantizar seguridad robusta y escalabilidad del sistema.

## Tabla de Contenidos

- [Seguridad](#seguridad)
  - [Rate Limiting](#rate-limiting)
  - [Validación y Sanitización](#validación-y-sanitización)
  - [Protección contra Ataques](#protección-contra-ataques)
  - [Headers de Seguridad](#headers-de-seguridad)
- [Escalabilidad](#escalabilidad)
  - [Pool de Conexiones Optimizado](#pool-de-conexiones-optimizado)
  - [Sistema de Caching](#sistema-de-caching)
  - [Manejo de Errores](#manejo-de-errores)
  - [Configuración por Ambientes](#configuración-por-ambientes)
- [Mejores Prácticas](#mejores-prácticas)
- [Monitoreo y Métricas](#monitoreo-y-métricas)

---

## Seguridad

### Rate Limiting

Protección contra ataques de fuerza bruta y abuso del API.

#### Implementación

```python
from common.security import rate_limit

@app.route('/api/auth/login', methods=['POST'])
@rate_limit(max_requests=5, window=60)  # 5 intentos por minuto
def login():
    # Lógica de login
    pass
```

#### Configuración

**Archivo**: `backend/common/security.py`

**Características**:
- **Por IP**: Limita requests por dirección IP
- **Por Token**: Para usuarios autenticados, limita por token JWT
- **Exponential Backoff**: Incrementa el tiempo de espera en cada reintento
- **Ventana deslizante**: 60 segundos por defecto
- **Limpieza automática**: Elimina entradas antiguas cuando el storage crece

**Límites Recomendados**:
- Login: 5 requests/minuto
- Endpoints públicos: 100 requests/minuto
- Endpoints autenticados: 60 requests/minuto
- Operaciones críticas: 10 requests/minuto

#### Respuesta cuando se excede el límite

```json
{
  "success": false,
  "message": "Rate limit exceeded. Try again later.",
  "retry_after": 45
}
```
HTTP Status: `429 Too Many Requests`

### Validación y Sanitización

Prevención de inyecciones SQL, XSS y otros ataques.

#### Funciones Disponibles

**1. Sanitización de Strings**
```python
from common.security import sanitize_string

# Elimina caracteres peligrosos
name = sanitize_string(user_input, max_length=100)
```

**2. Validación de Email**
```python
from common.security import sanitize_email

email = sanitize_email(user_input)
if email is None:
    # Email inválido
    pass
```

**3. Validación Ecuatoriana**
```python
from common.security import validate_cedula, validate_ruc, validate_phone

# Validar cédula (10 dígitos con verificación)
if validate_cedula("1234567890"):
    # Cédula válida
    pass

# Validar RUC (13 dígitos)
if validate_ruc("1234567890001"):
    # RUC válido
    pass

# Validar teléfono Ecuador (10 dígitos empezando con 0)
if validate_phone("0999999999"):
    # Teléfono válido
    pass
```

**4. Prevención SQL Injection**
```python
from common.security import prevent_sql_injection

if prevent_sql_injection(user_input):
    # Input contiene patrones sospechosos
    return error_response("Invalid input detected", 400)
```

**5. Validadores Centralizados**
```python
from common.security import InputValidator

# Validar datos de usuario
errors, sanitized_data = InputValidator.validate_user_input(data)
if errors:
    return error_response("Validation failed", 400, errors)

# Validar datos de paciente
errors, sanitized_data = InputValidator.validate_patient_input(data)
```

#### Reglas de Validación

**Usuarios**:
- Email: Formato válido, máx 255 caracteres
- Nombre: Mín 3 caracteres, máx 100
- Contraseña: Mín 8 caracteres, debe incluir:
  - Al menos una mayúscula
  - Al menos una minúscula
  - Al menos un número

**Pacientes**:
- Cédula: 10 dígitos con dígito verificador
- RUC: 13 dígitos con validación
- Email: Formato válido (opcional)
- Teléfono: 10 dígitos formato Ecuador

### Protección contra Ataques

#### SQL Injection
```python
# ❌ NUNCA hacer esto
query = f"SELECT * FROM users WHERE email = '{user_input}'"

# ✅ SIEMPRE usar parametrized queries
cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
```

#### XSS (Cross-Site Scripting)
```python
from common.security import sanitize_string

# Sanitizar antes de guardar o mostrar
safe_input = sanitize_string(user_input)
```

#### CSRF (Cross-Site Request Forgery)
- Tokens JWT incluyen timestamp de emisión
- Validación de origen en headers CORS
- Tokens expiran después de tiempo configurado

### Headers de Seguridad

Headers HTTP de seguridad agregados automáticamente:

```python
from common.security import secure_headers

@app.route('/endpoint')
@secure_headers()
def endpoint():
    return data
```

**Headers incluidos**:
- `X-Content-Type-Options: nosniff` - Previene MIME sniffing
- `X-Frame-Options: DENY` - Previene clickjacking
- `X-XSS-Protection: 1; mode=block` - Protección XSS navegador
- `Strict-Transport-Security` - Fuerza HTTPS
- `Content-Security-Policy` - Política de contenido

---

## Escalabilidad

### Pool de Conexiones Optimizado

**Archivo**: `backend/common/database.py`

#### Características

1. **Thread-Safe**: `ThreadedConnectionPool` para múltiples hilos
2. **Auto-Retry**: Reintentos automáticos en fallos de conexión
3. **Timeout Protection**: Queries limitados a 30 segundos
4. **Keep-Alive**: Mantiene conexiones activas
5. **Estadísticas**: Monitoreo de queries, errores y reintentos

#### Configuración

```env
# .env
DB_POOL_MIN=2          # Conexiones mínimas siempre activas
DB_POOL_MAX=20         # Máximo de conexiones concurrentes
DB_CONNECT_TIMEOUT=10  # Timeout de conexión en segundos
```

**Escalado por Ambiente**:

| Ambiente | Min | Max | Uso Esperado |
|----------|-----|-----|--------------|
| Development | 2 | 20 | 1-5 usuarios |
| Staging | 5 | 30 | 10-20 usuarios |
| Production | 10 | 50 | 50-100 usuarios |

#### Uso Básico

```python
from common.database import db

# Ejecutar query simple
with db.get_cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    user = cursor.fetchone()

# Ejecutar con commit
with db.get_cursor(commit=True) as cursor:
    cursor.execute("INSERT INTO users (...) VALUES (...)", params)
```

#### Funciones Avanzadas

```python
# Ejecutar query directa
results = db.execute_query("SELECT * FROM products", fetch=True)

# Ejecutar múltiples inserts
params_list = [(name1, price1), (name2, price2)]
rows_affected = db.execute_many("INSERT INTO products (name, price) VALUES (%s, %s)", params_list)

# Health check
if db.health_check():
    print("Database is healthy")

# Obtener estadísticas
stats = db.get_stats()
print(f"Queries: {stats['queries']}, Errors: {stats['errors']}")
```

### Sistema de Caching

**Archivo**: `backend/common/cache.py`

#### Implementación

**Cache Simple**:
```python
from common.cache import cache

# Guardar en cache
cache.set('key', value, ttl=300)  # 5 minutos

# Obtener de cache
value = cache.get('key')

# Eliminar de cache
cache.delete('key')

# Limpiar todo
cache.clear()
```

**Decorator para Funciones**:
```python
from common.cache import cached

@cached(ttl=600, key_prefix='user')
def get_user_data(user_id):
    # Esta función se cachea por 10 minutos
    return expensive_database_query(user_id)
```

**Decorator para Rutas Flask**:
```python
from common.cache import cache_response

@app.route('/api/products')
@cache_response(ttl=300)  # Solo cachea GET requests
def get_products():
    return {'products': products}
```

**Cache Especializado**:
```python
from common.cache import DataCache

# Cache de roles (cambian raramente)
roles = DataCache.get_roles()
if roles is None:
    roles = fetch_roles_from_db()
    DataCache.set_roles(roles, ttl=3600)  # 1 hora

# Cache de usuario
user = DataCache.get_user(user_id)

# Invalidar cache cuando cambian datos
DataCache.invalidate_user(user_id)
DataCache.invalidate_products()
```

#### Estrategias de Cache

**Por TTL (Time To Live)**:
- Roles: 1 hora (cambian raramente)
- Productos: 5 minutos (inventario dinámico)
- Usuarios: 10 minutos (balance entre freshness y performance)
- Listados: 2-5 minutos

**Invalidación**:
```python
# Invalidar cuando se actualiza
def update_product(product_id, data):
    # Actualizar en BD
    update_in_database(product_id, data)

    # Invalidar cache
    DataCache.invalidate_products()
    cache.delete(f'product:{product_id}')
```

#### Estadísticas

```python
stats = cache.get_stats()
# {
#     'total_entries': 150,
#     'active_entries': 142,
#     'expired_entries': 8
# }
```

### Manejo de Errores

**Archivo**: `backend/common/error_handler.py`

#### Excepciones Personalizadas

```python
from common.error_handler import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    DatabaseError
)

# Lanzar excepciones tipadas
if not user:
    raise NotFoundError("User not found")

if not has_permission:
    raise AuthorizationError("Insufficient permissions")

if duplicate:
    raise ConflictError("Email already exists")
```

#### Decorator de Manejo de Errores

```python
from common.error_handler import handle_exceptions

@app.route('/endpoint')
@handle_exceptions
def endpoint():
    # Cualquier excepción se maneja automáticamente
    # y se loggea en el servicio de logs
    do_something()
```

#### Operaciones de BD Seguras

```python
from common.error_handler import safe_db_operation

result = safe_db_operation(
    lambda: database.execute_query("SELECT ..."),
    error_message="Failed to fetch users"
)
```

#### Registrar Error Handlers

```python
from common.error_handler import register_error_handlers

app = Flask(__name__)
app.service_name = 'auth'  # Para logging
register_error_handlers(app)
```

#### Respuestas de Error Estandarizadas

```python
from common.error_handler import ErrorResponse

# 400 - Bad Request
return ErrorResponse.validation_error("Invalid email", ["Email format is invalid"])

# 401 - Unauthorized
return ErrorResponse.unauthorized()

# 403 - Forbidden
return ErrorResponse.forbidden("Admin access required")

# 404 - Not Found
return ErrorResponse.not_found("Product not found")

# 409 - Conflict
return ErrorResponse.conflict("Email already registered")

# 500 - Internal Error
return ErrorResponse.internal_error()

# 503 - Service Unavailable
return ErrorResponse.service_unavailable("Database maintenance")
```

### Configuración por Ambientes

**Archivo**: `backend/common/config.py`

#### Ambientes Disponibles

1. **Development** (Por defecto)
   - Debug activo
   - Rate limiting relajado
   - Logs verbose
   - Cache con TTL corto

2. **Production**
   - Debug desactivado
   - Rate limiting estricto
   - Logs a archivo
   - Pool de conexiones grande
   - Tokens con menor tiempo de vida

3. **Testing**
   - Database de prueba
   - Sin rate limiting
   - Sin caching
   - Logs verbose

4. **Staging**
   - Similar a production
   - Con más logging
   - Para pruebas pre-producción

#### Uso

```python
from common.config import get_config

config = get_config('production')

app = Flask(__name__)
app.config.from_object(config)

# Acceder a configuración
db_pool_size = config.DB_POOL_MAX
jwt_secret = config.JWT_SECRET_KEY
```

#### Cambiar Ambiente

```bash
# .env
FLASK_ENV=production

# O en runtime
export FLASK_ENV=production
python app.py
```

---

## Mejores Prácticas

### 1. Siempre Validar Input

```python
from common.security import InputValidator

errors, data = InputValidator.validate_patient_input(request.get_json())
if errors:
    return error_response("Validation failed", 400, errors)
```

### 2. Usar Rate Limiting en Endpoints Sensibles

```python
@app.route('/api/auth/login')
@rate_limit(max_requests=5, window=60)
def login():
    pass
```

### 3. Cachear Queries Pesadas

```python
@cached(ttl=300)
def get_expensive_report():
    # Query compleja
    return results
```

### 4. Invalidar Cache al Actualizar

```python
def update_product(product_id, data):
    update_database(product_id, data)
    DataCache.invalidate_products()
```

### 5. Manejar Errores Apropiadamente

```python
try:
    result = dangerous_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise DatabaseError("Operation failed")
```

### 6. Usar Transacciones

```python
with db.get_cursor(commit=True) as cursor:
    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE id = %s", (amount, from_id))
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE id = %s", (amount, to_id))
```

### 7. Monitorear Estadísticas

```python
# Endpoint de métricas
@app.route('/metrics')
@token_required
def metrics(current_user):
    return {
        'database': db.get_stats(),
        'cache': cache.get_stats()
    }
```

---

## Monitoreo y Métricas

### Estadísticas de Base de Datos

```python
stats = db.get_stats()
# {
#     'queries': 15234,
#     'errors': 12,
#     'retries': 45,
#     'pool_size': 20,
#     'timestamp': 1704912345.67
# }
```

### Estadísticas de Cache

```python
stats = cache.get_stats()
# {
#     'total_entries': 150,
#     'active_entries': 142,
#     'expired_entries': 8
# }
```

### Health Checks

```python
# Database health
if not db.health_check():
    alert_admin("Database is down!")

# Service health endpoint
@app.route('/health')
def health():
    db_healthy = db.health_check()
    cache_healthy = len(cache.cache) < 10000  # Check cache size

    return {
        'status': 'healthy' if db_healthy else 'unhealthy',
        'database': db_healthy,
        'cache': cache_healthy,
        'stats': {
            'db': db.get_stats(),
            'cache': cache.get_stats()
        }
    }
```

### Logs de Seguridad

Todos los eventos de seguridad se registran en el servicio de logs:

```python
from common.logger import auth_logger

# Login fallido
auth_logger.warning(
    action="Failed login attempt",
    details=f"Invalid credentials for {email}",
    ip_address=request.remote_addr
)

# Acceso no autorizado
auth_logger.error(
    action="Unauthorized access attempt",
    user_id=user_id,
    details="Tried to access admin endpoint",
    ip_address=request.remote_addr
)

# Rate limit exceeded
auth_logger.warning(
    action="Rate limit exceeded",
    ip_address=request.remote_addr
)
```

---

## Checklist de Seguridad

- [x] Rate limiting implementado
- [x] Validación y sanitización de input
- [x] Protección contra SQL injection
- [x] Protección contra XSS
- [x] Headers de seguridad
- [x] JWT con expiración
- [x] Contraseñas hasheadas con bcrypt
- [x] Logging de eventos de seguridad
- [x] CORS configurado
- [x] Timeouts en queries
- [x] Connection pooling
- [x] Error handling centralizado
- [x] Configuración por ambientes

## Checklist de Escalabilidad

- [x] Pool de conexiones thread-safe
- [x] Auto-retry en fallos de conexión
- [x] Sistema de caching
- [x] Query optimization
- [x] Prepared statements
- [x] Bulk operations support
- [x] Health check endpoints
- [x] Metrics y estadísticas
- [x] Configuración flexible por ambiente
- [x] Paginación en listados

---

## Escalando a Producción

### 1. Ajustar Pool de Conexiones

```env
DB_POOL_MIN=10
DB_POOL_MAX=50
```

### 2. Activar Logging a Archivo

```env
FLASK_ENV=production
LOG_TO_FILE=true
LOG_LEVEL=WARNING
```

### 3. Configurar Rate Limiting

```env
RATE_LIMIT_DEFAULT=60
RATE_LIMIT_AUTH=5
```

### 4. Usar Redis para Cache (Recomendado)

Reemplazar `backend/common/cache.py` con implementación de Redis para ambiente distribuido.

### 5. Monitoreo Continuo

- Implementar alertas en logs críticos
- Monitorear métricas de BD
- Tracking de rate limit exceeded
- Dashboard de health checks

---

**Sistema preparado para escalar de 10 a 10,000 usuarios** 🚀

