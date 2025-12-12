# 📊 Análisis Integral del Estado del Proyecto

**Fecha:** 12 de Diciembre, 2025
**Versión:** 1.0
**Contexto:** Transición a Monorepo y Alineación Backend-Frontend.

---

## 1. 🚨 Hallazgo Crítico: Infraestructura Backend
Antes de abordar la funcionalidad, se detectó una **anomalía estructural grave** en el backend que debe ser corregida inmediatamente para evitar trabajar sobre código "fantasma".

*   **Situación Actual:** Existe una duplicación anidada.
    *   Ruta A: `Backend/auth_service` (Nivel raíz backend)
    *   Ruta B: `Backend/backend/auth_service` (Nivel anidado)
*   **Diagnóstico:** La carpeta `Backend/backend` contiene la estructura completa y correcta (incluyendo servicios faltantes en la raíz como `logs_service` y `scripts`).
*   **Acción Recomendada:** "Aplanar" la estructura moviendo verificado el contenido de `Backend/backend/*` a `Backend/` y eliminando la carpeta anidada.

---

## 2. 🎨 Análisis de "Modelos Frontend" (Requerimientos)
Basado en la maqueta visual proporcionada, el sistema comercial completo requiere:

1.  **Dashboard Ejecutivo**: KPIs financieros, citas del día, ocupación.
2.  **Agenda / Citas**: Calendario interactivo, estados de cita, notificaciones (Email/WhatsApp).
3.  **Gestión de Pacientes**: Historia clínica detallada, antecedentes.
4.  **Facturación SRI**:
    *   Generación de XML/PDF.
    *   Listado de movimientos (Ingresos/Egresos).
5.  **Inventario & Tratamientos**:
    *   Kardex de productos.
    *   Definición de costos de tratamientos.
    *   Recetas automáticas (baja de inventario al recetar).

---

## 3. 🧩 Estado Actual del Frontend (Next.js Template)
La plantilla instalada es un excelente punto de partida ("esqueleto"), pero está **al 20%** respecto a los modelos.

| Módulo | Estado | Brecha (Gap) |
| :--- | :--- | :--- |
| **Auth** | 🟡 Básico | Falta integración real con JWT del backend y manejo de roles. |
| **Dashboard** | 🟡 Maqueta | UI genérica. Falta conectar con endpoints de estadísticas reales. |
| **Pacientes** | 🟡 Maqueta | Falta detalle de Historia Clínica, Antecedentes y Evoluciones. |
| **Citas** | 🟡 Maqueta | Falta calendario complejo, lógica de horarios y notificaciones. |
| **Facturación** | 🔴 Incompleto | Solo UI básica. Falta toda la lógica fiscal (SRI) y PDF. |
| **Inventario** | 🔴 Inexistente | No hay vistas creadas. Se debe implementar desde cero. |
| **Configuración**| 🔴 Inexistente | Faltan catálogos (CIE-10, Roles, Usuarios). |

---

## 4. ⚙️ Estado Actual del Backend (Microservicios)
El backend es robusto y cubre el **90%** de la lógica de negocio requerida, pero necesita exposición y orquestación.

| Servicio | Estado | Acciones de Integración |
| :--- | :--- | :--- |
| **Auth Service** | 🟢 Listo | Integrar Login/Register en Frontend. |
| **Citas Service** | 🟢 Listo | Crear endpoints para "Disponibilidad de Horarios" si no existen. |
| **Hist. Clínica**| 🟢 Listo | Conectar formularios de antecedentes. |
| **Facturación** | 🟢 Listo | Es el más complejo. El front debe enviar datos para firmar XML. |
| **Inventario** | 🟢 Listo | Crítico: Crear UI para gestionar productos y recetas. |
| **Logs** | 🟢 Listo | Transparente al usuario, útil para debug. |
| **Notificaciones**| ❓ Dudoso | No se ve un servicio de Email/WhatsApp claro. ¿Está en `common`? |

---

## 5. 🗺️ Hoja de Ruta (Roadmap) Sugerida

### Fase 1: Limpieza y Conexión (✅ COMPLETADO)
1.  **Backend Fix**: ✅ Corregir la estructura de carpetas duplicada.
2.  **Cliente HTTP**: Configurar `axios` o `fetch` en Next.js con interceptores para JWT.
3.  **Auth**: Lograr que el Login del frontend obtenga token del `auth_service`.

### Fase 2: Módulos Core (Día 2-3)
1.  **Pacientes**: Conectar listado y creación.
2.  **Inventario**: Crear vistas de productos (requisito para facturación y recetas).

### Fase 3: Procesos Críticos (Día 4-5)
1.  **Citas**: Implementar calendario visual.
2.  **Historia Clínica**: Formulario complejo de antecedentes.

### Fase 4: Facturación y Polishing (Día 6+)
1.  **Facturación**: UI para emitir facturas SRI.
2.  **Dashboard**: Conectar gráficos reales.

## 6. Recomendación Técnica
Dado que el Backend está en Python y el Frontend en Next.js, recomiendo fuertemente usar **TanStack Query (React Query)** en el frontend. Esto simplificará masivamente la gestión del estado del servidor (cache, loading, error) al consumir los microservicios.
