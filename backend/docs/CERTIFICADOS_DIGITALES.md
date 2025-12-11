# Certificados Digitales para Facturación Electrónica SRI

## 🔐 ¿Qué es un Certificado Digital?

Un certificado digital es como tu **"firma electrónica oficial"** para facturas electrónicas. Es **obligatorio** para emitir facturas válidas en producción.

---

## 📋 Requisitos

### Para Obtener el Certificado Necesitas:

1. ✅ **RUC** de la clínica (13 dígitos)
2. ✅ **Cédula** del representante legal
3. ✅ **Registro Único de Contribuyentes** actualizado
4. ✅ **Carta de autorización** (si no es el representante legal quien lo solicita)
5. 💰 **Pago**: $30-50 USD (dependiendo de la entidad)

---

## 🏦 ¿Dónde Obtenerlo?

### Entidades Certificadoras Autorizadas en Ecuador:

#### 1. **Banco Central del Ecuador**
- 🌐 Web: https://www.eci.bce.ec
- 📞 Teléfono: (02) 2570013
- 📧 Email: soporteeci@bce.fin.ec
- 💰 Costo: ~$35 USD
- ⏱️ Tiempo: 2-3 días hábiles

**Proceso:**
1. Ingresar a https://www.eci.bce.ec
2. Registrarse con RUC y datos de la empresa
3. Solicitar certificado de "Firma Electrónica"
4. Cargar documentos requeridos
5. Realizar pago en línea
6. Descargar certificado (.p12)

#### 2. **Security Data**
- 🌐 Web: https://www.securitydata.net.ec
- 📞 Teléfono: 1800-SECURITY (7328748)
- 📧 Email: info@securitydata.net.ec
- 💰 Costo: ~$40 USD
- ⏱️ Tiempo: 1-2 días hábiles

#### 3. **ANF AC Ecuador**
- 🌐 Web: https://www.anf.es/ec
- 📞 Teléfono: (02) 3333888
- 💰 Costo: ~$50 USD
- ⏱️ Tiempo: 2-3 días hábiles

---

## 📝 Documentos Requeridos

### Persona Jurídica (Empresas):

1. **Cédula** del representante legal (escaneada)
2. **RUC** actualizado (escaneado)
3. **Nombramiento** del representante legal (vigente)
4. **Carta de solicitud** (formato de la entidad)
5. **Foto** del representante legal

### Persona Natural:

1. **Cédula** (escaneada)
2. **RUC** actualizado (escaneado)
3. **Foto** del titular

---

## 💾 Formato del Certificado

El certificado que recibirás es un archivo **PKCS#12** con extensión `.p12` o `.pfx`

```
ejemplo: certificado_clinica_2024.p12
```

**Incluye:**
- 🔑 Clave privada (para firmar)
- 📜 Certificado público (para verificar)
- 🔐 Contraseña de protección

---

## 🚀 Instalación del Certificado en el Sistema

### Paso 1: Crear Carpeta de Certificados

```bash
# Windows (Git Bash)
mkdir -p backend/certificates

# Linux/Mac
mkdir -p backend/certificates
```

### Paso 2: Copiar Certificado

```bash
# Copiar tu archivo .p12 a la carpeta
cp /ruta/de/descarga/tu_certificado.p12 backend/certificates/clinica.p12
```

### Paso 3: Configurar en Base de Datos

```sql
-- Actualizar configuración SRI con ruta y contraseña del certificado
UPDATE sri_configuration
SET
  certificado_digital_path = 'backend/certificates/clinica.p12',
  certificado_password = 'TU_CONTRASEÑA_AQUI',
  ambiente = '2'  -- Cambiar a producción
WHERE active = TRUE;
```

**O usando la API:**

```bash
curl -X PUT http://localhost:5004/api/facturacion/sri/config/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "certificado_digital_path": "backend/certificates/clinica.p12",
    "certificado_password": "TU_CONTRASEÑA",
    "ambiente": "2"
  }'
```

---

## ✅ Verificar Certificado

### Usando Python:

```python
from facturacion_service.sri_production import XMLDigitalSigner

# Verificar certificado
signer = XMLDigitalSigner(
    certificate_path='backend/certificates/clinica.p12',
    password='TU_CONTRASEÑA'
)

# Ver información
print(f"Certificado válido: {signer.verify_certificate_validity()}")
```

### Información que Verás:

