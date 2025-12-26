# Guía de Integración Frontend-Backend

**Fecha:** 2025-12-24
**Estado:** Sistema al 90% - Tareas pendientes documentadas

---

## 📊 ESTADO ACTUAL DE INTEGRACIÓN

### ✅ COMPLETAMENTE CONECTADO (100%)

- **Autenticación** - Login, registro, validación JWT con RS256
- **Gestión de Pacientes** - CRUD completo, historia médica, búsqueda
- **Inventario** - Listado de productos con búsqueda

### 🟢 PARCIALMENTE CONECTADO (80%+)

- **Citas** - Calendario funcional, **nuevo endpoint `/appointments/today` agregado**
- **Facturación** - Listado funcional, **nuevos endpoints `/dashboard/stats` y `/dashboard/monthly` agregados**
- **Dashboard** - KPIs ahora funcionarán con nuevos endpoints

### 🔴 REQUIERE IMPLEMENTACIÓN

Las siguientes funcionalidades del frontend necesitan ser conectadas:

---

## 🔧 TAREAS PENDIENTES DE INTEGRACIÓN

### 1. BILLING - Página Nueva Factura (`Frontend/src/app/(app)/billing/new/page.tsx`)

**Estado Actual:** ❌ 100% datos mock, sin conexión a backend

**Líneas a modificar:** 25-29, 150-180

**Código Actual:**
```tsx
// Línea 25-29 - ELIMINAR
const initialItems = [
  { id: 1, name: "Consulta General...", quantity: 1, price: 150000, discount: 10 },
  { id: 2, name: "Kit de Bioseguridad", quantity: 1, price: 25000, discount: 0 },
];
```

**Implementación Requerida:**
```tsx
// 1. Agregar búsqueda de pacientes
const handleSearchPatient = async (docNumber: string) => {
  const res = await fetch(`/api/historia-clinica/patients/search?doc_number=${docNumber}`);
  const data = await res.json();
  setSelectedPatient(data.data);
};

// 2. Búsqueda de productos/servicios
const handleSearchProducts = async (query: string) => {
  const res = await fetch(`/api/inventario/products?search=${query}`);
  const data = await res.json();
  setAvailableProducts(data.data.products);
};

// 3. Crear factura
const handleCreateInvoice = async () => {
  const payload = {
    patient_id: selectedPatient.patient_id,
    subtotal: calculateSubtotal(),
    iva_percentage: 15.0,
    iva: calculateIVA(),
    total: calculateTotal(),
    payment_method: paymentMethod,
    status: isDraft ? 'pending' : 'paid',
    items: items.map(item => ({
      product_id: item.id,
      quantity: item.quantity,
      unit_price: item.price,
      discount_percentage: item.discount
    }))
  };

  const res = await fetch('/api/facturacion/invoices', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    router.push('/billing');
  }
};
```

**Endpoints Backend Disponibles:**
- ✅ `GET /api/historia-clinica/patients/search?doc_number=`
- ✅ `GET /api/inventario/products?search=`
- ✅ `POST /api/facturacion/invoices`

---

### 2. APPOINTMENTS - Sidebar de Detalles (`Frontend/src/app/(app)/appointments/page.tsx`)

**Estado Actual:** ❌ Datos hardcodeados (Juan Pérez, etc.)

**Líneas a modificar:** 295-330

**Código Actual:**
```tsx
// Línea 295-330 - REEMPLAZAR
<p>Jueves, 7 de Diciembre, 2023 - 9:00 AM</p>
<h3>Juan Pérez</h3>
<p>+57 300 123 4567</p>
```

**Implementación Requerida:**
```tsx
const [selectedAppointment, setSelectedAppointment] = useState(null);

const handleSelectAppointment = async (appointmentId: number) => {
  const res = await fetch(`/api/citas/appointments/${appointmentId}`);
  const data = await res.json();
  setSelectedAppointment(data.data);
};

// En el JSX del sidebar
{selectedAppointment && (
  <>
    <h3>{selectedAppointment.patient_name}</h3>
    <p>{selectedAppointment.patient_phone}</p>
    <p>{formatDate(selectedAppointment.appointment_date)}</p>
    <p>{selectedAppointment.reason}</p>
  </>
)}
```

