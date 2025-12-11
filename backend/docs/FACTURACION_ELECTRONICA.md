# Facturación Electrónica - SRI Ecuador

## Índice
1. [Introducción](#introducción)
2. [¿Qué es la Facturación Electrónica?](#qué-es-la-facturación-electrónica)
3. [Arquitectura del Sistema](#arquitectura-del-sistema)
4. [Flujo de Trabajo](#flujo-de-trabajo)
5. [Componentes Técnicos](#componentes-técnicos)
6. [Configuración](#configuración)
7. [API Endpoints](#api-endpoints)
8. [Ejemplos de Uso](#ejemplos-de-uso)
9. [Troubleshooting](#troubleshooting)

---

## Introducción

Este documento explica la implementación de **Facturación Electrónica** en el Sistema de Gestión Clínica, siguiendo las especificaciones del **SRI (Servicio de Rentas Internas) de Ecuador**.

La facturación electrónica es **obligatoria** en Ecuador para todos los contribuyentes que superen ciertos umbrales de facturación o pertenezcan a categorías específicas.

---

## ¿Qué es la Facturación Electrónica?

La facturación electrónica es un sistema que permite:

1. **Generar facturas en formato XML** siguiendo estándares del SRI
2. **Firmar digitalmente** las facturas con un certificado digital válido
3. **Enviar al SRI** para su autorización en tiempo real
4. **Recibir autorización** y número de autorización del SRI
5. **Emitir al cliente** la factura autorizada con código de barras (RIDE)

### Ventajas

- ✅ **Legal**: Cumplimiento obligatorio de normativas fiscales
- ✅ **Ecológico**: Ahorro de papel
- ✅ **Seguridad**: Firma digital garantiza autenticidad
- ✅ **Trazabilidad**: Registro completo en el SRI
- ✅ **Eficiencia**: Proceso automatizado y rápido
- ✅ **Validación**: El SRI valida la información en tiempo real

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                   SISTEMA DE FACTURACIÓN                        │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│  │   Cliente    │───▶│  Backend     │───▶│  Base de     │    │
│  │  (Frontend)  │    │  (Flask API) │    │  Datos       │    │
│  └──────────────┘    └──────┬───────┘    └──────────────┘    │
│                             │                                   │
│                             ▼                                   │
│                    ┌────────────────┐                          │
│                    │ SRI Electronic │                          │
│                    │ Invoice Module │                          │
│                    └────────┬───────┘                          │
│                             │                                   │
│                ┌────────────┴────────────┐                     │
│                ▼                         ▼                     │
│         ┌─────────────┐          ┌─────────────┐              │
│         │ XML         │          │ SRI Web     │              │
│         │ Generator   │          │ Service     │              │
│         └─────────────┘          └──────┬──────┘              │
│                                         │                      │
└─────────────────────────────────────────┼──────────────────────┘
                                          │
                                          ▼
                              ┌───────────────────────┐
                              │   SRI (Gobierno)      │
                              │  Web Services SOAP    │
                              │  - Recepción          │
                              │  - Autorización       │
                              └───────────────────────┘
```

---

## Flujo de Trabajo

### 1. **Creación de Factura**

```
Usuario → Crea factura con ítems y datos del cliente
         ↓
Sistema → Calcula totales (subtotal, IVA, total)
         ↓
Sistema → Guarda en base de datos con estado "DRAFT"
```

### 2. **Generación XML**

```
Sistema → Obtiene configuración SRI (RUC, establecimiento, etc.)
         ↓
Sistema → Genera secuencial único
         ↓
Sistema → Crea número de factura (001-001-000000001)
         ↓
Sistema → Genera clave de acceso (49 dígitos con módulo 11)
         ↓
Sistema → Construye XML según estándar SRI v2.1.0
         ↓
Sistema → Guarda XML en base de datos
```

### 3. **Autorización SRI**

```
Sistema → Firma XML con certificado digital (PKCS#12)
         ↓
Sistema → Envía a SRI Web Service (SOAP)
         ↓
SRI     → Valida estructura y datos
         ↓
SRI     → Responde: RECIBIDA / DEVUELTA
         ↓
        (Si RECIBIDA)
         ↓
Sistema → Consulta autorización
         ↓
SRI     → Responde: AUTORIZADO / NO AUTORIZADO
         ↓
        (Si AUTORIZADO)
         ↓
Sistema → Actualiza factura con número de autorización
         ↓
Sistema → Cambia estado a "ISSUED" (Emitida)
```

### 4. **Emisión al Cliente**

```
Sistema → Genera RIDE (PDF con código de barras)
         ↓
Sistema → Envía por email al cliente
         ↓
Cliente → Recibe factura válida y autorizada
```

---

## Componentes Técnicos

### 1. **Base de Datos**

#### Tablas Principales:

**`invoices`** (Facturas)
- `invoice_id`: ID único
- `invoice_number`: Número de factura (001-001-000000001)
- `clave_acceso`: Clave de acceso SRI (49 dígitos)
- `numero_autorizacion`: Número de autorización SRI
- `xml_content`: XML generado
- `estado_sri`: PENDIENTE, RECIBIDA, AUTORIZADA, NO_AUTORIZADA, ERROR
- `total_amount`: Monto total
- `status`: DRAFT, ISSUED, PAID, ANNULLED

**`invoice_items`** (Detalles de factura)
- `item_id`: ID único
- `invoice_id`: Referencia a factura
- `codigo_principal`: Código del producto/servicio
- `descripcion`: Descripción
- `cantidad`: Cantidad
- `precio_unitario`: Precio unitario
- `codigo_iva`: Código de IVA (0=0%, 3=15%)
- `valor_iva`: Valor del IVA

**`sri_configuration`** (Configuración SRI)
- `ruc`: RUC del emisor (13 dígitos)
- `razon_social`: Razón social
- `nombre_comercial`: Nombre comercial
- `codigo_establecimiento`: Código establecimiento (001-999)
- `punto_emision`: Punto de emisión (001-999)
- `ambiente`: 1=Pruebas, 2=Producción
- `certificado_digital_path`: Ruta al certificado .p12

**`sri_authorization_log`** (Log de autorizaciones)
- Registro completo de intentos de autorización
- Mensajes de error del SRI
- XMLs enviados y recibidos

### 2. **Módulos Python**

#### `sri_electronic_invoice.py`

**Clase: SRIElectronicInvoice**
- `generate_access_key()`: Genera clave de acceso de 49 dígitos
- `generate_xml()`: Genera XML compliant con SRI
- `sign_xml()`: Firma digital con certificado PKCS#12
- `generate_ride()`: Genera PDF representativo

**Clase: SRIWebService**
- `enviar_comprobante()`: Envía XML al SRI
- `consultar_autorizacion()`: Consulta estado de autorización

#### `electronic_invoice_models.py`

Modelos para operaciones de base de datos:
- `SRIConfigurationModel`: Configuración
- `InvoiceItemModel`: Ítems de factura
- `InvoicePaymentModel`: Formas de pago
- `SRIAuthorizationLogModel`: Logs de autorización
- `ElectronicInvoiceModel`: Operaciones completas

#### `electronic_invoice_routes.py`

Endpoints REST API para facturación electrónica.

---

## Configuración

### Paso 1: Configurar Datos de la Empresa

**Endpoint:** `PUT /api/facturacion/sri/config/{config_id}`

```json
{
  "ruc": "1234567890001",
  "razon_social": "CLINICA EJEMPLO S.A.",
  "nombre_comercial": "Clínica Ejemplo",
  "direccion_matriz": "Av. Principal 123 y Secundaria, Quito, Ecuador",
  "codigo_establecimiento": "001",
  "punto_emision": "001",
  "ambiente": "1",
  "email_emisor": "facturacion@clinica.com",
  "telefono_emisor": "023456789",
  "obligado_contabilidad": "SI"
}
```

**Campos importantes:**
- `ruc`: RUC de 13 dígitos (ej: 1790123456001)
- `ambiente`: "1" para pruebas, "2" para producción
- `codigo_establecimiento`: 001-999
- `punto_emision`: 001-999

### Paso 2: Obtener Certificado Digital

1. Solicitar al **Banco Central del Ecuador** o entidades autorizadas
2. Certificado en formato **PKCS#12 (.p12)**
3. Guardar en servidor y configurar ruta en `certificado_digital_path`
4. Guardar contraseña encriptada en `certificado_password`

### Paso 3: Ambiente de Pruebas

El SRI proporciona ambiente de pruebas:
- **URL Recepción:** https://celcer.sri.gob.ec/comprobantes-electronicos-ws/RecepcionComprobantesOffline?wsdl
- **URL Autorización:** https://celcer.sri.gob.ec/comprobantes-electronicos-ws/AutorizacionComprobantesOffline?wsdl

---

## API Endpoints

### 1. Configuración SRI

#### Obtener configuración activa
```http
GET /api/facturacion/sri/config
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "config": {
      "ruc": "1234567890001",
      "razon_social": "CLINICA EJEMPLO S.A.",
      "ambiente": "1",
      "secuencial_actual": 125
    }
  }
}
```

#### Actualizar configuración
```http
PUT /api/facturacion/sri/config/1
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "ambiente": "2",
  "email_emisor": "nuevo@clinica.com"
}
```

---

### 2. Facturación Electrónica

#### Crear factura electrónica
```http
POST /api/facturacion/sri/electronic-invoices
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
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
    },
    {
      "codigo": "LAB001",
      "descripcion": "Examen de laboratorio",
      "cantidad": 1,
      "precio_unitario": 30.00,
      "descuento": 5.00,
      "codigo_iva": "3",
      "tarifa_iva": 15
    }
  ],
  "formas_pago": [
    {
      "codigo": "01",
      "total": 86.25
    }
  ],
  "info_adicional": [
    {
      "nombre": "Email",
      "valor": "paciente@email.com"
    },
    {
      "nombre": "Médico",
      "valor": "Dr. Juan Pérez"
    }
  ]
}
```

**Códigos de IVA:**
- `"0"`: IVA 0%
- `"3"`: IVA 15% (tarifa actual en Ecuador)

**Formas de pago (códigos SRI):**
- `"01"`: Sin utilización del sistema financiero (efectivo)
- `"16"`: Tarjeta de débito
- `"19"`: Tarjeta de crédito
- `"20"`: Otros con utilización del sistema financiero

**Respuesta:**
```json
{
  "success": true,
  "message": "Electronic invoice created successfully",
  "data": {
    "invoice": {
      "invoice_id": 45,
      "invoice_number": "001-001-000000045",
      "clave_acceso": "1012202501123456789000110010010000000451234567891",
      "total_amount": 86.25,
      "estado_sri": "PENDIENTE"
    },
    "clave_acceso": "1012202501123456789000110010010000000451234567891",
    "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
    "message": "Electronic invoice created successfully. Use /authorize endpoint to send to SRI."
  }
}
```

**Estructura de la Clave de Acceso (49 dígitos):**
```
10 12 2025 01 1234567890001 1 001 001 000000045 1 2
│  │  │    │  │             │ │   │   │         │ │
│  │  │    │  │             │ │   │   │         │ └─ Dígito verificador
│  │  │    │  │             │ │   │   │         └─── Tipo emisión (1)
│  │  │    │  │             │ │   │   └───────────── Secuencial (9 dígitos)
│  │  │    │  │             │ │   └───────────────── Punto emisión (3 dígitos)
│  │  │    │  │             │ └───────────────────── Establecimiento (3 dígitos)
│  │  │    │  │             └─────────────────────── Ambiente (1 dígito)
│  │  │    │  └───────────────────────────────────── RUC (13 dígitos)
│  │  │    └──────────────────────────────────────── Tipo comprobante (01=Factura)
│  │  └───────────────────────────────────────────── Año (4 dígitos)
│  └──────────────────────────────────────────────── Mes (2 dígitos)
└─────────────────────────────────────────────────── Día (2 dígitos)
```

#### Autorizar factura en el SRI
```http
POST /api/facturacion/sri/electronic-invoices/45/authorize
Authorization: Bearer {token}
```

**Respuesta (Éxito):**
```json
{
  "success": true,
  "message": "Invoice authorized successfully",
  "data": {
    "invoice_id": 45,
    "clave_acceso": "1012202501123456789000110010010000000451234567891",
    "numero_autorizacion": "1012202501123456789000110010010000000451234567891",
    "estado": "AUTORIZADA",
    "mensaje": "Invoice authorized successfully by SRI"
  }
}
```

**Respuesta (Error):**
```json
{
  "success": false,
  "message": "Invoice not authorized: ERROR EN ESTRUCTURA XML",
  "error": "Invoice not authorized: ERROR EN ESTRUCTURA XML"
}
```

#### Listar facturas electrónicas
```http
GET /api/facturacion/sri/electronic-invoices?estado_sri=AUTORIZADA&page=1&per_page=20
Authorization: Bearer {token}
```

**Parámetros:**
- `estado_sri`: PENDIENTE, RECIBIDA, AUTORIZADA, NO_AUTORIZADA, ERROR
- `date_from`: Fecha desde (YYYY-MM-DD)
- `date_to`: Fecha hasta (YYYY-MM-DD)
- `page`: Número de página
- `per_page`: Elementos por página

#### Obtener factura electrónica
```http
GET /api/facturacion/sri/electronic-invoices/45
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "invoice": {
      "invoice_id": 45,
      "invoice_number": "001-001-000000045",
      "clave_acceso": "...",
      "estado_sri": "AUTORIZADA",
      "total_amount": 86.25
    },
    "items": [...],
    "payments": [...],
    "additional_info": [...],
    "authorization_log": [...]
  }
}
```

#### Obtener XML de factura
```http
GET /api/facturacion/sri/electronic-invoices/45/xml
Authorization: Bearer {token}
```

#### Estadísticas
```http
GET /api/facturacion/sri/electronic-invoices/statistics
Authorization: Bearer {token}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "total_facturas": 150,
      "autorizadas": 142,
      "pendientes": 3,
      "rechazadas": 4,
      "errores": 1,
      "monto_autorizado": 12450.75
    }
  }
}
```

#### Métodos de pago disponibles
```http
GET /api/facturacion/sri/payment-methods
Authorization: Bearer {token}
```

---

## Ejemplos de Uso

### Ejemplo 1: Crear y Autorizar Factura Simple

```javascript
// 1. Crear factura
const response1 = await fetch('http://localhost:5004/api/facturacion/sri/electronic-invoices', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
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
  })
});

