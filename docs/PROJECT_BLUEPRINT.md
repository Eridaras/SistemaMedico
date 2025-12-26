# PROJECT BLUEPRINT - Sistema Médico Clínica Bienestar

## RESUMEN EJECUTIVO

**Nombre:** Sistema Integral de Gestión Hospitalaria
**Cliente:** Clínica Bienestar (Ecuador)
**Objetivo:** Sistema completo de gestión clínica con facturación electrónica SRI, historia clínica digital, agendamiento de citas e inventario médico.

---

## LÓGICA DE NEGOCIO

### Contexto
Clínica odontológica en Ecuador requiere:
1. **Historia Clínica Digital** - Pacientes, antecedentes, notas clínicas
2. **Agendamiento de Citas** - Calendario médico con disponibilidad
3. **Inventario Médico** - Productos, tratamientos, motor de recetas
4. **Facturación Electrónica** - Cumplimiento normativa SRI Ecuador
5. **Control Financiero** - Ingresos, egresos, reportes

### Flujo Principal
```
1. PACIENTE → Registro (cédula/RUC ecuatoriano)
2. CITA → Agendamiento con doctor, verificación disponibilidad
3. ATENCIÓN → Historia clínica, notas, tratamientos aplicados
4. FACTURACIÓN → Generación automática con IVA, firma digital SRI
5. INVENTARIO → Descuento automático de productos según receta
6. REPORTES → Dashboard financiero, KPIs, métricas
```

---

## MÓDULOS Y FUNCIONALIDAD

### 1. AUTENTICACIÓN (Auth Service)
**Puerto:** 5001
**Funciones:**
- Login/Registro con JWT
- RBAC (Roles: Admin, Doctor, Recepción)
- Gestión de usuarios y permisos
- Validación de tokens

### 2. HISTORIA CLÍNICA (Historia Clinica Service)
**Puerto:** 5003
**Funciones:**
- Registro de pacientes (validación cédula/RUC Ecuador)
- Antecedentes médicos (alergias, cirugías, patologías)
- Notas clínicas por cita
- Búsqueda avanzada de pacientes

### 3. AGENDAMIENTO (Citas Service)
**Puerto:** 5005
**Funciones:**
- Calendario de citas por doctor
- Verificación de disponibilidad
- Asignación de tratamientos a citas
- Productos extra vendidos en cita
- Estados: PENDING, CONFIRMED, COMPLETED, CANCELLED

### 4. INVENTARIO (Inventario Service)
**Puerto:** 5002
**Funciones:**
- Gestión de productos médicos (stock, precios)
- Catálogo de tratamientos odontológicos
- **Motor de Recetas:** Vincula tratamientos con productos requeridos
- Alertas de stock bajo
- Verificación de disponibilidad para tratamientos

### 5. FACTURACIÓN (Facturacion Service)
**Puerto:** 5004
**Funciones:**
- Generación de facturas (DRAFT, ISSUED, PAID, ANNULLED)
- Cálculo automático de IVA (15% Ecuador)
- Numeración secuencial (001-001-XXXXXXXXX)
- Gastos operacionales
- Dashboard financiero (ingresos, egresos, profit)
- **Facturación Electrónica SRI:**
  - Firma digital XML
  - Envío SOAP a SRI
  - Autorización electrónica
  - RIDE (PDF representación impresa)

### 6. LOGS (Logs Service)
**Puerto:** 5006
**Funciones:**
- Registro centralizado de eventos
- Niveles: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Estadísticas por servicio
- Limpieza automática (retención 90 días)

---

## REGLAS DE NEGOCIO CRÍTICAS

### Normativa Ecuador
1. **Cédula:** 10 dígitos, validación algoritmo módulo 10
2. **RUC:** 13 dígitos, validación específica
3. **IVA:** 15% aplicable automáticamente
4. **SRI:** Facturación electrónica obligatoria >$200 mensuales

### Motor de Recetas
- Cada tratamiento puede tener N productos asociados
- Al agendar tratamiento, se verifica stock disponible
- Al completar cita, se descuenta inventario automáticamente
- Costo de tratamiento = Σ (productos × cantidad_requerida × cost_price)
- Margen = base_price - costo_productos

### Control de Citas
- No permitir citas superpuestas para mismo doctor
- Validación: end_time > start_time
- Estados progresivos (PENDING → CONFIRMED → COMPLETED)
- Cancelación permitida solo antes de COMPLETED

### Facturación
- Numeración secuencial sin saltos
- IVA automático (configurable via rate)
- Solo facturas ISSUED o PAID cuentan para ingresos
- Gastos requieren aprobación de Admin

---

## USUARIOS Y ROLES

### Admin (role_id: 1)
- Acceso total al sistema
- Gestión de usuarios y roles
- Configuración de tratamientos y productos
- Reportes financieros completos

### Doctor (role_id: 2)
- Acceso a historia clínica
- Creación de notas clínicas
- Visualización de agenda
- Sin acceso a facturación

### Recepción (role_id: 3)
- Registro de pacientes
- Agendamiento de citas
- Generación de facturas
- Sin acceso a configuración

---

## INTEGRACIONES EXTERNAS

### SRI (Servicio de Rentas Internas - Ecuador)
**Protocolo:** SOAP/XML
**Certificado:** P12 con firma digital
**Ambientes:**
- Pruebas: `https://celcer.sri.gob.ec/...`
- Producción: `https://cel.sri.gob.ec/...`

**Flujo:**
1. Generar XML factura (formato XAdES-BES)
2. Firmar digitalmente con certificado
3. Enviar a SRI via SOAP
4. Recibir clave de acceso (49 dígitos)
5. Consultar autorización
6. Generar RIDE (PDF)

### Futuras (Planificadas)
- **WhatsApp Business API** - Notificaciones de citas
- **Email SMTP** - Envío de facturas PDF
- **Pasarelas de Pago** - Pagos en línea

---

## ESTADO ACTUAL

### Implementado ✅
- Backend 6 microservicios funcionales
- Frontend Next.js con páginas principales
- Base de datos PostgreSQL completa
- Autenticación JWT + RBAC
- CRUD completo en todos los servicios
- Swagger/OpenAPI documentación
- CI/CD GitHub Actions
- Caching Redis
- Rate Limiting
- Prometheus Metrics

### En Desarrollo 🚧
- Facturación Electrónica SRI (estructura creada, falta firma/envío)
- Conexión completa Frontend-Backend
- Tests unitarios (infraestructura lista)

### Pendiente 📋
- Datos de prueba realistas
- RIDE (PDF facturas)
- Notificaciones automáticas
- Reportes avanzados
- Backup automático

---

## PRÓXIMOS HITOS

### Fase 1 (2 semanas)
- [ ] Completar integración SRI ambiente pruebas
- [ ] Poblar BD con datos realistas
- [ ] Tests unitarios 80% cobertura

### Fase 2 (1 mes)
- [ ] Conectar todas las páginas frontend con API
- [ ] RIDE generación automática
- [ ] Notificaciones WhatsApp/Email

### Fase 3 (3 meses)
- [ ] Migrar a producción SRI
- [ ] Reportes avanzados y analytics
- [ ] Sistema de backups automáticos

---

**Última Actualización:** 2025-12-24
**Responsable Técnico:** Omniscient Architect Agent
**Estado:** Desarrollo Activo
