# TECH STACK - Definición Rígida

## REGLA FUNDAMENTAL
**Puerto de Entrada:** `:3333` (Traefik Reverse Proxy)

---

## BACKEND - Flask Microservicios

### Tecnología Core
- **Lenguaje:** Python 3.11+
- **Framework:** Flask 3.1.0
- **Patrón:** Microservicios independientes
- **Comunicación:** HTTP/REST

### Versiones Exactas (requirements-base.txt)
```
Flask==3.1.0
Flask-CORS==4.0.0
flask-restx==1.3.0
flask-talisman==1.1.0
PyJWT==2.8.0
bcrypt==4.1.2
psycopg2-binary==2.9.9
alembic==1.13.3
flask-caching==2.3.0
redis==5.2.1
flask-limiter==3.9.0
flask-compress==1.15
prometheus-flask-exporter==0.23.0
uvicorn[standard]==0.27.1
gunicorn==21.2.0
python-dotenv==1.0.0
requests==2.31.0
```

### Estructura de Servicios
```
backend/
├── common/                 → Shared utilities
├── auth_service/          → Puerto 5001
├── inventario_service/    → Puerto 5002
├── historia_clinica_service/ → Puerto 5003
├── facturacion_service/   → Puerto 5004
├── citas_service/         → Puerto 5005
└── logs_service/          → Puerto 5006
```

**NOTA CRÍTICA:** Estructura actual NO cumple con protocolo OMNISCIENT (requiere `services/{nombre}/src/tests/Dockerfile`)

---

## BASE DE DATOS

### PostgreSQL 16
- **Versión:** 16-alpine (Docker)
- **Driver:** psycopg2-binary 2.9.9
- **Pool:** Min 2, Max 20 conexiones
- **Migrations:** Alembic 1.13.3

### Tablas Principales (14)
- users, roles
- patients, medical_history, clinical_notes
- products, treatments, treatment_recipes
- appointments, appointment_treatments, appointment_extras
- invoices, operational_expenses
- electronic_invoices
- system_logs

---

## DOCKER & ORQUESTACIÓN

### Docker Compose
**Archivo:** `backend/docker-compose.yml`

```yaml
version: '3.9'
services:
  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```

### ⚠️ TRAEFIK REQUERIDO (NO IMPLEMENTADO)
**Estado:** PENDIENTE

**Configuración Esperada:**
```yaml
services:
  traefik:
    image: traefik:v2.9
    command:
      - --api.insecure=true
      - --providers.docker=true
      - --entrypoints.web.address=:3333
    ports:
      - "3333:3333"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
    networks:
      - traefik-net
```

**Red:** `traefik-net` (bridge)

**Servicios Backend con Traefik:**
```yaml
  auth-service:
    build: ./services/auth
    labels:
      - "traefik.http.routers.auth.rule=PathPrefix(`/api/auth`)"
      - "traefik.http.services.auth.loadbalancer.server.port=5000"
    networks:
      - traefik-net
```

---

## FRONTEND - Next.js + React

### Tecnología Core
- **Framework:** Next.js 15.5.9 (App Router)
- **UI Library:** React 19.2.1
- **Lenguaje:** TypeScript 5.6.3
- **Styling:** Tailwind CSS 3.4.1
- **Components:** shadcn/ui (40+ componentes)

### Versiones Exactas (package.json)
```json
{
  "next": "15.5.9",
  "react": "19.2.1",
  "react-dom": "19.2.1",
  "typescript": "5.6.3",
  "tailwindcss": "3.4.1",
  "framer-motion": "12.23.26",
  "recharts": "2.15.1",
  "zod": "3.24.2"
}
```

### Puerto
- **Desarrollo:** 9002
- **Producción:** TBD (via Traefik en :3333)

### Servidor
**Actual:** Node standalone server
**Requerido:** Nginx en contenedor expuesto via Traefik