**Endpoints Backend Disponibles:**
- ✅ `GET /api/citas/appointments/:id` - Detalles completos de la cita

---

### 3. APPOINTMENTS - Formulario Nueva Cita

**Estado Actual:** ❌ Botón "Nueva Cita" sin funcionalidad

**Implementación Requerida:**
```tsx
const [isModalOpen, setIsModalOpen] = useState(false);

const handleCreateAppointment = async (formData) => {
  const payload = {
    patient_id: formData.patient_id,
    doctor_id: formData.doctor_id,
    appointment_date: formData.date,
    reason: formData.reason,
    notes: formData.notes
  };

  const res = await fetch('/api/citas/appointments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  if (res.ok) {
    fetchAppointments(); // Recargar calendario
    setIsModalOpen(false);
  }
};

// Verificar disponibilidad antes de crear
const checkAvailability = async (doctorId, date) => {
  const res = await fetch('/api/citas/appointments/check-availability', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ doctor_id: doctorId, appointment_date: date })
  });
  return res.json();
};
```

**Endpoints Backend Disponibles:**
- ✅ `POST /api/citas/appointments`
- ✅ `POST /api/citas/appointments/check-availability`

---

### 4. INVENTORY - Botones de Acción

**Estado Actual:** ❌ Botones "Editar" y "Eliminar" sin funcionalidad

**Líneas a modificar:** Tabla de productos

**Implementación Requerida:**
```tsx
// Editar producto
const handleEditProduct = async (productId: number, updatedData) => {
  const res = await fetch(`/api/inventario/products/${productId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updatedData)
  });

  if (res.ok) {
    fetchProducts();
  }
};

// Actualizar stock
const handleUpdateStock = async (productId: number, newStock: number) => {
  const res = await fetch(`/api/inventario/products/${productId}/stock`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ current_stock: newStock })
  });

  if (res.ok) {
    fetchProducts();
  }
};
```

**Endpoints Backend Disponibles:**
- ✅ `PUT /api/inventario/products/:id`
- ✅ `PATCH /api/inventario/products/:id/stock`

---

### 5. INVENTORY - Categorías Dinámicas

**Estado Actual:** ❌ Categorías hardcodeadas

**Línea:** 114

**Código Actual:**
```tsx
const categories = ['Todo', 'Medicamentos', 'Insumos', 'Equipos'];
```

**Implementación Requerida:**
```tsx
const [categories, setCategories] = useState(['Todo']);

useEffect(() => {
  fetch('/api/inventario/treatments/categories')
    .then(res => res.json())
    .then(data => {
      setCategories(['Todo', ...data.data.categories]);
    });
}, []);
```

**Endpoints Backend Disponibles:**
- ✅ `GET /api/inventario/treatments/categories`

---

### 6. PATIENTS - Botones de Acción

**Estado Actual:** ❌ Botones sin funcionalidad

**Implementación Requerida:**

```tsx
// Botón "Agendar Cita"
const handleScheduleAppointment = (patientId: number) => {
  router.push(`/appointments?patient_id=${patientId}`);
};

// Botón "Ver Historia"
const handleViewHistory = (patientId: number) => {
  router.push(`/patients/${patientId}`);
};

