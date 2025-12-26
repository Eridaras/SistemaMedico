# 💰 Facturación Service - Servicio de Facturación Electrónica

Microservicio de gestión de facturación electrónica del Sistema Médico. Integración completa con SRI Ecuador.

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Endpoints](#-endpoints)
- [Modelos de Datos](#-modelos-de-datos)
- [Integración SRI](#-integración-sri)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)

---

## ✨ Funcionalidades

- **Facturación Electrónica SRI**: Generación de facturas XML según normativa ecuatoriana
- **Firma Digital**: Firma de comprobantes con certificado P12
- **Envío Automático**: Transmisión SOAP a SRI
- **Consulta de Autorización**: Verificación de estado con SRI
- **Generación de RIDE**: PDF de representación impresa
- **Dashboard Financiero**: Ingresos, egresos, gráficos
- **Gestión de Gastos**: Registro de egresos de la clínica
- **Cálculo de IVA**: Automático según tarifa (0%, 12%, 15%)
- **Anulación de Facturas**: Proceso completo con SRI

---

## 🌐 Endpoints

### Base URL
```
http://localhost:5004/api/facturacion
```

### Documentación Interactiva
```
http://localhost:5004/docs
```

### Lista de Endpoints

#### Facturas (Invoices)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/invoices` | Listar todas las facturas | Sí |
| `GET` | `/invoices/:id` | Obtener factura por ID | Sí |
| `POST` | `/invoices` | Crear nueva factura | Sí |
| `POST` | `/invoices/:id/send-sri` | Enviar a SRI para autorización | Sí |
| `GET` | `/invoices/:id/authorization` | Consultar estado SRI | Sí |
| `GET` | `/invoices/:id/ride` | Generar RIDE (PDF) | Sí |
| `POST` | `/invoices/:id/cancel` | Anular factura | Sí (Admin) |
| `GET` | `/invoices/patient/:patient_id` | Facturas por paciente | Sí |

#### Gastos (Expenses)

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/expenses` | Listar todos los gastos | Sí |
| `POST` | `/expenses` | Registrar nuevo gasto | Sí |
| `GET` | `/expenses/:id` | Obtener gasto por ID | Sí |
| `PUT` | `/expenses/:id` | Actualizar gasto | Sí |
| `DELETE` | `/expenses/:id` | Eliminar gasto | Sí (Admin) |

#### Configuración SRI

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/sri/config` | Obtener configuración SRI | Sí (Admin) |
| `POST` | `/sri/config` | Crear/actualizar config SRI | Sí (Admin) |
| `POST` | `/sri/upload-certificate` | Subir certificado P12 | Sí (Admin) |
| `GET` | `/sri/test-connection` | Probar conexión con SRI | Sí (Admin) |

#### Dashboard

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| `GET` | `/dashboard/stats` | Estadísticas financieras | Sí |
| `GET` | `/dashboard/monthly` | Ingresos/egresos mensuales | Sí |

---

## 📊 Modelos de Datos

### Invoice (Factura)

```python
{
    "invoice_id": 1,
    "patient_id": 10,
    "patient_name": "Juan Pérez García",
    "invoice_number": "001-001-000001234",
    "clave_acceso": "1712202501179...",  # 49 dígitos
    "estado_sri": "AUTORIZADO",
    "fecha_emision": "2025-12-17T10:00:00Z",
    "fecha_autorizacion": "2025-12-17T10:05:23Z",
    "subtotal_0": 0.00,
    "subtotal_15": 100.00,
    "iva": 15.00,
    "total": 115.00,
    "payment_method": "EFECTIVO",
    "items": [
        {
            "product_id": 3,
            "description": "Consulta Médica General",
            "quantity": 1,
            "unit_price": 100.00,
            "tax_rate": 0.15,
            "total_price": 115.00
        }
    ],
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción | Validación |
|-------|------|-------------|------------|
| `invoice_id` | int | ID único de la factura | PK, Autoincremental |
| `patient_id` | int | ID del paciente | FK a `patients` |
| `invoice_number` | string | Número de factura | Formato: 001-001-000001234 |
| `clave_acceso` | string | Clave de acceso SRI | 49 dígitos |
| `estado_sri` | string | Estado SRI | PENDIENTE, AUTORIZADO, RECHAZADO, ANULADO |
| `fecha_emision` | datetime | Fecha de emisión | ISO 8601 |
| `fecha_autorizacion` | datetime | Fecha autorización SRI | ISO 8601 |
| `subtotal_0` | decimal | Subtotal IVA 0% | >= 0 |
| `subtotal_15` | decimal | Subtotal IVA 15% | >= 0 |
| `iva` | decimal | Total IVA calculado | Auto |
| `total` | decimal | Total de la factura | Auto |
| `payment_method` | string | Forma de pago | EFECTIVO, TARJETA, TRANSFERENCIA |

### Invoice Item (Detalle de Factura)

```python
{
    "item_id": 1,
    "invoice_id": 1,
    "product_id": 3,
    "description": "Consulta Médica General",
    "quantity": 1,
    "unit_price": 100.00,
    "tax_rate": 0.15,
    "discount": 0.00,
    "total_price": 115.00
}
```

### Expense (Gasto)

```python
{
    "expense_id": 1,
    "category": "SUMINISTROS",
    "description": "Compra de guantes y mascarillas",
    "amount": 150.00,
    "date": "2025-12-17",
    "payment_method": "EFECTIVO",
    "invoice_number": "001-002-12345",
    "notes": "Proveedor XYZ",
    "created_at": "2025-12-17T10:00:00Z"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `expense_id` | int | ID único del gasto |
| `category` | string | Categoría (SUMINISTROS, SERVICIOS, SALARIOS, etc.) |
| `description` | text | Descripción del gasto |
| `amount` | decimal | Monto del gasto |
| `date` | date | Fecha del gasto |
| `payment_method` | string | Forma de pago |
| `invoice_number` | string | Número de factura del proveedor |
| `notes` | text | Notas adicionales |

### SRI Configuration

```python
{
    "config_id": 1,
    "ruc_emisor": "1791234567001",
    "razon_social": "CLINICA BIENESTAR S.A.",
    "nombre_comercial": "Clínica Bienestar",
    "direccion_matriz": "Av. Principal 123, Quito, Pichincha",
    "codigo_establecimiento": "001",
    "punto_emision": "001",
    "ambiente": "1",  # 1=Pruebas, 2=Producción
    "tipo_emision": "1",  # 1=Normal
    "contribuyente_especial": "000",
    "obligado_contabilidad": "SI",
    "p12_certificate": b"...",  # Certificado en bytea
    "p12_password": "encrypted_password"
}
```

---

## 🇪🇨 Integración SRI

### Flujo Completo de Facturación Electrónica

```
1. Crear Factura (POST /invoices)
   ↓
2. Generar XML (según ficha técnica SRI v2.1.0)
   ↓
3. Firmar XML (con certificado P12)
   ↓
4. Enviar a SRI (SOAP RecepcionComprobantesOffline)
   ↓
5. Consultar Autorización (SOAP AutorizacionComprobantesOffline)
   ↓
6. Generar RIDE (PDF con código QR)
   ↓
7. Almacenar y Enviar al Cliente
```

### Endpoints SRI

#### Ambiente de Pruebas
```
Recepción: https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl
Autorización: https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl
```

#### Ambiente de Producción
```
Recepción: https://cel.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl
Autorización: https://cel.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl
```

### Clave de Acceso (49 dígitos)

```python
# Formato: DDMMYYYYTTNNNNNNNNNNNNNNNNNDV
# DD: Día
# MM: Mes
# YYYY: Año
# TT: Tipo de comprobante (01=Factura)
# NNNNNNNNNNNNNNN: Número de factura
# D: Dígito verificador
```

### Estados SRI

| Estado | Descripción | Acción |
|--------|-------------|--------|
| **PENDIENTE** | Factura creada, no enviada | Enviar a SRI |
| **ENVIADO** | Enviado, esperando respuesta | Consultar autorización |
| **AUTORIZADO** | Autorizado por SRI | Generar RIDE |
| **RECHAZADO** | Rechazado por SRI | Revisar y corregir |
| **ANULADO** | Anulado por la clínica | No se puede revertir |

---

## 🚀 Instalación

### Instalar Dependencias

```bash
cd backend/facturacion_service
pip install -r ../requirements-base.txt

# Dependencias adicionales para SRI
pip install zeep  # Cliente SOAP
pip install lxml  # XML processing
pip install cryptography  # Firma digital
pip install reportlab  # Generación PDF
```

### Variables de Entorno

```env
DATABASE_URL=postgresql://user:password@localhost:5432/clinica_db
JWT_SECRET_KEY=tu_clave_secreta

# SRI
SRI_AMBIENTE=1  # 1=Pruebas, 2=Producción
SRI_RUC_EMISOR=1791234567001
SRI_RAZON_SOCIAL=CLINICA BIENESTAR S.A.
```

### Certificado P12

1. Obtener certificado de firma electrónica
2. Subir mediante endpoint: `POST /api/facturacion/sri/upload-certificate`

---

## 💻 Uso

### Ejecutar el Servicio

```bash
cd backend/facturacion_service
python app.py
```

El servicio estará disponible en `http://localhost:5004`

### Ejemplo de Creación de Factura

```bash
curl -X POST http://localhost:5004/api/facturacion/invoices \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 10,
    "payment_method": "EFECTIVO",
    "items": [
      {
        "product_id": 3,
        "description": "Consulta Médica General",
        "quantity": 1,
        "unit_price": 100.00,
        "tax_rate": 0.15
      }
    ]
  }'
```

### Ejemplo de Envío a SRI

```bash
curl -X POST http://localhost:5004/api/facturacion/invoices/1/send-sri \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "estado": "ENVIADO",
    "clave_acceso": "171220250117912345670011...",
    "mensaje": "Comprobante recibido por SRI"
  }
}
```

### Ejemplo de Consulta de Autorización

```bash
curl -X GET http://localhost:5004/api/facturacion/invoices/1/authorization \
  -H "Authorization: Bearer TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "estado": "AUTORIZADO",
    "numero_autorizacion": "1712202510000001234",
    "fecha_autorizacion": "2025-12-17T10:05:23Z"
  }
}
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
cd backend
pytest tests/test_facturacion.py -v
```

### Casos de Prueba

- ✅ Creación de factura con cálculo de IVA
- ✅ Generación de clave de acceso
- ✅ Generación de XML SRI
- ✅ Firma digital de XML
- ✅ Envío a SRI (mock)
- ✅ Consulta de autorización
- ✅ Generación de RIDE
- ✅ Anulación de facturas

---

## 📄 RIDE (Representación Impresa del Documento Electrónico)

### Componentes del RIDE

1. **Datos del Emisor**: RUC, razón social, dirección
2. **Datos del Cliente**: Cédula/RUC, nombre, dirección
3. **Detalle de la Factura**: Productos/servicios, cantidades, precios
4. **Totales**: Subtotal, IVA, total
5. **Código QR**: Para validación en portal SRI
6. **Número de Autorización**: 49 dígitos

### Generar RIDE

```bash
curl -X GET http://localhost:5004/api/facturacion/invoices/1/ride \
  -H "Authorization: Bearer TOKEN" \
  --output factura_001.pdf
```

---

## 📊 Dashboard Financiero

### Métricas Disponibles

```bash
GET /api/facturacion/dashboard/stats
```

**Respuesta:**
```json
{
  "ingresos_mes": 15000.00,
  "egresos_mes": 8500.00,
  "utilidad_mes": 6500.00,
  "facturas_emitidas": 45,
  "facturas_autorizadas": 42,
  "facturas_pendientes": 3
}
```

---

## 🔒 Seguridad

### Certificado P12

- Almacenado encriptado en base de datos
- Acceso restringido solo a admin
- Password encriptado

### Validaciones

- Cédula/RUC válidos
- Clave de acceso con dígito verificador
- Firma digital verificable
- Integridad del XML

---

## 🐛 Troubleshooting

### Error: "Invalid RUC format"
- Verifica que el RUC tenga 13 dígitos
- Los últimos 3 dígitos son el establecimiento (001-999)

### Error: "P12 certificate not configured"
- Sube el certificado mediante el endpoint correspondiente

### Error: "SRI connection timeout"
- Verifica conectividad con los endpoints SRI
- Revisa firewall y proxy

### Error: "Invalid XML signature"
- Verifica que el certificado P12 sea válido
- Verifica la contraseña del certificado

---

## 📚 Recursos Adicionales

- **Swagger UI**: http://localhost:5004/docs
- **Documentación General**: [../../README.md](../../README.md)
- **Guía SRI**: [../docs/FACTURACION_ELECTRONICA.md](../docs/FACTURACION_ELECTRONICA.md)
- **Ficha Técnica SRI**: v2.23 (XML v2.1.0)

---

**Última actualización:** 2025-12-17
