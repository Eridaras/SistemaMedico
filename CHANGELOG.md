# Changelog

Todos los cambios notables del proyecto Sistema Médico - Clínica Bienestar.

## [1.1.0] - 2025-12-12

### ✨ Añadido

#### Frontend
- **Login Page Premium**: Diseño split-screen con panel de branding y formulario mejorado
- **Dashboard**: KPIs animados, gráfico de Ingresos vs Egresos, lista de citas del día
- **Historia Clínica**: Tabla de pacientes con búsqueda, avatares y acciones
- **Agendamiento**: Calendario mensual interactivo con panel lateral de detalles
- **Inventario**: Gestión de productos con filtros por categoría y badges de estado
- **Facturación**: 
  - Listado de movimientos con estadísticas
  - Generador de nueva factura con cálculo automático de impuestos
- **Animaciones**: Transiciones suaves entre páginas con framer-motion
- **Loading Screen**: Skeleton premium que imita el layout del Dashboard
- **Page Transition Component**: Componente reutilizable para animaciones

#### Autenticación
- **Sistema de Login**: Integración con JWT del backend
- **Middleware Next.js**: Protección de rutas automática
- **Cookies de Sesión**: Manejo seguro de tokens

#### Documentación
- **PLAN_IMPLEMENTACION.md**: Flujo completo para facturación electrónica SRI Ecuador
- **ESTRATEGIA_PRUEBAS.md**: Estrategia de testing para backend y frontend

### 🔧 Modificado
- **next.config.ts**: API rewrites para proxy a 6 microservicios backend
- **globals.css**: Paleta de colores actualizada (#197fe6 primary)
- **layout.tsx**: Fuente Inter, metadata actualizada

### 🐛 Corregido
- Redirección después del login (window.location.href en lugar de router.push)
- Manejo de estructura de respuesta del backend (data.data.token)

---

## [1.0.0] - 2025-12-01

### ✨ Añadido
- Backend completo con 5 microservicios (Auth, Inventario, Citas, Historia Clínica, Facturación)
- Facturación Electrónica SRI Ecuador (estructura base)
- Base de datos PostgreSQL con schema completo
- Frontend Next.js inicial

---

## Próximas Versiones

### [1.2.0] - Planificado
- [ ] Integración completa con SRI Ecuador (ambiente pruebas)
- [ ] Datos de prueba reales
- [ ] RIDE (PDF de facturas)
- [ ] Notificaciones WhatsApp/Email

### [1.3.0] - Planificado
- [ ] Conexión Frontend-Backend completa
- [ ] CRUD funcional en todas las páginas
- [ ] Reportes y estadísticas
