# Guía Rápida - Facturación Electrónica SRI Ecuador

## Inicio Rápido en 5 Pasos

### 1️⃣ Configurar Datos de la Empresa

```bash
# Login como admin
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# Guardar el token que recibas
TOKEN="tu_token_aqui"

# Actualizar configuración SRI
curl -X PUT http://localhost:5004/api/facturacion/sri/config/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ruc": "1234567890001",
    "razon_social": "TU CLINICA S.A.",
    "nombre_comercial": "Tu Clínica",
    "direccion_matriz": "Av. Principal 123, Quito, Ecuador",
    "email_emisor": "facturacion@tuclinica.com",
    "telefono_emisor": "023456789",
    "ambiente": "1"
  }'
```

**Importante:**
- `ruc`: Debe ser tu RUC real de 13 dígitos
- `ambiente`: "1" = Pruebas, "2" = Producción

---

### 2️⃣ Crear Factura Electrónica

```bash
curl -X POST http://localhost:5004/api/facturacion/sri/electronic-invoices \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 1,
    "items": [
      {
        "codigo": "CONS001",
        "descripcion": "Consulta médica general",
        "cantidad": 1,
        "precio_unitario": 50.00,
        "descuento": 0,
        "codigo_iva": "3",
        "tarifa_iva": 15
      }
    ],
    "formas_pago": [
      {
        "codigo": "01",
        "total": 57.50
      }
    ],
    "info_adicional": [
      {
        "nombre": "Email",
        "valor": "paciente@email.com"
      }
    ]
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "invoice": {
      "invoice_id": 1,
      "invoice_number": "001-001-000000001",
      "clave_acceso": "10122025011234567890001...",
      "estado_sri": "PENDIENTE",
      "total_amount": 57.50
    },
    "clave_acceso": "10122025011234567890001...",
    "xml": "<?xml version=\"1.0\"?>..."
  }
}
```

---

### 3️⃣ Autorizar en SRI

```bash
# Usa el invoice_id de la respuesta anterior
curl -X POST http://localhost:5004/api/facturacion/sri/electronic-invoices/1/authorize \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta Exitosa:**
```json
{
  "success": true,
  "message": "Invoice authorized successfully",
  "data": {
    "invoice_id": 1,
    "clave_acceso": "10122025011234567890001...",
    "numero_autorizacion": "10122025011234567890001...",
    "estado": "AUTORIZADA"
  }
}
```

---

### 4️⃣ Consultar Factura

```bash
# Ver factura completa con todos los detalles
curl -X GET http://localhost:5004/api/facturacion/sri/electronic-invoices/1 \
  -H "Authorization: Bearer $TOKEN"

# Obtener solo el XML
curl -X GET http://localhost:5004/api/facturacion/sri/electronic-invoices/1/xml \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5️⃣ Ver Estadísticas

```bash
# Estadísticas generales
curl -X GET http://localhost:5004/api/facturacion/sri/electronic-invoices/statistics \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_facturas": 10,
      "autorizadas": 8,
      "pendientes": 1,
      "rechazadas": 1,
      "errores": 0,
      "monto_autorizado": 1250.75
    }
  }
}
```

---

## Códigos de IVA

| Código | Descripción |
|--------|-------------|
| `"0"`  | IVA 0%      |
| `"3"`  | IVA 15%     |

---

## Formas de Pago SRI

```bash
# Consultar todas las formas de pago disponibles
curl -X GET http://localhost:5004/api/facturacion/sri/payment-methods \
  -H "Authorization: Bearer $TOKEN"
```

**Códigos Comunes:**
| Código | Descripción |
|--------|-------------|
| `"01"` | Efectivo (sin sistema financiero) |
| `"16"` | Tarjeta de débito |
| `"19"` | Tarjeta de crédito |
| `"20"` | Transferencia bancaria |

---

## Estados de Factura

- **PENDIENTE**: Creada pero no enviada al SRI
- **RECIBIDA**: Recibida por el SRI, esperando autorización
- **AUTORIZADA**: Autorizada por el SRI (válida para entregar)
- **NO_AUTORIZADA**: Rechazada por el SRI
- **ERROR**: Error en el proceso

---

## Listar Facturas

```bash
# Todas las facturas electrónicas
curl -X GET "http://localhost:5004/api/facturacion/sri/electronic-invoices?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"

# Solo facturas autorizadas
curl -X GET "http://localhost:5004/api/facturacion/sri/electronic-invoices?estado_sri=AUTORIZADA" \
  -H "Authorization: Bearer $TOKEN"

# Por rango de fechas
curl -X GET "http://localhost:5004/api/facturacion/sri/electronic-invoices?date_from=2024-12-01&date_to=2024-12-31" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Ejemplo Python Completo

```python
import requests
import json

BASE_URL = "http://localhost:5004/api/facturacion/sri"
AUTH_URL = "http://localhost:5001/api/auth"

# 1. Login
response = requests.post(f"{AUTH_URL}/login", json={
    "username": "admin",
    "password": "admin123"
})
token = response.json()['data']['access_token']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# 2. Crear factura
invoice_data = {
    "patient_id": 1,
    "items": [
        {
            "codigo": "CONS001",
            "descripcion": "Consulta médica",
            "cantidad": 1,
            "precio_unitario": 50.00,
            "descuento": 0,
            "codigo_iva": "3",
            "tarifa_iva": 15
        }
    ],
    "formas_pago": [
        {"codigo": "01", "total": 57.50}
    ]
}

