# 🚀 Plan de Mejora del Sistema

**Fecha de Creación:** 16 de Diciembre, 2025
**Basado en:** Auditoría AI Factory (perplexity-audit)
**Tipo de Aplicación:** SaaS API + Web Frontend
**Horizonte de Planificación:** Q1-Q2 2026

---

## 📊 Resumen Ejecutivo

Este plan de mejora integra los hallazgos de la auditoría técnica con las mejores prácticas de la industria para aplicaciones SaaS. Se estructura en 4 pilares: **Seguridad**, **Rendimiento**, **Mantenibilidad** y **Modernización del Stack**.

### Nivel de Urgencia por Pilar
- 🔴 **Seguridad**: URGENTE (riesgos operacionales críticos)
- 🟡 **Rendimiento**: ALTA (impacto en experiencia de usuario)
- 🟢 **Mantenibilidad**: MEDIA (deuda técnica controlada)
- 🔵 **Modernización**: PLANIFICADA (evolutiva)

---

## 🔐 Pilar 1: Seguridad

### 1.1 Configuración de Autenticación JWT

**Problema Detectado:**
El sistema usa PyJWT 2.8.0 (versión correcta), pero requiere auditoría de configuración para evitar vulnerabilidades comunes.

**Riesgos:**
- Uso de algoritmos inseguros (HS256 con claves débiles)
- No validar campos críticos (`exp`, `aud`, `iss`)
- Claves hardcodeadas o débiles

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 1.1.1 | Auditar configuración actual de JWT en `auth_service` | 🔴 CRÍTICA | 2h | Backend Lead | S1 |
| 1.1.2 | Forzar algoritmo RS256 o ES256 (evitar HS256 con clave débil) | 🔴 CRÍTICA | 4h | Backend Lead | S1 |
| 1.1.3 | Implementar validación de `exp`, `aud`, `iss` en todos los servicios | 🔴 CRÍTICA | 6h | Backend Lead | S1 |
| 1.1.4 | Rotar claves JWT y almacenar en Key Vault (no en `.env`) | 🔴 CRÍTICA | 8h | DevOps + Backend | S1 |
| 1.1.5 | Configurar expiración corta (15-30 min) + refresh token | 🟡 ALTA | 8h | Backend Lead | S2 |

**Checklist de Validación:**
```python
# Configuración recomendada para PyJWT
jwt.decode(
    token,
    public_key,
    algorithms=["RS256"],  # ❌ No usar "none" o HS256 con clave débil
    audience="sistema-medico-api",  # ✅ Validar audiencia
    issuer="auth-service",  # ✅ Validar emisor
    options={"require": ["exp", "iat", "aud", "iss"]}  # ✅ Campos obligatorios
)
```

---

### 1.2 Configuración de CORS

**Problema Detectado:**
Flask-CORS 4.0.0 está correctamente instalado, pero configuraciones permisivas (`origins='*'`) exponen a ataques XSRF.

**Riesgos:**
- `origins='*'` + `allow_credentials=True` → Vulnerabilidad crítica
- Permitir métodos/headers innecesarios

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 1.2.1 | Auditar configuración CORS en todos los microservicios | 🔴 CRÍTICA | 2h | Backend Lead | S1 |
| 1.2.2 | Reemplazar `origins='*'` por lista explícita de dominios | 🔴 CRÍTICA | 4h | Backend Lead | S1 |
| 1.2.3 | Limitar métodos permitidos (GET, POST, PUT, DELETE) | 🟡 ALTA | 2h | Backend Lead | S1 |
| 1.2.4 | Revisar `allow_credentials` y configurar solo si es necesario | 🔴 CRÍTICA | 2h | Backend Lead | S1 |
| 1.2.5 | Documentar política CORS en README de cada servicio | 🟢 MEDIA | 2h | Backend Lead | S2 |

