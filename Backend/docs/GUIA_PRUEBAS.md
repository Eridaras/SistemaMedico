# Guía de Pruebas - Facturación Electrónica SRI

## 🎯 Objetivo

Esta guía te ayudará a probar el sistema completo de facturación electrónica en el ambiente de pruebas del SRI.

---

## 📋 Requisitos Previos

### 1. Servicios Corriendo
Asegúrate de que todos los servicios estén activos:
```bash
# Auth Service - Puerto 5001
# Facturación Service - Puerto 5004
```

### 2. Usuario Admin
- Username: `admin`
- Password: `admin123`

### 3. Paciente en Base de Datos
Debe existir al menos 1 paciente (patient_id = 1) para asociar la factura.

---

## 🧪 Prueba Automática (Recomendado)

### Ejecutar Script de Prueba

```bash
cd backend
python tests/test_electronic_invoice.py
```

Este script ejecuta automáticamente:
1. ✅ Login y obtención de token
2. ✅ Configuración de datos SRI de prueba
3. ✅ Creación de factura electrónica
4. ✅ Generación de XML
5. ✅ Autorización con SRI (simulada)
6. ✅ Consulta de factura
7. ✅ Estadísticas
8. ✅ Verificación de almacenamiento de XMLs

**Salida esperada:**
```
============================================================
           TEST DE FACTURACIÓN ELECTRÓNICA SRI
============================================================

============================================================
  1. AUTENTICACIÓN
============================================================
✅ Login exitoso
ℹ️  Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

============================================================
  2. CONFIGURACIÓN SRI
============================================================
ℹ️  Configuración actual ID: 1
ℹ️  RUC actual: 9999999999001
ℹ️  Actualizando configuración con datos de prueba...
✅ Configuración actualizada
ℹ️  RUC: 0190329773001
ℹ️  Razón Social: CLINICA DE PRUEBAS S.A.
ℹ️  Ambiente: PRUEBAS

============================================================
  3. CREAR FACTURA ELECTRÓNICA
============================================================
ℹ️  Enviando datos de factura...
ℹ️  Total items: 2
ℹ️  Total: $86.25
✅ Factura creada exitosamente
ℹ️  ID: 1
ℹ️  Número: 001-001-000000001
ℹ️  Clave de acceso: 10122025010190329773001100100100000000011...
ℹ️  Estado SRI: PENDIENTE
ℹ️  Total: $86.25

============================================================
  4. AUTORIZAR CON SRI
============================================================
ℹ️  Enviando factura 1 al SRI...
✅ Factura AUTORIZADA por el SRI
ℹ️  Estado: AUTORIZADA
ℹ️  Número de autorización: 10122025010190329773001...

============================================================
  5. CONSULTAR FACTURA
============================================================
✅ Factura recuperada
ℹ️  Items: 2
ℹ️  Log de autorizaciones: 2

============================================================
  7. VERIFICAR ALMACENAMIENTO DE XML
============================================================
✅ XML encontrado en: backend/storage/xml/2024/12/facturas/001-001-000000001.xml
✅ XML autorizado encontrado en: backend/storage/xml/2024/12/autorizados/001-001-000000001_AUTORIZADO.xml
✅ Backups encontrados: 1
ℹ️  Total de XMLs en storage: 2
```

---

## 🔧 Prueba Manual

Si prefieres probar manualmente, sigue estos pasos:

### Paso 1: Login

```bash
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Guarda el token:**
```bash
TOKEN="tu_token_aqui"
```

### Paso 2: Configurar Datos SRI

```bash
curl -X PUT http://localhost:5004/api/facturacion/sri/config/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ruc": "0190329773001",
    "razon_social": "CLINICA DE PRUEBAS S.A.",
    "nombre_comercial": "Clinica Test",
    "direccion_matriz": "Av. 10 de Agosto N37-185, Quito, Ecuador",
    "email_emisor": "pruebas@clinica.com",
    "telefono_emisor": "023456789",
    "ambiente": "1"
  }'
