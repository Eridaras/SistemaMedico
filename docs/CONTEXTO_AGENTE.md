# 🧠 CONTEXTO MAESTRO PARA AGENTES Y DESARROLLADORES

> **IMPORTANTE PARA AGENTES DE IA:** Lee este documento ANTES de realizar cualquier tarea. Este es el estado de la verdad del proyecto. Si realizas cambios estructurales importantes, **ACTUALIZA ESTE DOCUMENTO**.

## 1. Identidad del Proyecto
**Nombre:** Sistema Médico - Clínica Bienestar
**Objetivo:** Sistema integral de gestión hospitalaria (HIS) con facturación electrónica nativa para Ecuador (SRI).
**Estado Actual:** MVP Funcional (Frontend Premium + Backend Microservicios).

---

## 2. Stack Tecnológico

### 🎨 Frontend (Carpeta `/Frontend`)
- **Framework:** Next.js 15 (App Router)
- **Lenguaje:** TypeScript
- **Estilos:** Tailwind CSS + Shadcn/UI
- **Iconos:** Lucide React
- **Estado/Auth:** Cookies + JWT (Custom implementation in `src/lib/auth.ts`)
- **Animaciones:** Framer Motion (`page-transition.tsx`)
- **Visualización:** Recharts

### ⚙️ Backend (Carpeta `/backend`)
- **Lenguaje:** Python 3.9+
- **Framework:** Flask (Microservicios)
- **Base de Datos:** PostgreSQL
- **Facturación:** XML v2.1.0 (XADES-BES) compatible con SRI
- **Comunicación SRI:** SOAP (Zeep)

---

## 3. Arquitectura de Microservicios

El sistema opera con una arquitectura de microservicios. Cada servicio corre en su propio proceso/puerto.

| Servicio | Puerto | Directorio | Descripción |
|----------|--------|------------|-------------|
| **Auth** | `5001` | `/backend/auth_service` | Login, JWT, Roles, Usuarios (PostgreSQL: `users`, `roles`) |
| **Inventario** | `5002` | `/backend/inventario_service` | Productos, Stock, Categorías (PostgreSQL: `products`) |
| **Historia** | `5003` | `/backend/historia_clinica_service` | Pacientes, Consultas, Historial (PostgreSQL: `patients`) |
| **Facturación** | `5004` | `/backend/facturacion_service` | Facturas, SRI, XML, Firmas (PostgreSQL: `invoices`) |
| **Citas** | `5005` | `/backend/citas_service` | Agendamiento, Calendario (PostgreSQL: `appointments`) |
| **Frontend** | `9002` | `/Frontend` | Interfaz de Usuario (Next.js Proxy -> Backend) |

> **Nota sobre Proxy:** El Frontend usa `next.config.ts` (`async rewrites`) para redirigir peticiones desde `/api/*` hacia los puertos específicos del backend. **El frontend NO hace peticiones directas a localhost:5001, usa /api/auth/...**

---

## 4. Estructura de Base de Datos (PostgreSQL)

El esquema es relacional. Tablas principales creadas:
- `users`: Usuarios del sistema (con `role_id`).
- `roles`: RBAC (Admin, Médico, etc).
- `patients`: Datos demográficos.
- `appointments`: Citas médicas.
- `products`: Inventario.
- `invoices`: Cabecera de facturas.
- `invoice_items`: Detalle de facturas.
- `sri_configuration`: Credenciales de firma electrónica.

---

## 5. Estado Actual del Desarrollo (Snapshot)

### ✅ Funcionalidades Activas
1.  **Login Premium:** Autenticación JWT completa contra `auth_service`. UI con diseño split-screen y animaciones.
2.  **Dashboard:** KPIs visuales, Gráficos (mock data visual, estructura real lista), Lista de citas.
3.  **Navegación:** Sidebar responsive, transiciones suaves entre páginas.
4.  **Módulos UI:**
    *   Pacientes (Tabla, Búsqueda).
    *   Agendamiento (Calendario Interactivo).
    *   Facturación (Lista, Generador de facturas con cálculos IVA).
    *   Inventario (Buscador, Filtros).

### 🚧 En Progreso / Pendiente
1.  **Conexión Real de Datos:** Las tablas de UI (Pacientes, Citas) muestran datos simulados (`const data = [...]`) en el Frontend. Falta conectar `fetch` a los endpoints del Backend ya existentes.
2.  **Facturación SRI:** El backend tiene la lógica de generación XML, pero falta probar el flujo completo de firma y envío SOAP con credenciales de prueba.
3.  **Ambiente de Pruebas:** Necesitamos poblar la BD con datos masivos de prueba (ver `docs/PLAN_IMPLEMENTACION.md`).

---

## 6. Reglas para Agentes (Guidelines)

1.  **Modificaciones de UI:** Siempre mantén la estética "Premium" (sombras suaves, bordes redondeados, paleta azul `#197fe6`). Usa `PageTransition` en cada nueva página.
2.  **Nuevas Funcionalidades:**
    *   Primero define el modelo de datos en Backend.
    *   Crea el endpoint en el servicio correspondiente.
    *   Actualiza el `rewrite` en `next.config.ts` si es un nuevo servicio.
    *   Crea la UI en Frontend.
3.  **Manejo de Errores:** Nunca dejes un `catch` vacío. Muestra errores visuales al usuario (Toasts o mensajes en formulario).
4.  **Tests:** Si tocas lógica crítica (especialmente Facturación/SRI), ejecuta los tests en `backend/tests/`.

---

## 7. Comandos Operativos

**Backend (Todos los servicios):**
```bash
cd backend
.\run_all.bat
```

**Frontend:**
```bash
cd Frontend
npm run dev
```

**Generar Datos de Prueba (Próximamente):**
```bash
python backend/scripts/generate_mock_data.py
```

---

## 8. Rutas Clave del Proyecto

- **Conf. Next.js:** `Frontend/next.config.ts` (Aquí están los proxys).
- **Auth Utils:** `Frontend/src/lib/auth.ts` (Lógica de login cliente).
- **Estilos Globales:** `Frontend/src/app/globals.css`.
- **Backend Routes:** `backend/<servicio>/routes.py`.
- **Modelos DB:** `backend/<servicio>/models.py`.

---

**Última actualización:** 12 Dic 2025 - Implementación de Frontend Premium completada.