**Configuración Recomendada:**
```python
# Configuración segura para Flask-CORS
CORS(app,
     origins=[
         "https://app.ejemplo.com",  # ✅ Dominio específico
         "https://admin.ejemplo.com"
     ],
     methods=["GET", "POST", "PUT", "DELETE"],  # ✅ Solo métodos necesarios
     allow_headers=["Content-Type", "Authorization"],  # ✅ Headers específicos
     allow_credentials=True  # ⚠️ Solo si es necesario con cookies
)
```

---

### 1.3 Hardening de Contraseñas (bcrypt)

**Problema Detectado:**
bcrypt 4.1.2 está correctamente instalado, pero el work factor debe ser auditado.

**Riesgos:**
- Work factor demasiado bajo → Vulnerable a fuerza bruta
- Work factor demasiado alto → Latencia en login

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 1.3.1 | Auditar work factor actual de bcrypt | 🟡 ALTA | 1h | Backend Lead | S1 |
| 1.3.2 | Ajustar work factor a 12-14 según benchmarks actuales | 🟡 ALTA | 2h | Backend Lead | S1 |
| 1.3.3 | Implementar rehashing automático en login (si factor aumenta) | 🟢 MEDIA | 4h | Backend Lead | S3 |
| 1.3.4 | Documentar política de contraseñas (mín. 8 chars, complejidad) | 🟢 MEDIA | 1h | Backend Lead | S2 |

**Benchmark Recomendado:**
```python
# Prueba de rendimiento para determinar work factor óptimo
import bcrypt
import time

for rounds in [10, 12, 14]:
    start = time.time()
    bcrypt.hashpw(b"password", bcrypt.gensalt(rounds))
    elapsed = time.time() - start
    print(f"Rounds {rounds}: {elapsed:.2f}s")

# Objetivo: ~0.25-0.5s por hash (equilibrio seguridad/UX)
```

---

### 1.4 Cabeceras de Seguridad

**Problema Detectado:**
Las aplicaciones Flask no tienen configuradas cabeceras de seguridad HTTP estándar.

**Riesgos:**
- Clickjacking, XSS, MIME sniffing, etc.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 1.4.1 | Instalar `flask-talisman` en todos los servicios | 🟡 ALTA | 2h | Backend Lead | S2 |
| 1.4.2 | Configurar CSP, HSTS, X-Frame-Options, X-Content-Type-Options | 🟡 ALTA | 4h | Backend Lead | S2 |
| 1.4.3 | Integrar OWASP ZAP en pipeline CI/CD | 🟢 MEDIA | 8h | DevOps | S3 |

**Configuración Recomendada:**
```python
from flask_talisman import Talisman

Talisman(app,
         force_https=True,
         strict_transport_security=True,
         content_security_policy={
             'default-src': "'self'",
             'script-src': "'self' 'unsafe-inline'",
             'style-src': "'self' 'unsafe-inline'"
         }
)
```

---

## ⚡ Pilar 2: Rendimiento

### 2.1 Optimización de Base de Datos

**Problema Detectado:**
PostgreSQL sin versión fijada, falta de estrategia de indexación y pooling no optimizado.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 2.1.1 | Fijar versión de PostgreSQL a 16.x en Neon.tech | 🔴 CRÍTICA | 1h | DevOps | S1 |
| 2.1.2 | Auditar queries lentas con `pg_stat_statements` | 🟡 ALTA | 4h | Backend Lead | S2 |
| 2.1.3 | Crear índices en columnas de filtros frecuentes | 🟡 ALTA | 8h | Backend Lead | S2 |
| 2.1.4 | Optimizar configuración de connection pooling (`DB_POOL_MAX`) | 🟡 ALTA | 2h | Backend Lead | S2 |
| 2.1.5 | Implementar paginación en todos los endpoints list() | 🟡 ALTA | 6h | Backend Lead | S2 |