```

**RUCs de Prueba Válidos SRI:**
- `0190329773001` - Empresa de prueba 1
- `1234567890001` - Empresa de prueba 2

### Paso 3: Crear Factura Electrónica

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
        "valor": "paciente@test.com"
      },
      {
        "nombre": "Médico",
        "valor": "Dr. Juan Pérez"
      }
    ]
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Electronic invoice created successfully",
  "data": {
    "invoice": {
      "invoice_id": 1,
      "invoice_number": "001-001-000000001",
      "clave_acceso": "10122025010190329773001100100100000000011234567891",
      "estado_sri": "PENDIENTE",
      "total_amount": 86.25
    },
    "clave_acceso": "10122025010190329773001100100100000000011234567891",
    "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>..."
  }
}
```

### Paso 4: Autorizar con SRI

```bash
# Reemplaza {invoice_id} con el ID recibido en el paso anterior
curl -X POST http://localhost:5004/api/facturacion/sri/electronic-invoices/1/authorize \
  -H "Authorization: Bearer $TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "message": "Invoice authorized successfully",
  "data": {
    "invoice_id": 1,
    "clave_acceso": "10122025010190329773001100100100000000011234567891",
    "numero_autorizacion": "10122025010190329773001100100100000000011234567891",
    "estado": "AUTORIZADA",
    "mensaje": "Invoice authorized successfully by SRI"
  }
}
```

### Paso 5: Verificar XML Generado

**Ver en sistema de archivos:**
```
backend/storage/xml/2024/12/
├── facturas/
│   └── 001-001-000000001.xml
├── autorizados/
│   └── 001-001-000000001_AUTORIZADO.xml
```

**Descargar XML desde API:**
```bash
curl -X GET http://localhost:5004/api/facturacion/sri/electronic-invoices/1/xml \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📁 Estructura de Almacenamiento

Los XMLs se organizan automáticamente:

```
backend/storage/
├── xml/
│   ├── 2024/
│   │   ├── 12/
│   │   │   ├── facturas/           ← XMLs pendientes/en proceso
│   │   │   │   ├── 001-001-000000001.xml
│   │   │   │   ├── 001-001-000000002.xml
│   │   │   ├── autorizados/        ← XMLs autorizados por SRI
│   │   │   │   ├── 001-001-000000001_AUTORIZADO.xml
│   │   │   ├── rechazados/         ← XMLs rechazados por SRI
│   │   │       ├── 001-001-000000003_ERROR.xml
├── ride/                           ← PDFs (implementación futura)
│   ├── 2024/
│   │   ├── 12/
│   │   │   ├── 001-001-000000001.pdf
├── backup/                         ← Backups con timestamp
    ├── 001-001-000000001_20241210_143052.xml
```

---

## ✅ Verificaciones de Calidad

### 1. Validar Clave de Acceso (49 dígitos)

La clave debe tener exactamente **49 dígitos** y seguir el formato:

```
DD MM YYYY TC RUC           E SSS SSS NNNNNNNNN T M
10 12 2025 01 0190329773001 1 001 001 000000001 1 2
```

**Validación automática:**
- El sistema calcula el dígito verificador (último dígito) usando módulo 11
- Si la clave es inválida, el SRI rechazará la factura

### 2. Validar Totales

```python
# Cálculos que debe hacer el sistema:
Subtotal sin impuestos = Σ (cantidad × precio_unitario - descuento)
IVA 15% = Subtotal IVA 15% × 0.15
Total = Subtotal sin impuestos + IVA

# Ejemplo:
Item 1: 1 × 50.00 - 0 = 50.00
Item 2: 1 × 30.00 - 5.00 = 25.00
Subtotal sin impuestos = 75.00
IVA 15% = 75.00 × 0.15 = 11.25
Total = 75.00 + 11.25 = 86.25 ✅
```

### 3. Validar XML

**Elementos obligatorios en XML:**
- ✅ `<infoTributaria>` con RUC, razón social, clave de acceso
- ✅ `<infoFactura>` con datos del comprador y totales
- ✅ `<detalles>` con al menos 1 ítem
- ✅ `<totalConImpuestos>` con IVA 0% y/o 15%

**Abrir XML y verificar:**
```bash
# Windows
notepad backend/storage/xml/2024/12/facturas/001-001-000000001.xml