```yaml
  frontend:
    build: ./frontend
    labels:
      - "traefik.http.routers.front.rule=PathPrefix(`/`)"
      - "traefik.http.services.front.loadbalancer.server.port=3000"
    networks:
      - traefik-net
```

---

## SEGURIDAD

### Autenticación
- **Método:** JWT (JSON Web Tokens)
- **Algoritmo:** HS256 (Producción debe usar RS256)
- **Expiración:** 24 horas
- **Almacenamiento Frontend:** HTTP-only cookies

### Hashing
- **Passwords:** bcrypt (12 rounds)
- **Tiempo hash:** ~0.4s (benchmark)

### Rate Limiting
- **General:** 100 req/min
- **Auth endpoints:** 5 req/min
- **Storage:** Memory (Dev), Redis (Prod)

### Headers de Seguridad
- CSP (Content Security Policy)
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff

---

## CACHING

### Redis 7
- **Uso:** Cache de queries frecuentes
- **TTL Default:** 300 segundos
- **Estrategia:** Lazy loading

**Implementado en:**
- Auth: User queries
- Inventario: Product lists
- Historia Clínica: Patient data

---

## TESTING

### Backend
- **Framework:** pytest + pytest-flask
- **Cobertura Objetivo:** 100%
- **Ubicación:** `backend/tests/`

### Load Testing
- **Herramienta:** Locust
- **Archivo:** `backend/locustfile.py`

### Frontend
- **Pendiente:** Jest + React Testing Library

---

## MONITOREO

### Prometheus Metrics
- **Endpoint:** `/metrics` en cada servicio
- **Métricas:** Request count, latency, errors

### Logging
- **Librería:** Python logging
- **Formato:** JSON structured logs
- **Destino:** Console (Dev), File (Prod)

### Health Checks
- **Endpoint:** `/health` en cada servicio
- **Respuesta:** `{"status": "healthy", "service": "nombre"}`

---

## CI/CD

### GitHub Actions
**Archivo:** `.github/workflows/ci-cd.yml`

**Pipeline:**
1. Lint (flake8, black)
2. Tests (pytest)
3. Build (Docker images)
4. Deploy (Manual approval)

### Dependabot
- Actualizaciones automáticas de dependencias
- PRs semanales

---

## AMBIENTES

### Desarrollo
- **Backend:** Flask debug mode (puertos 5001-5006)
- **Frontend:** Next.js dev server (puerto 9002)
- **DB:** Docker Compose PostgreSQL local

### Producción
- **Backend:** Gunicorn + Uvicorn workers
- **Frontend:** Next.js build + Nginx
- **DB:** PostgreSQL managed (ej: Neon.tech)
- **Proxy:** Traefik :3333
- **Certs:** Let's Encrypt automático

---

## RESTRICCIONES INNEGOCIABLES

### ❌ PROHIBIDO
- Hardcodear URLs absolutas (usar nombres de servicio Docker)
- `debug=True` en producción
- Passwords en plain text
- Archivos .env en git
- Dependencias sin version pinning

### ✅ OBLIGATORIO
- Todos los servicios en red `traefik-net`
- Health check en cada servicio
- Tests antes de merge
- Migrations con Alembic (no DDL manual)
- JWT en todos los endpoints (excepto `/health` y `/login`)

---

## GAPS ACTUALES vs OMNISCIENT

### NO IMPLEMENTADO
❌ Traefik reverse proxy
❌ Red Docker `traefik-net`
❌ Estructura `services/{nombre}/src/tests/Dockerfile`
❌ Frontend en contenedor con Nginx
❌ URLs inter-service via DNS Docker

### IMPLEMENTADO
✅ PostgreSQL Docker
✅ 6 microservicios Flask funcionales
✅ Frontend Next.js funcional
✅ Redis caching
✅ Prometheus metrics
✅ CI/CD pipeline

---

**Última Actualización:** 2025-12-24
**Conformidad con Protocolo:** 60% (requiere reestructuración Docker/Traefik)