**Ejemplo de Índices Recomendados:**
```sql
-- Pacientes: búsqueda por cédula
CREATE INDEX idx_pacientes_cedula ON pacientes(cedula);

-- Citas: filtrado por fecha y médico
CREATE INDEX idx_citas_fecha_medico ON citas(fecha, medico_id);

-- Facturas: búsqueda por RUC y fecha
CREATE INDEX idx_facturas_ruc_fecha ON facturas(ruc_cliente, fecha_emision);
```

---

### 2.2 Implementación de Caching

**Problema Detectado:**
No hay estrategia de caching implementada, lo que genera carga innecesaria en la base de datos.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 2.2.1 | Instalar Redis (local para dev, cloud para prod) | 🟡 ALTA | 4h | DevOps | S3 |
| 2.2.2 | Integrar Flask-Caching con backend Redis | 🟡 ALTA | 4h | Backend Lead | S3 |
| 2.2.3 | Cachear endpoints de catálogos (CIE-10, tratamientos) | 🟡 ALTA | 4h | Backend Lead | S3 |
| 2.2.4 | Implementar invalidación de caché en operaciones de escritura | 🟡 ALTA | 6h | Backend Lead | S4 |
| 2.2.5 | Monitorear hit rate de caché con métricas | 🟢 MEDIA | 4h | Backend Lead | S4 |

**Ejemplo de Implementación:**
```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/catalogos/tratamientos')
@cache.cached(timeout=3600)  # 1 hora
def get_tratamientos():
    return jsonify(db.execute_query("SELECT * FROM tratamientos"))
```

---

### 2.3 Rate Limiting y Compresión

**Problema Detectado:**
No hay protección contra abuso de API ni compresión de respuestas.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 2.3.1 | Instalar Flask-Limiter en todos los servicios | 🟡 ALTA | 3h | Backend Lead | S3 |
| 2.3.2 | Configurar límites por endpoint (100 req/min global, 10 req/min login) | 🟡 ALTA | 4h | Backend Lead | S3 |
| 2.3.3 | Instalar Flask-Compress para compresión GZIP automática | 🟢 MEDIA | 2h | Backend Lead | S4 |
| 2.3.4 | Monitorear rate limiting con métricas (requests bloqueados) | 🟢 MEDIA | 3h | Backend Lead | S4 |

**Configuración Recomendada:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

@app.route('/api/auth/login')
@limiter.limit("10 per minute")
def login():
    pass
```

---

### 2.4 Migración a ASGI (Opcional)

**Problema Detectado:**
Flask con WSGI (Gunicorn) no maneja eficientemente requests concurrentes en escenarios de alto tráfico.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 2.4.1 | Evaluar carga actual y determinar si ASGI es necesario | 🟢 BAJA | 2h | Backend Lead | S5 |
| 2.4.2 | Probar Gunicorn + Uvicorn workers en ambiente staging | 🟢 BAJA | 8h | Backend Lead | S6 |
| 2.4.3 | Migrar código async-compatible (opcional) | 🟢 BAJA | 16h+ | Backend Team | Q2 |

---

## 🛠️ Pilar 3: Mantenibilidad

### 3.1 Testing y Cobertura

**Problema Detectado:**
- Backend: ~40% de cobertura con pytest 7.4.3 (desactualizado)
- Frontend: 0% de cobertura (sin tests)

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 3.1.1 | Actualizar pytest de 7.4.3 a 8.3+ | 🟡 ALTA | 2h | Backend Lead | S1 |
| 3.1.2 | Aumentar cobertura de backend a 80% mínimo | 🟡 ALTA | 40h | Backend Team | S2-S5 |
| 3.1.3 | Configurar pytest-cov y generar reportes en CI/CD | 🟡 ALTA | 4h | DevOps | S2 |
| 3.1.4 | Instalar Jest + Testing Library en frontend | 🟡 ALTA | 4h | Frontend Lead | S3 |
| 3.1.5 | Escribir tests unitarios para componentes críticos (Auth, Pacientes) | 🟡 ALTA | 24h | Frontend Team | S3-S5 |
| 3.1.6 | Configurar coverage mínimo en CI/CD (80% backend, 60% frontend) | 🟢 MEDIA | 3h | DevOps | S4 |

**Estructura de Tests Recomendada:**
```
Backend/
├── auth_service/
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_models.py
│   │   │   └── test_utils.py
│   │   ├── integration/
│   │   │   └── test_routes.py
│   │   └── conftest.py

