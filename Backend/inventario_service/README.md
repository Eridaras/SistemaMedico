# 📦 Inventario Service - Servicio de Inventario

Microservicio de gestión de inventario y tratamientos del Sistema Médico. Controla productos, stock, recetas de tratamientos y alertas.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Motor de Recetas](#-motor-de-recetas)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Gestión de Productos**: CRUD completo de productos/insumos médicos
- **Control de Stock**: Seguimiento de cantidad, alertas de stock bajo
- **Tratamientos**: Definición de servicios médicos ofrecidos
- **Motor de Recetas**: Vinculación automática de tratamientos con productos necesarios
- **Alertas de Inventario**: Notificación de productos bajo mínimo
- **Categorización**: Organización por categorías (Medicamentos, Insumos, Equipos)
- **Cálculo de Precios**: Precio base + IVA automático
- **SKU Único**: Código identificador por producto

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5002/api/inventario
```

### Documentación Interactiva
```
http://localhost:5002/docs
```

### Lista de Endpoints

#### Productos

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/products` | Listar todos los productos | Sí |
| `GET` | `/products/:id` | Obtener producto por ID | Sí |
| `POST` | `/products` | Crear nuevo producto | Sí |
| `PUT` | `/products/:id` | Actualizar producto | Sí |
| `DELETE` | `/products/:id` | Eliminar producto | Sí (Admin) |
| `GET` | `/products/low-stock` | Productos con stock bajo | Sí |
| `POST` | `/products/:id/adjust-stock` | Ajustar stock (entrada/salida) | Sí |

#### Tratamientos

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/treatments` | Listar todos los tratamientos | Sí |
| `GET` | `/treatments/:id` | Obtener tratamiento por ID | Sí |
| `POST` | `/treatments` | Crear nuevo tratamiento | Sí |
| `PUT` | `/treatments/:id` | Actualizar tratamiento | Sí |
| `DELETE` | `/treatments/:id` | Eliminar tratamiento | Sí (Admin) |
| `GET` | `/treatments/:id/recipe` | Obtener receta del tratamiento | Sí |
| `POST` | `/treatments/:id/recipe` | Agregar producto a receta | Sí |

---

## 📊 Modelos de Datos

### Product (Producto)

```python
{
    "product_id": 1,
    "sku": "MED-001",
    "name": "Paracetamol 500mg",
    "description": "Analgésico y antipirético",
    "category": "Medicamentos",
    "cost_price": 0.50,
    "sale_price": 1.20,
    "stock_quantity": 250,
    "min_stock_alert": 50,
    "unit": "Tabletas",
    "is_taxable": true,
    "tax_rate": 0.15,
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `product_id` | int | ID único del producto | PK, Autoincremental |
| `sku` | string | Código SKU único | Único, alfanumérico |
| `name` | string | Nombre del producto | Requerido, max 200 |
| `description` | text | Descripción detallada | Opcional |
| `category` | string | Categoría del producto | Enum predefinido |
| `cost_price` | decimal | Precio de costo | >= 0 |
| `sale_price` | decimal | Precio de venta | >= cost_price |
| `stock_quantity` | int | Cantidad en stock | >= 0 |
| `min_stock_alert` | int | Umbral de alerta | Default: 10 |
| `unit` | string | Unidad de medida | Ej: Unidades, Tabletas, ml |
| `is_taxable` | boolean | Aplica IVA | Default: true |
| `tax_rate` | decimal | Tasa de impuesto | Default: 0.15 (15%) |

### Treatment (Tratamiento)

```python
{
    "treatment_id": 1,
    "name": "Limpieza Dental",
    "description": "Limpieza profesional completa",
    "base_price": 35.00,
    "duration_minutes": 45,
    "category": "Odontología",
    "is_active": true
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `treatment_id` | int | ID único del tratamiento |
| `name` | string | Nombre del tratamiento |
| `description` | text | Descripción del procedimiento |
| `base_price` | decimal | Precio base del servicio |
| `duration_minutes` | int | Duración estimada |
| `category` | string | Categoría del tratamiento |
| `is_active` | boolean | Estado activo/inactivo |

### Treatment Recipe (Receta de Tratamiento)

```python
{
    "recipe_id": 1,
    "treatment_id": 1,
    "product_id": 5,
    "quantity_needed": 2,
    "notes": "Usar antes del procedimiento"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `recipe_id` | int | ID único de la receta |
| `treatment_id` | int | ID del tratamiento |
| `product_id` | int | ID del producto necesario |
| `quantity_needed` | int | Cantidad requerida |
| `notes` | text | Notas de uso |

---

## 🔧 Motor de Recetas

El **Motor de Recetas** es una característica única que vincula automáticamente tratamientos con los productos necesarios:

### Flujo de Trabajo

1. **Definir Tratamiento**: Crear un tratamiento (ej: "Curación de Herida")
2. **Agregar Productos a Receta**: Vincular productos necesarios:
   - 1x Gasas estériles
   - 1x Guantes descartables
   - 1x Solución antiséptica
3. **Al Realizar Tratamiento**: El sistema automáticamente:
   - Descuenta el stock de todos los productos
   - Verifica disponibilidad antes de confirmar
   - Genera alerta si algún producto está bajo mínimo

### Ejemplo de Uso

```python
# Crear receta para "Limpieza Dental"
POST /api/inventario/treatments/1/recipe
{
  "product_id": 5,  # Pasta profiláctica
  "quantity_needed": 1,
  "notes": "Usar sabor menta"
}

POST /api/inventario/treatments/1/recipe
{
  "product_id": 12,  # Hilo dental
  "quantity_needed": 1
}
```

### Beneficios

- ✅ Descuento automático de stock
- ✅ Prevención de faltantes antes de procedimientos
- ✅ Cálculo preciso de costos por tratamiento
- ✅ Trazabilidad de uso de productos

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/inventario_service
pip install -r ../requirements-base.txt
```

### Variables de Entorno

Usa el mismo `.env` del backend:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db
JWT_SECRET_KEY=tu_clave_secreta
```

### Migrar Base de Datos

```bash
cd backend
alembic upgrade head
```

---

## 💻 Uso

### Ejecutar el Servicio

```bash
cd backend/inventario_service
python app.py
```

El servicio estará disponible en `http://localhost:5002`

### Ejemplo de Creación de Producto

```bash
curl -X POST http://localhost:5002/api/inventario/products \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sku": "MED-001",
    "name": "Paracetamol 500mg",
    "category": "Medicamentos",
    "cost_price": 0.50,
    "sale_price": 1.20,
    "stock_quantity": 250,
    "min_stock_alert": 50,
    "unit": "Tabletas",
    "is_taxable": true
  }'
```

### Ejemplo de Consulta de Stock Bajo

```bash
curl -X GET http://localhost:5002/api/inventario/products/low-stock \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "product_id": 7,
      "name": "Guantes Látex M",
      "stock_quantity": 15,
      "min_stock_alert": 50,
      "status": "LOW_STOCK"
    }
  ]
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_inventario.py -v
```

### Casos de Prueba

- ✅ CRUD de productos
- ✅ Validación de SKU único
- ✅ Control de stock negativo
- ✅ Alertas de stock bajo
- ✅ Creación de tratamientos con recetas
- ✅ Descuento automático de stock al realizar tratamiento
- ✅ Cálculo de precios con IVA

---

## 📊 Categorías Predefinidas

### Productos
- Medicamentos
- Insumos Médicos
- Equipos
- Material Quirúrgico
- Consumibles

### Tratamientos
- Odontología
- Medicina General
- Cirugía Menor
- Diagnóstico
- Prevención

---

## 🔒 Integración con Otros Servicios

### Facturación Service
- Consulta de precios de productos
- Validación de stock disponible
- Descuento de stock al generar factura

### Historia Clínica Service
- Registro de tratamientos realizados
- Historial de productos utilizados

---

## 🐛 Troubleshooting

### Error: "SKU already exists"
- Cada SKU debe ser único en el sistema
- Verifica el SKU antes de crear

### Error: "Insufficient stock"
- El stock no puede ser negativo
- Ajusta el stock con el endpoint `/adjust-stock`

### Alerta: "Low stock"
- Producto bajo el mínimo configurado
- Realizar pedido de reposición

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5002/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Estrategia de Pruebas**: [../../docs/ESTRATEGIA_PRUEBAS.md](../../docs/ESTRATEGIA_PRUEBAS.md)

---

**Última actualización:** 2025-12-17
