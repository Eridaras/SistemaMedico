# 📋 Plan de Implementación - Sistema Médico Clínica Bienestar

## Versión: 1.0.0
## Última Actualización: 2025-12-12

---

## 🎯 Resumen Ejecutivo

Este documento detalla el flujo completo de tareas necesarias para poblar el sistema con datos de prueba reales y habilitar la facturación electrónica con el SRI de Ecuador en ambiente de pruebas.

---

## 📊 Estado Actual del Sistema

### ✅ Componentes Completados

| Módulo | Estado | Descripción |
|--------|--------|-------------|
| **Autenticación** | ✅ Funcional | Login/Logout con JWT |
| **Dashboard** | ✅ Funcional | KPIs, gráficos, citas del día |
| **Historia Clínica** | ✅ UI Lista | Listado de pacientes |
| **Agendamiento** | ✅ UI Lista | Calendario mensual |
| **Inventario** | ✅ UI Lista | Gestión de productos |
| **Facturación** | ✅ UI Lista | Listado y generación |
| **Backend APIs** | ✅ Funcional | 5 microservicios corriendo |
| **Base de Datos** | ✅ Funcional | PostgreSQL configurado |

### 🔄 Pendientes de Implementación

| Módulo | Estado | Prioridad |
|--------|--------|-----------|
| Datos de prueba reales | ⏳ Pendiente | Alta |
| Facturación Electrónica SRI | ⏳ Pendiente | Alta |
| Certificado P12 de prueba | ⏳ Pendiente | Alta |
| Integración Frontend-Backend completa | ⏳ Pendiente | Media |
| RIDE (PDF de facturas) | ⏳ Pendiente | Media |

---

## 🚀 FASE 1: Datos de Prueba (Semana 1)

### 1.1 Configuración de Roles y Usuarios

```sql
-- Roles a crear
- Administrador (acceso completo)
- Médico (consultas, historia clínica)
- Recepcionista (citas, pacientes, facturación)
- Auxiliar (inventario)
```

**Tareas:**
- [ ] Crear script SQL con datos de roles
- [ ] Crear usuarios de prueba para cada rol
- [ ] Validar permisos por rol

### 1.2 Pacientes de Prueba

**Datos requeridos por paciente:**
- Nombre completo
- Cédula/RUC (válidos con dígito verificador)
- Fecha de nacimiento
- Género
- Teléfono
- Email
- Dirección
- Tipo de sangre
- Alergias (opcional)

**Cantidad:** 20 pacientes de prueba

### 1.3 Productos/Servicios de Inventario

**Categorías:**
- Medicamentos
- Suministros médicos
- Equipos
- Servicios de consulta
- Procedimientos

**Por producto:**
- Código
- Nombre
- Descripción
- Precio unitario
- Stock
- Código IVA (0% o 15%)

**Cantidad:** 30 productos/servicios

### 1.4 Citas de Prueba

**Incluir:**
- Citas pasadas (para historial)
- Citas futuras (para agenda)
- Diferentes estados: Programada, Confirmada, Atendida, Cancelada

**Cantidad:** 50 citas

---

## 🧾 FASE 2: Facturación Electrónica SRI (Semana 2-3)

### 2.1 Requisitos para Ambiente de Pruebas SRI

| Requisito | Estado | Descripción |
|-----------|--------|-------------|
| RUC de Pruebas | ⏳ | RUC autorizado en ambiente PRUEBAS |
| Certificado P12 | ⏳ | Certificado digital de firma |
| Clave Acceso SRI | ⏳ | Credenciales portal SRI |

### 2.2 Configuración del Emisor (SRI)

**Datos requeridos:**
```yaml
ruc_emisor: "XXXXXXXXXXXX"  # 13 dígitos
razon_social: "CLINICA BIENESTAR S.A."
nombre_comercial: "Clínica Bienestar"
direccion_matriz: "Quito, Pichincha, Ecuador"
codigo_establecimiento: "001"
punto_emision: "001"
ambiente: "1"  # 1=Pruebas, 2=Producción
tipo_emision: "1"  # 1=Normal
contribuyente_especial: "000"  # Si aplica
obligado_contabilidad: "SI" | "NO"
```

### 2.3 Flujo de Facturación Electrónica

```
┌─────────────────┐
│ 1. Crear Factura │
│    (Frontend)    │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 2. Generar XML  │
│ (SRI Compliant) │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 3. Firmar XML   │
│  (Certificado)  │
└────────┬────────┘
         ▼
┌─────────────────────────────┐
│ 4. Enviar a SRI (SOAP)      │
│ RecepcionComprobantesOffline │
└────────┬────────────────────┘
         ▼
┌─────────────────────────────┐
│ 5. Consultar Autorización   │
│ AutorizacionComprobantesOff │
└────────┬────────────────────┘
         ▼
┌─────────────────┐
│ 6. Generar RIDE │
│     (PDF)       │
└────────┬────────┘
         ▼
┌─────────────────┐
│ 7. Almacenar/   │
│    Enviar Email │
└─────────────────┘
```

