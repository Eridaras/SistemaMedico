# 🧠 CONTEXTO MAESTRO PARA AGENTES Y DESARROLLADORES

> **IMPORTANTE PARA AGENTES DE IA:** Lee este documento ANTES de realizar cualquier tarea. Este es el estado de la verdad del proyecto. Si realizas cambios estructurales importantes, **ACTUALIZA ESTE DOCUMENTO**.

## 1. Identidad del Proyecto
**Nombre:** Sistema Médico - Clínica Bienestar
**Objetivo:** Sistema integral de gestión hospitalaria (HIS) con facturación electrónica nativa para Ecuador (SRI).
**Estado Actual:** MVP Híbrido (Infraestructura de Producción + Frontend Parcialmente Conectado).

---

## 2. Mapa de Integración (Estado Real)

La aplicación tiene una discrepancia entre la robustez del Backend (completamente funcional) y la integración del Frontend (módulos desconectados).

| Módulo | Backend (API) | Frontend (UI) | Estado de Conexión | Notas |
|--------|---------------|---------------|--------------------|-------|
| **Auth** | ✅ Listo | ✅ Listo | 🟢 **Conectado** | Login JWT, Roles y Protección de rutas 100% funcionales. |
| **Pacientes** | ✅ Listo | ✅ Listo | 🟢 **Conectado** | Tabla, creación y búsqueda consumen API real `/api/historia-clinica`. |
| **Inventario** | ✅ Listo | ✅ Listo | 🟢 **Conectado** | API `/api/inventario` 100% integrada. Muestra stock real. |
| **Citas** | ✅ Listo | ✅ Listo | 🔴 **Desconectado** | UI es "Fake/Mock". Usa datos estáticos en `src/app/(app)/appointments/page.tsx`. Endpoint `/api/citas` funcional pero no se consume. |
| **Facturación** | ✅ Listo | ✅ Listo | 🔴 **Desconectado** | UI simulada. Lógica SRI en backend existe pero no se invoca desde UI. |
| **Dashboard** | N/A | ✅ Listo | 🟡 **Parcial** | Gráficos visuales pero datos estáticos. |

> **Tarea Crítica Inmediata:** Conectar los módulos de Citas y Facturación a los endpoints existentes del Backend.

---

## 3. Infraestructura Técnica (Backend)

La infraestructura backend está en un estado muy avanzado (Sprint 6 completado).

### ✅ Implementado y Operativo:
1.  **Microservicios WSGI/ASGI**: Flask + Gunicorn (configurado para producción) + Uvicorn workers.
2.  **Base de Datos**: PostgreSQL 16.x con índices optimizados y extensión `pg_trgm`.
3.  **Seguridad**: 
    *   JWT con validación estricta (iss, aud, exp).
    *   Cabeceras de seguridad (Flask-Talisman).
    *   Rate Limiting (Flask-Limiter) con almacenamiento en memoria/redis.
4.  **Rendimiento**:
    *   Caching capa 2 (Flask-Caching con Redis).
    *   Compresión Gzip/Brotli (Flask-Compress).
5.  **Observabilidad**:
    *   Métricas Prometheus (`/metrics`) en todos los servicios.
    *   Logging estructurado JSON.
6.  **Calidad de Código (CI/CD)**:
    *   Pipeline GitHub Actions configurado.
    *   Linting estricto (Ruff, MyPy).
    *   Escaneo de seguridad (Bandit, OWASP ZAP baseline).

### ⚙️ Stack Backend:
- **Lenguaje:** Python 3.12+
- **Framework:** Flask 3.1.0
- **Dependencias Clave:** `flask-restx`, `sqlalchemy`, `alembic`, `pydantic`.

---

## 4. Estructura de Proyecto

```
Sistema Médico/
├── backend/                  # Monorepo de microservicios
│   ├── auth_service/         # Puerto 5001
│   ├── inventario_service/   # Puerto 5002
│   ├── historia_clinica_service/ # Puerto 5003
│   ├── facturacion_service/  # Puerto 5004
│   ├── citas_service/        # Puerto 5005
│   ├── logs_service/         # Puerto 5006
│   ├── common/               # Librerías compartidas (Metrics, Auth, Cache)
│   ├── scripts/              # Setup, Seeds, Herramientas
│   └── docs/                 # Documentación técnica
├── Frontend/                 # Next.js 15 (App Router)
│   ├── src/app/(app)/        # Rutas protegidas (Dashboard)
│   ├── src/app/(auth)/       # Rutas públicas (Login)
│   └── src/lib/              # Utilidades cliente
└── .github/workflows/        # CI/CD Pipelines
```

---

## 5. Guía para Desarrolladores / Agentes

### Si vas a trabajar en **Citas** o **Facturación**:
1.  **NO crees nuevos componentes UI.** Ya existen y son visualmente correctos (`appointments/page.tsx`).
2.  **TU OBJETIVO:** Reemplazar los arrays estáticos (`const appointments = [...]`) por llamadas a `fetch` o `useSWR` que apunten a los endpoints ya existentes (`/api/citas/appointments`).
3.  **VERIFICACIÓN:** Asegúrate de que los modelos de datos del backend (`datetime` strings) coincidan con lo que espera el frontend.

### Si vas a trabajar en **Backend**:
1.  El código debe cumplir con `ruff` y `mypy` (ver `.pre-commit-config.yaml`).
2.  Cualquier nuevo endpoint debe usar los decoradores standard:
    *   `@token_required` (Auth)
    *   `@cached_response` (Si aplica)
    *   `@limiter.limit` (Si es público/costoso)
3.  Actualiza los tests en `tests/` si cambias lógica de negocio.

---

## 6. Comandos Operativos

**Backend:**
```bash
cd backend
run_all.bat   # Windows
# o
./run_all.sh  # Linux/Mac
```

**Frontend:**
```bash
cd Frontend
npm run dev
```

**Validación (Tests & Lint):**
```bash
# Backend
cd backend
pytest
ruff check .

# Frontend
cd Frontend
npm run lint
npm run typecheck
```

---

**Última actualización:** 17 Dic 2025 - Reflejo exacto del estado post-sprint 6.