// Botón "Editar"
const handleEditPatient = (patientId: number) => {
  router.push(`/patients/${patientId}/edit`);
};
```

**Endpoints Backend Disponibles:**
- ✅ `PUT /api/historia-clinica/patients/:id`

---

### 7. BILLING - Botón "Ver Detalle"

**Estado Actual:** ❌ Sin funcionalidad

**Implementación Requerida:**
```tsx
const handleViewInvoiceDetail = (invoiceId: number) => {
  router.push(`/billing/${invoiceId}`);
};
```

Luego crear página: `Frontend/src/app/(app)/billing/[id]/page.tsx`

```tsx
const InvoiceDetailPage = ({ params }) => {
  const [invoice, setInvoice] = useState(null);

  useEffect(() => {
    fetch(`/api/facturacion/invoices/${params.id}`)
      .then(res => res.json())
      .then(data => setInvoice(data.data));
  }, [params.id]);

  return <InvoiceDetails invoice={invoice} />;
};
```

**Endpoints Backend Disponibles:**
- ✅ `GET /api/facturacion/invoices/:id`

---

## 🔄 CONFIGURACIÓN PARA DOCKER (Traefik)

Cuando ejecutes el sistema con Docker Compose en puerto :3333, actualiza:

**Archivo:** `Frontend/next.config.ts`

**Cambiar:**
```typescript
// DESARROLLO (servicios individuales)
destination: 'http://localhost:5001/api/auth/:path*',

// PRODUCCIÓN (Traefik)
destination: 'http://localhost:3333/api/auth/:path*',
```

O mejor, usar variable de entorno:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3333';

async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: `${API_BASE_URL}/api/:path*`,
    },
  ];
}
```

**.env.local:**
```
# Desarrollo (servicios separados)
NEXT_PUBLIC_API_URL=http://localhost:5001

# Docker con Traefik
NEXT_PUBLIC_API_URL=http://localhost:3333
```

---

## 📋 RESUMEN DE ENDPOINTS BACKEND LISTOS PERO NO USADOS

### Tratamientos (Inventario)
```
GET  /api/inventario/treatments
POST /api/inventario/treatments
GET  /api/inventario/treatments/:id/recipe
POST /api/inventario/treatments/:id/recipe
GET  /api/inventario/treatments/:id/check-stock
```

### Citas - Tratamientos y Extras
```
GET    /api/citas/appointments/:id/treatments
POST   /api/citas/appointments/:id/treatments
PUT    /api/citas/appointments/treatments/:id
DELETE /api/citas/appointments/treatments/:id
GET    /api/citas/appointments/:id/extras
POST   /api/citas/appointments/:id/extras
```

### Gastos Operacionales
```
GET    /api/facturacion/expenses
POST   /api/facturacion/expenses
PUT    /api/facturacion/expenses/:id
DELETE /api/facturacion/expenses/:id
GET    /api/facturacion/expenses/categories
GET    /api/facturacion/expenses/totals
```

---

## ✅ ENDPOINTS AGREGADOS HOY (2025-12-24)

### Citas Service
```
GET /api/citas/appointments/today
```
- Retorna citas del día actual
- Usado por el dashboard

### Facturación Service
```
GET /api/facturacion/dashboard/stats
GET /api/facturacion/dashboard/monthly
```
- Stats: KPIs financieros (ingresos, egresos, balance)
- Monthly: Datos mensuales para gráficos

---

## 🎯 PRIORIDADES DE IMPLEMENTACIÓN

### Alta Prioridad (Funcionalidad Básica)
1. ✅ Dashboard - Endpoints agregados (HECHO)
2. Billing/new - Conectar formulario completo
3. Appointments - Conectar sidebar de detalles

### Media Prioridad (Mejoras UX)
4. Appointments - Formulario nueva cita con modal
5. Inventory - Botones editar/eliminar con modals
6. Patients - Conectar botones de acción

### Baja Prioridad (Extras)
7. Categorías dinámicas de inventario
8. Página de detalle de factura
9. Filtros avanzados en todas las páginas

---

## 📝 NOTAS FINALES

- El backend está **MÁS completo** que el frontend
- Muchos endpoints útiles están disponibles pero no se usan
- La mayoría de funcionalidades requieren solo conectar el frontend
- No hay endpoints faltantes críticos (todos los necesarios existen)
- Sistema funcional al **90%** - Solo falta integración de UI

**Última Actualización:** 2025-12-24 18:30