### 2.4 Endpoints SRI (Ambiente Pruebas)

| Servicio | URL |
|----------|-----|
| Recepción | `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl` |
| Autorización | `https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl` |

### 2.5 Tareas de Implementación SRI

- [ ] **2.5.1** Obtener RUC de pruebas autorizado por SRI
- [ ] **2.5.2** Obtener certificado P12 de pruebas
- [ ] **2.5.3** Configurar tabla `sri_configuration` con datos del emisor
- [ ] **2.5.4** Probar generación de XML
- [ ] **2.5.5** Probar firma digital XML
- [ ] **2.5.6** Probar envío a SRI (SOAP)
- [ ] **2.5.7** Probar consulta de autorización
- [ ] **2.5.8** Implementar generación de RIDE (PDF)
- [ ] **2.5.9** Integrar con frontend de facturación

---

## 🔗 FASE 3: Integración Frontend-Backend (Semana 3-4)

### 3.1 Conexión de Páginas con APIs

| Página | API Backend | Estado |
|--------|-------------|--------|
| Dashboard | `/api/stats`, `/api/citas/today` | ⏳ |
| Pacientes | `/api/historia-clinica/pacientes` | ⏳ |
| Citas | `/api/citas` | ⏳ |
| Inventario | `/api/inventario/productos` | ⏳ |
| Facturación | `/api/facturacion/invoices` | ⏳ |

### 3.2 Tareas por Módulo

#### Dashboard
- [ ] Conectar KPIs con datos reales
- [ ] Mostrar citas del día desde API
- [ ] Gráfico con datos históricos

#### Pacientes
- [ ] CRUD completo de pacientes
- [ ] Búsqueda funcional
- [ ] Página de detalle de paciente
- [ ] Historia clínica por paciente

#### Citas
- [ ] Crear nueva cita (modal/página)
- [ ] Editar cita existente
- [ ] Cancelar cita
- [ ] Confirmar cita
- [ ] Notificaciones (WhatsApp/Email)

#### Inventario
- [ ] CRUD de productos
- [ ] Control de stock
- [ ] Alertas de stock bajo

#### Facturación
- [ ] Listar facturas reales
- [ ] Crear nueva factura
- [ ] Integrar con SRI
- [ ] Descargar RIDE (PDF)
- [ ] Anular facturas

---

## 📝 FASE 4: Testing y Validación (Semana 4)

### 4.1 Pruebas Backend
- [ ] Unit tests para cada servicio
- [ ] Pruebas de integración SRI
- [ ] Validación de XML generados

### 4.2 Pruebas Frontend
- [ ] Navegación completa
- [ ] Formularios funcionales
- [ ] Responsive design
- [ ] Manejo de errores

### 4.3 Pruebas End-to-End
- [ ] Flujo completo de facturación
- [ ] Flujo de atención de paciente
- [ ] Flujo de agendamiento

---

## 📦 Commits y Control de Versiones

### Estructura de Commits

```
feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato/estilos
refactor: refactorización
test: pruebas
chore: mantenimiento
```

### Branches

- `main` - Producción estable
- `develop` - Desarrollo activo
- `feature/sri-integration` - Facturación electrónica
- `feature/real-data` - Datos de prueba

---

## 🗓️ Cronograma Estimado

| Semana | Fase | Entregables |
|--------|------|-------------|
| 1 | Datos de Prueba | Scripts SQL, datos poblados |
| 2 | SRI Config | Certificados, configuración emisor |
| 3 | SRI Integration | XML, firma, envío funcional |
| 4 | Frontend Integration | Todas las páginas conectadas |
| 5 | Testing & Deploy | Sistema probado y documentado |

---

## 📞 Contactos y Recursos

### SRI Ecuador
- Portal: https://www.sri.gob.ec
- Ambiente Pruebas: https://celcer.sri.gob.ec
- Ficha Técnica: v2.23 (XML v2.1.0)

### Documentación del Proyecto
- `/docs/ONBOARDING.md` - Guía inicial
- `/docs/ESTRATEGIA_PRUEBAS.md` - Estrategia de testing
- `/docs/PLAN_IMPLEMENTACION.md` - Este documento
- `/backend/README.md` - Documentación backend

---

## 📌 Próximos Pasos Inmediatos

1. **[ ] Obtener credenciales SRI pruebas**
   - Contactar con contador o representante legal
   - Solicitar RUC habilitado para pruebas

2. **[ ] Obtener certificado P12**
   - Certificado de firma electrónica
   - Puede ser de pruebas o uno real

3. **[ ] Ejecutar script de datos de prueba**
   - Crear scripts SQL
   - Poblar base de datos

4. **[ ] Actualizar GitHub**
   - Commit cambios actuales
   - Documentar progreso

---

*Documento creado: 2025-12-12*
*Última actualización: 2025-12-12*