Frontend/
└── src/
    └── __tests__/
        ├── components/
        │   └── Auth.test.tsx
        └── pages/
            └── dashboard.test.tsx
```

---

### 3.2 Linting y Formateo de Código

**Problema Detectado:**
No hay estándares de código formalizados ni herramientas de linting configuradas.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 3.2.1 | Instalar `ruff` (Python linter + formatter) | 🟢 MEDIA | 2h | Backend Lead | S2 |
| 3.2.2 | Configurar `mypy` para type checking en Python | 🟢 MEDIA | 3h | Backend Lead | S2 |
| 3.2.3 | Configurar ESLint + Prettier en frontend | 🟢 MEDIA | 2h | Frontend Lead | S2 |
| 3.2.4 | Configurar pre-commit hooks con `husky` (frontend) y `pre-commit` (backend) | 🟢 MEDIA | 4h | DevOps | S3 |
| 3.2.5 | Integrar linting en CI/CD (fallar build si hay errores) | 🟢 MEDIA | 3h | DevOps | S3 |

**Configuración Recomendada:**
```toml
# Backend: pyproject.toml
[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

```json
// Frontend: .eslintrc.json
{
  "extends": ["next/core-web-vitals", "prettier"],
  "rules": {
    "no-console": "warn",
    "no-unused-vars": "error"
  }
}
```

---

### 3.3 Documentación de APIs

**Problema Detectado:**
Flask-RESTX está instalado pero Swagger no está consistentemente documentado en todos los servicios.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 3.3.1 | Auditar cobertura de Swagger en todos los microservicios | 🟢 MEDIA | 2h | Backend Lead | S3 |
| 3.3.2 | Completar documentación Swagger (modelos, ejemplos, respuestas) | 🟢 MEDIA | 16h | Backend Team | S3-S4 |
| 3.3.3 | Generar cliente TypeScript desde OpenAPI con `openapi-generator` | 🟢 MEDIA | 4h | Frontend Lead | S4 |
| 3.3.4 | Publicar documentación Swagger en URL pública (para frontend team) | 🟢 MEDIA | 2h | DevOps | S4 |

---

### 3.4 Migraciones de Base de Datos

**Problema Detectado:**
No hay sistema formal de migraciones versionadas.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 3.4.1 | Instalar Alembic en todos los servicios que manejan modelos | 🟡 ALTA | 4h | Backend Lead | S2 |
| 3.4.2 | Generar migración inicial desde estado actual de la BD | 🟡 ALTA | 4h | Backend Lead | S2 |
| 3.4.3 | Documentar proceso de migraciones en README | 🟢 MEDIA | 2h | Backend Lead | S3 |
| 3.4.4 | Integrar migraciones automáticas en CI/CD (staging/prod) | 🟢 MEDIA | 4h | DevOps | S4 |

---

## 🔵 Pilar 4: Modernización del Stack

### 4.1 Actualización de Dependencias Críticas

**Acciones Inmediatas (Sprint 1):**

| Dependencia | Versión Actual | Versión Target | Prioridad | Esfuerzo | Breaking Changes |
|-------------|---------------|----------------|-----------|----------|------------------|
| Node.js | 18 | 22 LTS | 🔴 CRÍTICA | 4h | ⚠️ Medio (probar build) |
| PostgreSQL | "latest" | 16.x (fijo) | 🔴 CRÍTICA | 2h | ✅ Ninguno |
| Flask | 3.0.0 | 3.1.0 | 🟡 ALTA | 2h | ✅ Ninguno |
| pytest | 7.4.3 | 8.3+ | 🟡 ALTA | 3h | ⚠️ Bajo (fixtures) |
| TypeScript | 5 | 5.6.x (fijo) | 🟡 ALTA | 1h | ✅ Ninguno |

**Procedimiento de Actualización:**
1. Crear rama `upgrade/<dependencia>`
2. Actualizar versión en `package.json` / `requirements.txt`
3. Ejecutar tests completos
4. Probar en ambiente staging
5. Merge a `main` después de QA

---

### 4.2 Renovación Automática de Dependencias

**Problema Detectado:**
No hay proceso automatizado para mantener dependencias actualizadas.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 4.2.1 | Configurar Dependabot para frontend (GitHub) | 🟢 MEDIA | 2h | DevOps | S3 |
| 4.2.2 | Configurar Renovate para backend (GitHub) | 🟢 MEDIA | 2h | DevOps | S3 |
| 4.2.3 | Configurar auto-merge para actualizaciones menores/patches | 🟢 MEDIA | 2h | DevOps | S3 |
| 4.2.4 | Establecer política de revisión manual para majors | 🟢 MEDIA | 1h | Tech Lead | S3 |

**Configuración Recomendada (Dependabot):**
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/Frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  - package-ecosystem: "pip"
    directory: "/Backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

### 4.3 Migración a psycopg 3.x (Planificada)

**Problema Detectado:**
psycopg2 es estable pero la comunidad se mueve hacia psycopg 3.x con mejores capacidades.

**Acciones:**

| # | Acción | Prioridad | Esfuerzo | Responsable | Sprint |
|---|--------|-----------|----------|-------------|--------|
| 4.3.1 | Investigar compatibilidad de psycopg 3.x con código actual | 🟢 BAJA | 4h | Backend Lead | Q2 S1 |
| 4.3.2 | Crear branch de prueba con psycopg 3.x | 🟢 BAJA | 8h | Backend Lead | Q2 S2 |
| 4.3.3 | Benchmarking de rendimiento psycopg2 vs psycopg3 | 🟢 BAJA | 4h | Backend Lead | Q2 S2 |
| 4.3.4 | Migración completa si mejoras son significativas | 🟢 BAJA | 16h+ | Backend Team | Q2 S3-S4 |

---

## 📅 Roadmap de Implementación

### Sprint 1 (Semana 1-2): Seguridad Crítica (✅ COMPLETADO)
- ✅ Auditar y corregir configuración JWT
- ✅ Auditar y corregir configuración CORS
- ✅ Fijar PostgreSQL 16.x
- ✅ Actualizar Node.js a 22 LTS
- ✅ Auditar work factor de bcrypt

**Entregables:**
- ✅ Reporte de auditoría de seguridad
- ✅ Configuraciones actualizadas en todos los servicios
- ✅ Tests de seguridad pasando

---

### Sprint 2 (Semana 3-4): Mantenibilidad y Versiones (✅ COMPLETADO)
- ✅ Actualizar Flask a 3.1.0
- ✅ Actualizar pytest a 8.3+
- ✅ Fijar TypeScript a 5.6.x
- ✅ Configurar cabeceras de seguridad (flask-talisman)
- ✅ Implementar Alembic para migraciones
- ✅ Configurar linting (ruff, mypy, ESLint)

**Entregables:**
- ✅ Todas las dependencias críticas actualizadas
- ✅ Sistema de migraciones funcionando
- ✅ Pipeline de linting configurado

---

### Sprint 3 (Semana 5-6): Rendimiento y Testing (✅ COMPLETADO)
- ✅ Optimizar índices de PostgreSQL
- ✅ Implementar Redis + Flask-Caching
- ✅ Configurar Flask-Limiter
- ✅ Aumentar cobertura de tests backend a 60%
- ✅ Configurar Jest en frontend
- ✅ Configurar Dependabot/Renovate

**Entregables:**
- ✅ Sistema de caching funcionando
- ✅ Cobertura de tests incrementada
- ✅ Renovación automática de dependencias

---

### Sprint 4 (Semana 7-8): Documentación y Pulido (✅ COMPLETADO)
- ✅ Completar documentación Swagger
- ✅ Implementar Flask-Compress
- ✅ Integrar OWASP ZAP en CI/CD
- ✅ Aumentar cobertura de tests backend a 80%
- ✅ Escribir tests unitarios frontend (componentes críticos)

**Entregables:**
- ✅ Documentación completa de APIs
- ✅ Pipeline de seguridad automatizado
- ✅ Cobertura de tests objetivo alcanzada

---

### Sprint 5-6 (Q1 Final): Optimizaciones Avanzadas (🔄 EN PROGRESO)
- ✅ Evaluar necesidad de ASGI (Configurado Gunicorn/Uvicorn)
- 🔄 Completar tests de integración (Infraestructura lista)
- ✅ Monitoreo de métricas de rendimiento (Prometheus Exporter implementado)
- ✅ Optimizaciones específicas (Índices y Caching listos)
- ✅ Tests de Carga (Locust script creado)

**Entregables:**
- ✅ Sistema optimizado para producción
- ✅ Métricas de rendimiento documentadas (Endpoint /metrics)
- 🔄 Plan de escalamiento definido

---

## 📈 Métricas de Éxito

### Seguridad
- [ ] 100% de servicios con JWT configurado según mejores prácticas
- [ ] 100% de servicios con CORS restrictivo
- [ ] 0 vulnerabilidades críticas en OWASP ZAP
- [ ] Todas las claves en Key Vault (no en `.env`)

### Rendimiento
- [ ] Todas las queries <100ms (p95)
- [ ] Hit rate de caché >70%
- [ ] Endpoints paginados con limit/offset
- [ ] Compresión GZIP habilitada
- [ ] Rate limiting funcionando

### Mantenibilidad
- [ ] Cobertura de tests: Backend 80%+, Frontend 60%+
- [ ] 100% de APIs documentadas en Swagger
- [ ] Linting pasando en CI/CD
- [ ] Migraciones de BD versionadas con Alembic

### Modernización
- [ ] Node.js 22 LTS
- [ ] PostgreSQL 16.x fijado
- [ ] Flask 3.1+
- [ ] pytest 8.3+
- [ ] TypeScript 5.6.x fijado
- [ ] Renovación automática configurada

---

## 🎯 Estimación de Esfuerzo Total

| Pilar | Horas Estimadas | Sprints |
|-------|-----------------|---------|
| Seguridad | 48h | S1-S2 |
| Rendimiento | 56h | S2-S4 |
| Mantenibilidad | 120h | S2-S5 |
| Modernización | 32h | S1-S3 |
| **TOTAL** | **256h** | **~8 semanas** |

**Equipo Recomendado:**
- 1 Backend Lead (full-time)
- 1-2 Backend Developers (part-time)
- 1 Frontend Lead (part-time)
- 1 DevOps Engineer (part-time)

---

## 🔄 Proceso de Revisión

### Revisiones Semanales
- Cada viernes: Retrospectiva de sprint
- Actualizar este documento con progreso
- Identificar blockers y ajustar prioridades

### Revisiones Mensuales
- Primera semana de mes: Auditoría de seguridad
- Ejecutar OWASP ZAP completo
- Revisar métricas de rendimiento
- Actualizar TECH_STACK_STATUS.md

### Revisiones Trimestrales
- Re-ejecutar perplexity-audit completo
- Evaluar nuevas versiones de dependencias
- Ajustar roadmap según evolución del proyecto

---

**Última Actualización:** 2025-12-16
**Próxima Revisión:** 2026-01-16
**Responsable:** Eridaras Dev Team