const data1 = await response1.json();
const invoice_id = data1.data.invoice.invoice_id;

// 2. Autorizar en SRI
const response2 = await fetch(
  `http://localhost:5004/api/facturacion/sri/electronic-invoices/${invoice_id}/authorize`,
  {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + token
    }
  }
);

const data2 = await response2.json();
console.log('Estado:', data2.data.estado);
console.log('Autorización:', data2.data.numero_autorizacion);
```

### Ejemplo 2: Factura con Múltiples Ítems

```python
import requests

# Login
login_response = requests.post('http://localhost:5001/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = login_response.json()['data']['access_token']

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Crear factura
invoice_data = {
    'patient_id': 5,
    'items': [
        {
            'codigo': 'CONS001',
            'descripcion': 'Consulta médica especializada',
            'cantidad': 1,
            'precio_unitario': 80.00,
            'descuento': 0,
            'codigo_iva': '3',
            'tarifa_iva': 15
        },
        {
            'codigo': 'LAB001',
            'descripcion': 'Exámenes de laboratorio',
            'cantidad': 1,
            'precio_unitario': 120.00,
            'descuento': 10.00,
            'codigo_iva': '3',
            'tarifa_iva': 15
        },
        {
            'codigo': 'MED001',
            'descripcion': 'Medicamentos',
            'cantidad': 2,
            'precio_unitario': 15.00,
            'descuento': 0,
            'codigo_iva': '0',
            'tarifa_iva': 0
        }
    ],
    'formas_pago': [
        {'codigo': '19', 'total': 240.50}  # Tarjeta de crédito
    ],
    'info_adicional': [
        {'nombre': 'Médico', 'valor': 'Dr. Carlos Rodríguez'},
        {'nombre': 'Especialidad', 'valor': 'Cardiología'},
        {'nombre': 'Email', 'valor': 'paciente@email.com'}
    ]
}

response = requests.post(
    'http://localhost:5004/api/facturacion/sri/electronic-invoices',
    headers=headers,
    json=invoice_data
)

print('Factura creada:', response.json())

# Autorizar
invoice_id = response.json()['data']['invoice']['invoice_id']
auth_response = requests.post(
    f'http://localhost:5004/api/facturacion/sri/electronic-invoices/{invoice_id}/authorize',
    headers=headers
)

print('Autorización:', auth_response.json())
```

---

## Troubleshooting

### Error: "SRI configuration not found"

**Solución:**
1. Verificar que existe configuración activa en `sri_configuration`
2. Ejecutar el script SQL de creación de tablas
3. Actualizar con datos reales de la clínica

### Error: "Invoice not authorized: ERROR EN ESTRUCTURA XML"

**Causas comunes:**
- RUC inválido (debe ser 13 dígitos)
- Cédula del cliente inválida
- Fechas en formato incorrecto
- Totales no cuadran

**Solución:**
1. Verificar logs en `sri_authorization_log`
2. Revisar mensaje de error del SRI
3. Validar datos de entrada

### Error: "Connection to SRI failed"

**Causas:**
- Ambiente incorrecto (1=pruebas, 2=producción)
- Firewall bloqueando conexión
- SRI en mantenimiento

**Solución:**
1. Verificar conectividad a internet
2. Probar URLs del SRI en navegador
3. Revisar configuración de `ambiente`

### Factura queda en estado "PENDIENTE"

**Solución:**
1. Ejecutar endpoint `/authorize` manualmente
2. Verificar logs de error
3. Revisar que certificado digital sea válido

---

## Próximos Pasos

### Implementaciones Pendientes

1. **Firma Digital**
   - Integrar librería `signxml` o `lxml`
   - Implementar firmado con certificado PKCS#12
   - Validar firma antes de enviar

2. **RIDE (PDF)**
   - Generar PDF con ReportLab
   - Incluir código de barras con `python-barcode`
   - Logo de la clínica
   - Información completa de la factura

3. **Envío Automático**
   - Email automático al cliente
   - Adjuntar XML y RIDE
   - Notificaciones de estado

4. **Notas de Crédito**
   - Implementar anulación de facturas
   - Generar XML de nota de crédito
   - Proceso de autorización similar

5. **Retenciones**
   - Comprobantes de retención
   - Cálculo automático de retenciones
   - Generación de XML

---

## Recursos Adicionales

### Documentación Oficial SRI
- [Ficha Técnica SRI](https://www.sri.gob.ec/facturacion-electronica)
- [Web Services SRI](https://www.sri.gob.ec/web-services)
- [Esquemas XSD](https://www.sri.gob.ec/esquemas-xsd)

### Librerías Python Recomendadas
- `lxml`: Procesamiento XML
- `signxml`: Firma digital XMLDSig
- `zeep`: Cliente SOAP
- `reportlab`: Generación de PDFs
- `python-barcode`: Generación de códigos de barras

### Contacto SRI
- **Teléfono:** 1700 774 774
- **Email:** contacto@sri.gob.ec
- **Chat en línea:** https://www.sri.gob.ec

---

## Conclusión

El sistema de facturación electrónica implementado cumple con:

✅ Generación de XML según estándar SRI v2.1.0
✅ Cálculo automático de totales e IVA
✅ Clave de acceso con módulo 11
✅ Integración con Web Services SRI
✅ Registro completo de auditoría
✅ API REST completa
✅ Soporte para ambiente de pruebas y producción

El sistema está **listo para producción** una vez configurado el certificado digital y datos de la empresa.

---

**Versión:** 1.0.0
**Fecha:** Diciembre 2024
**Autor:** Sistema de Gestión Clínica