```
Certificate loaded successfully from backend/certificates/clinica.p12
Certificate subject: CN=CLINICA EJEMPLO S.A., RUC=1234567890001
Certificate issuer: CN=Banco Central del Ecuador
Valid from: 2024-01-15 00:00:00
Valid until: 2026-01-15 23:59:59
```

---

## 🔒 Seguridad del Certificado

### ⚠️ MUY IMPORTANTE:

1. **NUNCA subas el certificado a GitHub**
   ```gitignore
   # Ya está en .gitignore
   backend/certificates/*.p12
   backend/certificates/*.pfx
   ```

2. **Guarda la contraseña de forma segura**
   - Usa variables de entorno
   - Usa un gestor de contraseñas
   - NO la dejes en código fuente

3. **Haz backup del certificado**
   - Guarda una copia en lugar seguro
   - Si lo pierdes, debes solicitar uno nuevo

4. **Protege el archivo**
   ```bash
   # Permisos solo para el dueño
   chmod 600 backend/certificates/clinica.p12
   ```

---

## 📊 Validez del Certificado

**Duración típica:** 2 años

**Renovación:**
- 30 días antes del vencimiento
- Proceso similar a la solicitud inicial
- Costo similar (~$30-50 USD)

**El sistema te avisará:**
```python
# El sistema verifica automáticamente la validez
if not signer.verify_certificate_validity():
    print("⚠️ ALERTA: Certificado vencido o no válido")
    print("Renovar certificado urgentemente")
```

---

## 🧪 Certificado de Prueba

Para **ambiente de pruebas** NO necesitas certificado real:

```python
# En ambiente de pruebas (ambiente = "1")
# El sistema funciona sin certificado
# Las facturas se generan pero no son legales
```

**Para producción SÍ es obligatorio.**

---

## 🔧 Troubleshooting

### Error: "Certificate not loaded"

**Causa:** Ruta o contraseña incorrecta

**Solución:**
```bash
# Verificar que existe el archivo
ls -la backend/certificates/clinica.p12

# Verificar contraseña (probando cargar)
python -c "
from facturacion_service.sri_production import XMLDigitalSigner
signer = XMLDigitalSigner('backend/certificates/clinica.p12', 'TU_CONTRASEÑA')
"
```

### Error: "Certificate is not valid"

**Causa:** Certificado vencido o aún no válido

**Solución:**
- Verificar fechas de validez
- Renovar certificado si venció
- Contactar a la entidad certificadora

### Error: "Invalid password"

**Causa:** Contraseña incorrecta

**Solución:**
- Verificar contraseña (sensible a mayúsculas/minúsculas)
- Si olvidaste la contraseña, solicitar nuevo certificado

---

## 📱 Pasos Después de Instalar el Certificado

### 1. Probar Firma

```bash
# Crear factura de prueba
curl -X POST http://localhost:5004/api/facturacion/sri/electronic-invoices \
  -H "Authorization: Bearer $TOKEN" \
  -d '{...}'

# Verificar que el XML esté firmado
# Debe contener sección <ds:Signature>
```

### 2. Cambiar a Producción

```sql
UPDATE sri_configuration
SET ambiente = '2'  -- PRODUCCIÓN
WHERE active = TRUE;
```

### 3. Probar con SRI Real

```bash
# La primera factura debe pasar por el SRI real
# Si falla, revisar logs en sri_authorization_log
```

---

## 📞 Soporte

**Entidades Certificadoras:**
- Banco Central: (02) 2570013
- Security Data: 1800-SECURITY
- ANF AC: (02) 3333888

**SRI:**
- Teléfono: 1700 774 774
- Web: https://www.sri.gob.ec
- Email: contacto@sri.gob.ec

---

## ✅ Checklist

Antes de pasar a producción:

- [ ] Certificado digital obtenido (.p12)
- [ ] Certificado copiado a `backend/certificates/`
- [ ] Contraseña configurada en base de datos
- [ ] Certificado verificado (fechas válidas)
- [ ] Permisos de archivo configurados (600)
- [ ] Backup del certificado realizado
- [ ] Prueba de firma exitosa
- [ ] Ambiente cambiado a producción (`ambiente = "2"`)
- [ ] Primera factura probada con SRI real
- [ ] Facturas autorizándose correctamente

---

## 🎯 Resumen Rápido

| Concepto | Valor |
|----------|-------|
| **Costo** | $30-50 USD |
| **Tiempo** | 1-3 días |
| **Validez** | 2 años |
| **Formato** | .p12 / .pfx |
| **Obligatorio** | Sí (producción) |
| **Entidades** | BCE, Security Data, ANF |

---

**Última actualización:** Diciembre 2024