response = requests.post(
    f"{BASE_URL}/electronic-invoices",
    headers=headers,
    json=invoice_data
)

result = response.json()
print(f"Factura creada: {result['data']['invoice']['invoice_number']}")
print(f"Clave de acceso: {result['data']['clave_acceso']}")

invoice_id = result['data']['invoice']['invoice_id']

# 3. Autorizar
auth_response = requests.post(
    f"{BASE_URL}/electronic-invoices/{invoice_id}/authorize",
    headers=headers
)

auth_result = auth_response.json()
if auth_result['success']:
    print(f"✅ Factura AUTORIZADA")
    print(f"Número de autorización: {auth_result['data']['numero_autorizacion']}")
else:
    print(f"❌ Error: {auth_result['message']}")

# 4. Consultar factura
invoice = requests.get(
    f"{BASE_URL}/electronic-invoices/{invoice_id}",
    headers=headers
).json()

print(f"\nDetalles de factura:")
print(json.dumps(invoice['data'], indent=2))
```

---

## Ejemplo JavaScript/Node.js

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:5004/api/facturacion/sri';
const AUTH_URL = 'http://localhost:5001/api/auth';

async function createAndAuthorizeInvoice() {
    // 1. Login
    const loginRes = await axios.post(`${AUTH_URL}/login`, {
        username: 'admin',
        password: 'admin123'
    });

    const token = loginRes.data.data.access_token;
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };

    // 2. Crear factura
    const invoiceRes = await axios.post(
        `${BASE_URL}/electronic-invoices`,
        {
            patient_id: 1,
            items: [
                {
                    codigo: 'CONS001',
                    descripcion: 'Consulta médica',
                    cantidad: 1,
                    precio_unitario: 50.00,
                    descuento: 0,
                    codigo_iva: '3',
                    tarifa_iva: 15
                }
            ],
            formas_pago: [
                { codigo: '01', total: 57.50 }
            ]
        },
        { headers }
    );

    const invoice = invoiceRes.data.data.invoice;
    console.log(`Factura creada: ${invoice.invoice_number}`);
    console.log(`Clave de acceso: ${invoiceRes.data.data.clave_acceso}`);

    // 3. Autorizar
    const authRes = await axios.post(
        `${BASE_URL}/electronic-invoices/${invoice.invoice_id}/authorize`,
        {},
        { headers }
    );

    if (authRes.data.success) {
        console.log('✅ Factura AUTORIZADA');
        console.log(`Número: ${authRes.data.data.numero_autorizacion}`);
    } else {
        console.log(`❌ Error: ${authRes.data.message}`);
    }

    // 4. Consultar
    const detailsRes = await axios.get(
        `${BASE_URL}/electronic-invoices/${invoice.invoice_id}`,
        { headers }
    );

    console.log('\nDetalles:', JSON.stringify(detailsRes.data.data, null, 2));
}

createAndAuthorizeInvoice().catch(console.error);
```

---

## Troubleshooting Rápido

### Error: "SRI configuration not found"
```bash
# Verificar que existe configuración
curl -X GET http://localhost:5004/api/facturacion/sri/config \
  -H "Authorization: Bearer $TOKEN"

# Si no existe, crearla con PUT al endpoint /config/1
```

### Error: "Invoice not authorized"
```bash
# Ver logs de autorización
curl -X GET http://localhost:5004/api/facturacion/sri/electronic-invoices/{id} \
  -H "Authorization: Bearer $TOKEN"

# Revisar el campo "authorization_log" para ver errores del SRI
```

### Factura en estado "PENDIENTE"
```bash
# Autorizar manualmente
curl -X POST http://localhost:5004/api/facturacion/sri/electronic-invoices/{id}/authorize \
  -H "Authorization: Bearer $TOKEN"
```

---

## Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/sri/config` | Obtener configuración SRI |
| PUT | `/sri/config/{id}` | Actualizar configuración |
| POST | `/sri/electronic-invoices` | Crear factura electrónica |
| POST | `/sri/electronic-invoices/{id}/authorize` | Autorizar en SRI |
| GET | `/sri/electronic-invoices` | Listar facturas |
| GET | `/sri/electronic-invoices/{id}` | Ver factura completa |
| GET | `/sri/electronic-invoices/{id}/xml` | Obtener XML |
| GET | `/sri/electronic-invoices/statistics` | Estadísticas |
| GET | `/sri/payment-methods` | Métodos de pago SRI |
| GET | `/sri/health` | Health check |

---

## Próximos Pasos

1. **Producción**: Cambiar `ambiente` a `"2"` y obtener certificado digital
2. **RIDE**: Implementar generación de PDF
3. **Email**: Configurar envío automático al cliente
4. **Notas de Crédito**: Para anulaciones

---

## Soporte

- **Documentación Completa**: Ver [FACTURACION_ELECTRONICA.md](./FACTURACION_ELECTRONICA.md)
- **SRI Ecuador**: https://www.sri.gob.ec
- **Teléfono SRI**: 1700 774 774

---

**Versión:** 1.0.0
**Última actualización:** Diciembre 2024