# Linux/Mac
cat backend/storage/xml/2024/12/facturas/001-001-000000001.xml
```

---

## 🐛 Solución de Problemas

### Error: "SRI configuration not found"

**Causa:** No existe configuración en la base de datos.

**Solución:**
```bash
# Verificar que existe el registro
curl -X GET http://localhost:5004/api/facturacion/sri/config \
  -H "Authorization: Bearer $TOKEN"

# Si no existe, se creó uno por defecto con el SQL
# Actualízalo con tus datos reales
```

### Error: "patient_id not found"

**Causa:** No existe el paciente en la base de datos.

**Solución:**
```bash
# Crear un paciente de prueba
curl -X POST http://localhost:5002/api/inventario/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "doc_type": "CEDULA",
    "doc_number": "1710123456",
    "email": "juan@test.com",
    "phone": "0987654321",
    "address": "Quito, Ecuador"
  }'
```

### Error: "Invalid clave_acceso"

**Causa:** El RUC configurado no es válido.

**Solución:**
```bash
# Usar un RUC de prueba válido
# RUCs de prueba SRI: 0190329773001, 1234567890001
```

### XML no se guarda

**Causa:** Permisos de escritura en carpeta `storage`.

**Solución:**
```bash
# Crear carpeta manualmente
mkdir -p backend/storage/xml
mkdir -p backend/storage/ride
mkdir -p backend/storage/backup

# En Windows (Git Bash)
mkdir -p backend/storage/xml
```

---

## 📊 Verificar Estadísticas

```bash
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

## 🎯 Checklist de Pruebas

- [ ] Login y obtención de token
- [ ] Configuración de datos SRI de prueba
- [ ] Creación de factura con 1 ítem
- [ ] Creación de factura con múltiples ítems
- [ ] Factura con IVA 0%
- [ ] Factura con IVA 15%
- [ ] Factura con IVA mixto (0% y 15%)
- [ ] Factura con descuentos
- [ ] Generación correcta de clave de acceso
- [ ] XML válido y bien formado
- [ ] Autorización con SRI (simulada)
- [ ] Almacenamiento de XML en filesystem
- [ ] Backups automáticos creados
- [ ] Consulta de factura completa
- [ ] Estadísticas correctas
- [ ] Listado de facturas con filtros
- [ ] Descarga de XML

---

## 📝 Notas Importantes

### Ambiente de Pruebas vs Producción

**Pruebas (ambiente = "1"):**
- URL SRI: https://celcer.sri.gob.ec
- Usar RUCs de prueba
- No requiere certificado digital real
- Autorizaciones son simuladas

**Producción (ambiente = "2"):**
- URL SRI: https://cel.sri.gob.ec
- Usar RUC real de la clínica
- **REQUIERE certificado digital** (.p12)
- Autorizaciones son reales y legales

### Certificado Digital

Para pasar a producción necesitas:
1. Solicitar certificado en Banco Central del Ecuador o Security Data
2. Costo: ~$30-50 USD
3. Validez: 2 años
4. Formato: PKCS#12 (.p12)
5. Guardar en: `backend/certificates/certificado.p12`
6. Configurar ruta y contraseña en `sri_configuration`

---

## 🚀 Próximos Pasos

1. **Pruebas exitosas** → Sistema funcional
2. **Obtener certificado digital** → Para producción
3. **Implementar firma digital** → Firmar XMLs
4. **Implementar RIDE** → PDF con código de barras
5. **Configurar emails** → Envío automático
6. **Cambiar a producción** → ambiente = "2"

---

## 📞 Soporte

**Dudas técnicas:**
- Ver [FACTURACION_ELECTRONICA.md](./FACTURACION_ELECTRONICA.md)
- Ver [QUICK_START_FACTURACION_ELECTRONICA.md](./QUICK_START_FACTURACION_ELECTRONICA.md)

**SRI Ecuador:**
- Teléfono: 1700 774 774
- Web: https://www.sri.gob.ec
- Chat: https://www.sri.gob.ec/chat

---

**Última actualización:** Diciembre 2024
